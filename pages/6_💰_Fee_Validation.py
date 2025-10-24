import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import psycopg2
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Fee Validation", layout="wide")
st.title("Fee Validation, Discrepancy Detection & Anomaly Analysis")

# Database Connection Parameters
NEON_DB_MAIN = {
    "host": "ep-frosty-dawn-ad0cnbjn-pooler.c-2.us-east-1.aws.neon.tech",
    "database": "neondb",
    "user": "neondb_owner",
    "password": "npg_XCO6HPNfw7El",
    "port": 5432,
    "sslmode": "require",
}

NEON_DB_PRICE = {
    "host": "ep-wispy-tooth-a4uiq32x.us-east-1.aws.neon.tech",
    "database": "neondb",
    "user": "neondb_owner",
    "password": "npg_7AlUWE8wkigH",
    "port": 5432,
    "sslmode": "require",
}

# ---------- Data Access ----------
def get_customer_transactions(limit: int | None = 200) -> pd.DataFrame:
    """Fetch customer_transactions from main Neon database (with applied charges)."""
    try:
        with psycopg2.connect(**NEON_DB_MAIN) as conn:
            base = (
                "SELECT transaction_id, customer_id, account_id, transaction_date, created_at, "
                "amount, transaction_type, description, charges AS fee_applied, charge_type, charge_method "
                "FROM customer_transactions ORDER BY created_at DESC"
            )
            if limit is not None:
                base += " LIMIT %s"
                return pd.read_sql(base, conn, params=(limit,))
            return pd.read_sql(base, conn)
    except Exception as e:
        # Fallback to generic transactions if customer_transactions not available
        try:
            with psycopg2.connect(**NEON_DB_MAIN) as conn:
                query = (
                    "SELECT id AS transaction_id, created_at, amount, transaction_type_name AS transaction_type, "
                    "COALESCE(fee_applied, 0) AS fee_applied, description FROM transactions ORDER BY created_at DESC"
                )
                if limit is not None:
                    query += " LIMIT %s"
                    return pd.read_sql(query, conn, params=(limit,))
                return pd.read_sql(query, conn)
        except Exception as e2:
            st.error(f"Error fetching transactions: {e2}")
            return pd.DataFrame()

def get_transaction_types() -> pd.DataFrame:
    """Fetch transaction_types from price DB."""
    try:
        with psycopg2.connect(**NEON_DB_PRICE) as conn:
            return pd.read_sql("SELECT * FROM transaction_types", conn)
    except Exception as e:
        st.warning(f"Could not load transaction_types: {e}")
        return pd.DataFrame()

def get_price_recommendations() -> pd.DataFrame:
    """Fetch price recommendations from price Neon database."""
    try:
        with psycopg2.connect(**NEON_DB_PRICE) as conn:
            return pd.read_sql(
                """
                SELECT transaction_type_id,
                       COALESCE(recommended_min_fee, 0) AS recommended_min_fee,
                       COALESCE(recommended_max_fee, 1e12) AS recommended_max_fee,
                       COALESCE(recommended_flat_fee, 0) AS recommended_flat_fee,
                       COALESCE(recommended_percentage_fee, 0) AS recommended_percentage_fee
                FROM price_recommendations
                """,
                conn,
            )
    except Exception as e:
        st.error(f"Error connecting to price recommendations database: {e}")
        return pd.DataFrame()

def get_core_charges() -> pd.DataFrame:
    """Fetch configured charges table (optional, for reference)."""
    try:
        with psycopg2.connect(**NEON_DB_MAIN) as conn:
            return pd.read_sql("SELECT * FROM charges", conn)
    except Exception:
        return pd.DataFrame()


# ---------- Helpers ----------
def safe_float(x) -> float:
    try:
        if x is None or (isinstance(x, float) and np.isnan(x)):
            return 0.0
        if isinstance(x, (int, float, np.floating)):
            return float(x)
        if isinstance(x, str):
            cleaned = x.replace("$", "").replace(",", "").strip()
            return float(cleaned) if cleaned else 0.0
        return float(x)
    except Exception:
        return 0.0

def compute_expected_fee(amount: float, rec_row: pd.Series) -> float:
    perc = safe_float(rec_row.get("recommended_percentage_fee", 0))
    # If percentage looks like 5 instead of 0.05, convert
    perc = perc / 100.0 if perc > 1 else perc
    flat = safe_float(rec_row.get("recommended_flat_fee", 0))
    min_fee = safe_float(rec_row.get("recommended_min_fee", 0))
    max_fee = safe_float(rec_row.get("recommended_max_fee", 1e12))

    raw = flat + (safe_float(amount) * perc)
    clamped = max(min_fee, min(max_fee, raw))
    return float(clamped)

def robust_mad_score(values: pd.Series) -> pd.Series:
    v = pd.to_numeric(values, errors="coerce").astype(float)
    med = np.nanmedian(v)
    mad = np.nanmedian(np.abs(v - med))
    if mad == 0 or np.isnan(mad):
        return pd.Series([0.0] * len(v), index=v.index)
    return 0.6745 * (v - med) / mad


# ---------- UI Controls ----------
with st.sidebar:
    st.header("Filters & Settings")
    currency = st.selectbox("Currency", ["USD", "ZiG"], index=0)
    exchange_rate = st.number_input("USD→ZiG rate", min_value=0.0001, value=13.5, step=0.1)
    limit = st.slider("Records", min_value=100, max_value=5000, value=1000, step=100)
    severity_threshold = st.slider("Anomaly severity threshold", 0, 100, 80, 1)
    contamination = st.slider("IsolationForest contamination", 0.001, 0.2, 0.03, 0.001)
    enable_autorefresh = st.checkbox("Auto-refresh", value=False)
    refresh_secs = st.number_input("Refresh seconds", min_value=5, value=30)

try:
    from streamlit_autorefresh import st_autorefresh
    if enable_autorefresh:
        st_autorefresh(interval=int(refresh_secs * 1000), key="fees_autorefresh")
except Exception:
    pass


# ---------- Load Data ----------
with st.spinner("Loading data…"):
    tx_df = get_customer_transactions(limit=limit)
    types_df = get_transaction_types()
    rec_df = get_price_recommendations()
    charges_df = get_core_charges()

if tx_df.empty:
    st.info("No transaction data available. Please check database connectivity.")
    st.stop()

# Currency conversion
if currency == "ZiG":
    tx_df["amount_display"] = pd.to_numeric(tx_df["amount"], errors="coerce") * exchange_rate
else:
    tx_df["amount_display"] = pd.to_numeric(tx_df["amount"], errors="coerce")

# ---------- Map to transaction types and recommendations ----------
tx_df["transaction_type_key"] = tx_df.get("transaction_type", pd.Series([None] * len(tx_df)))
if isinstance(tx_df["transaction_type_key"].iloc[0] if len(tx_df) else None, str):
    tx_df["transaction_type_key"] = tx_df["transaction_type_key"].str.strip().str.lower()

if not types_df.empty:
    # Normalize names for join
    name_col = "transaction_type_name" if "transaction_type_name" in types_df.columns else (
        "type_name" if "type_name" in types_df.columns else None
    )
    if name_col is not None:
        types_df["tt_name_key"] = types_df[name_col].astype(str).str.strip().str.lower()
        tx_df = tx_df.merge(
            types_df[["transaction_type_id", name_col, "tt_name_key"]],
            left_on="transaction_type_key",
            right_on="tt_name_key",
            how="left",
        )

if not rec_df.empty and "transaction_type_id" in tx_df.columns:
    tx_df = tx_df.merge(rec_df, on="transaction_type_id", how="left")

# Applied fee column harmonization
if "fee_applied" not in tx_df.columns and "charges" in tx_df.columns:
    tx_df["fee_applied"] = tx_df["charges"]

tx_df["fee_applied"] = tx_df["fee_applied"].apply(safe_float)
tx_df["amount_numeric"] = pd.to_numeric(tx_df["amount"], errors="coerce").fillna(0.0)

# Compute expected fees from recommendations if available
if {"recommended_min_fee", "recommended_max_fee", "recommended_flat_fee", "recommended_percentage_fee"}.issubset(tx_df.columns):
    tx_df["expected_fee"] = tx_df.apply(lambda r: compute_expected_fee(r["amount_numeric"], r), axis=1)
else:
    tx_df["expected_fee"] = 0.0

tx_df["fee_difference"] = tx_df["fee_applied"] - tx_df["expected_fee"]

# Classify discrepancy
tolerance_pct = 0.05  # 5% dynamic tolerance baseline
dynamic_band = np.maximum(0.25, 0.5 * np.abs(tx_df["fee_difference"].median()))

def classify_row(row) -> str:
    expected = safe_float(row.get("expected_fee", 0))
    applied = safe_float(row.get("fee_applied", 0))
    tol = max(tolerance_pct * expected, dynamic_band)
    if applied < expected - tol:
        return "Undercharge"
    if applied > expected + tol:
        return "Overcharge"
    return "Compliant"

tx_df["fee_status_type"] = tx_df.apply(classify_row, axis=1)


# ---------- Sidebar Data Filters (based on loaded data) ----------
with st.sidebar:
    st.header("Data Filters")
    # Type filter
    type_name_col = "transaction_type_name" if "transaction_type_name" in tx_df.columns else (
        "transaction_type" if "transaction_type" in tx_df.columns else None
    )
    selected_types = None
    if type_name_col:
        all_types = sorted(tx_df[type_name_col].dropna().astype(str).unique().tolist())
        selected_types = st.multiselect("Transaction types", options=all_types, default=all_types[: min(20, len(all_types))])
    # Date range filter
    time_col = "created_at" if "created_at" in tx_df.columns else (
        "transaction_date" if "transaction_date" in tx_df.columns else None
    )
    date_range = None
    if time_col:
        tmp_dates = pd.to_datetime(tx_df[time_col], errors="coerce").dropna()
        if not tmp_dates.empty:
            start_default = tmp_dates.min().date()
            end_default = tmp_dates.max().date()
            date_range = st.date_input("Date range", value=(start_default, end_default))
    # Amount range
    amt_min = float(np.nanmin(tx_df["amount_numeric"])) if len(tx_df) else 0.0
    amt_max = float(np.nanmax(tx_df["amount_numeric"])) if len(tx_df) else 0.0
    amount_range = st.slider("Amount range", min_value=float(0.0), max_value=float(max(amt_max, 1.0)), value=(float(amt_min), float(amt_max)))
    # Anomaly only
    only_anomalies = st.checkbox("Show anomalies only", value=False)

# Apply data filters
filtered_df = tx_df.copy()
if type_name_col and selected_types is not None and len(selected_types) > 0:
    filtered_df = filtered_df[filtered_df[type_name_col].astype(str).isin(selected_types)]
if time_col and date_range and isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    filtered_df[time_col] = pd.to_datetime(filtered_df[time_col], errors="coerce")
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[(filtered_df[time_col] >= start_date) & (filtered_df[time_col] <= (end_date + pd.Timedelta(days=1)))]
if amount_range:
    amin, amax = amount_range
    filtered_df = filtered_df[(filtered_df["amount_numeric"] >= amin) & (filtered_df["amount_numeric"] <= amax)]
if only_anomalies:
    filtered_df = filtered_df[filtered_df["is_anomaly"]]


# ---------- Anomaly Detection ----------
features = tx_df[["amount_numeric", "expected_fee", "fee_applied", "fee_difference"]].copy()
features = features.fillna(0.0)
scaler = StandardScaler()
X = scaler.fit_transform(features.values)

iforest = IsolationForest(n_estimators=200, contamination=contamination, random_state=42)
iforest.fit(X)
scores = iforest.decision_function(X)  # higher = more normal

# Normalize to severity 0..100 (higher = more anomalous)
norm = (scores - scores.min()) / (scores.max() - scores.min() + 1e-9)
severity_iforest = (1.0 - norm) * 100.0

mad_scores = robust_mad_score(tx_df["fee_difference"]).abs()
mad_norm = (mad_scores - mad_scores.min()) / (mad_scores.max() - mad_scores.min() + 1e-9)
severity_mad = mad_norm * 100.0

tx_df["anomaly_severity"] = 0.6 * severity_iforest + 0.4 * severity_mad
tx_df["is_anomaly"] = tx_df["anomaly_severity"] >= severity_threshold


# ---------- KPIs ----------
total = len(filtered_df)
status_counts = filtered_df["fee_status_type"].value_counts()
under = int(status_counts.get("Undercharge", 0))
over = int(status_counts.get("Overcharge", 0))
comp = int(status_counts.get("Compliant", 0))
anoms = int(filtered_df["is_anomaly"].sum())

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total Transactions", f"{total:,}")
with col2:
    st.metric("Compliant", comp)
with col3:
    st.metric("Undercharges", under)
with col4:
    st.metric("Overcharges", over)
with col5:
    st.metric("Anomalies", anoms)


# ---------- Visuals ----------
tabs = st.tabs(["Overview", "By Type", "Time", "Scatter", "Table", "Queue"]) 

with tabs[0]:
    # Pie of fee status
    if not status_counts.empty:
        fig = px.pie(
            names=status_counts.index,
            values=status_counts.values,
            title="Fee Compliance Status",
            color=status_counts.index,
            color_discrete_map={
                "Compliant": "#16a34a",
                "Undercharge": "#f59e0b",
                "Overcharge": "#ef4444",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    # Severity distribution
    figsev = px.histogram(
        filtered_df,
        x="anomaly_severity",
        nbins=30,
        color=filtered_df["is_anomaly"].map({True: "Anomaly", False: "Normal"}),
        title="Anomaly Severity Distribution",
    )
    st.plotly_chart(figsev, use_container_width=True)

with tabs[1]:
    # Group by transaction type name if available
    if type_name_col:
        agg = (
            filtered_df.groupby([type_name_col, "fee_status_type"]).size().reset_index(name="count")
        )
        if not agg.empty:
            fig2 = px.bar(
                agg, x=type_name_col, y="count", color="fee_status_type", barmode="stack",
                title="Fee Status by Transaction Type",
            )
            fig2.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)
        # Average difference by type
        diff_by_type = (
            filtered_df.groupby(type_name_col)["fee_difference"].mean().reset_index()
        )
        if not diff_by_type.empty:
            st.plotly_chart(
                px.bar(
                    diff_by_type, x=type_name_col, y="fee_difference",
                    title="Average Fee Difference by Type",
                ),
                use_container_width=True,
            )
    else:
        st.info("No transaction type name available to group by.")

with tabs[2]:
    # Time series of average difference
    if time_col:
        tmp = filtered_df.copy()
        tmp[time_col] = pd.to_datetime(tmp[time_col], errors="coerce")
        time_agg = (
            tmp.dropna(subset=[time_col])
               .groupby(pd.Grouper(key=time_col, freq="D"))["fee_difference"].mean()
               .reset_index()
        )
        st.plotly_chart(
            px.line(time_agg, x=time_col, y="fee_difference", title="Daily Average Fee Difference"),
            use_container_width=True,
        )
    else:
        st.info("No timestamp column available for time-series analysis.")

with tabs[3]:
    # Scatter amount vs difference colored by anomalies
    st.plotly_chart(
        px.scatter(
            filtered_df,
            x="amount_numeric",
            y="fee_difference",
            color=filtered_df["is_anomaly"].map({True: "Anomaly", False: "Normal"}),
            size=filtered_df["anomaly_severity"].clip(0, 100),
            hover_data=[
                "transaction_id",
                "transaction_type_name" if "transaction_type_name" in filtered_df.columns else "transaction_type",
                "expected_fee",
                "fee_applied",
                "anomaly_severity",
            ],
            title="Amount vs Fee Difference (Bubble size = severity)",
        ),
        use_container_width=True,
    )

with tabs[4]:
    # Build display table
    display_cols = [
        c for c in [
            "transaction_id",
            "created_at" if "created_at" in filtered_df.columns else None,
            "transaction_type_name" if "transaction_type_name" in filtered_df.columns else (
                "transaction_type" if "transaction_type" in filtered_df.columns else None
            ),
            "amount",
            "expected_fee",
            "fee_applied",
            "fee_difference",
            "fee_status_type",
            "anomaly_severity",
        ]
        if c is not None and c in filtered_df.columns
    ]

    if display_cols:
        df_show = filtered_df[display_cols].copy()
        for col in ["amount", "expected_fee", "fee_applied", "fee_difference"]:
            if col in df_show.columns:
                df_show[col] = pd.to_numeric(df_show[col], errors="coerce").round(2)
        st.dataframe(df_show, use_container_width=True, height=420)

        csv = df_show.to_csv(index=False)
        st.download_button("Download CSV", data=csv, file_name="fee_discrepancy_analysis.csv", mime="text/csv")
    else:
        st.warning("No columns available for display.")

with tabs[5]:
    st.subheader("Auto‑prioritized Investigation Queue")
    queue_df = filtered_df.sort_values("anomaly_severity", ascending=False).head(200)
    q_cols = [
        c for c in [
            "transaction_id",
            "created_at" if "created_at" in queue_df.columns else None,
            "transaction_type_name" if "transaction_type_name" in queue_df.columns else (
                "transaction_type" if "transaction_type" in queue_df.columns else None
            ),
            "amount",
            "expected_fee",
            "fee_applied",
            "fee_difference",
            "fee_status_type",
            "anomaly_severity",
        ]
        if c is not None and c in queue_df.columns
    ]
    if q_cols:
        show_q = queue_df[q_cols].copy()
        for col in ["amount", "expected_fee", "fee_applied", "fee_difference"]:
            if col in show_q.columns:
                show_q[col] = pd.to_numeric(show_q[col], errors="coerce").round(2)
        st.dataframe(show_q, use_container_width=True, height=420)
    else:
        st.info("No data available for queue.")


# ---------- Reference Data Expanders ----------
with st.expander("Reference Data"):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Configured Charges (Core)")
        if not charges_df.empty:
            st.dataframe(charges_df, use_container_width=True)
        else:
            st.info("No charges table available.")
    with c2:
        st.subheader("Price Recommendations")
        if not rec_df.empty:
            st.dataframe(rec_df, use_container_width=True)
        else:
            st.info("No price recommendations available.")