import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI
import json
import numpy as np

# Page configuration
st.set_page_config(
    page_title="AI Revenue Intelligence",
    page_icon="",
    layout="wide"
)

def main():
    st.title(" AI-Assisted Revenue Categorization")

    # --- Enter API Key directly here ---
    OPENAI_API_KEY = "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"
    client = OpenAI(api_key=OPENAI_API_KEY)

    # --- Fetch Transactions from dummydb ---
    try:
        conn1 = psycopg2.connect(
            host="localhost",
            database="dummydb",
            user="dummydata",
            password="Test123",
            port=5433
        )
        transactions = pd.read_sql(
            "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 200", conn1
        )
        conn1.close()
    except Exception as e:
        st.error(f"❌ Error connecting to transactions database: {e}")
        transactions = pd.DataFrame()

    # --- Fetch Mapping Tables from Neon ---
    try:
        conn2 = psycopg2.connect(
            host="ep-wispy-tooth-a4uiq32x.us-east-1.aws.neon.tech",
            database="neondb",
            user="neondb_owner",
            password="npg_7AlUWE8wkigH",
            port=5432
        )
        cur2 = conn2.cursor()

        cur2.execute("SELECT * FROM transaction_categories")
        categories = pd.DataFrame(cur2.fetchall(), columns=[desc[0] for desc in cur2.description])

        cur2.execute("SELECT * FROM transaction_subcategories")
        subcategories = pd.DataFrame(cur2.fetchall(), columns=[desc[0] for desc in cur2.description])

        cur2.execute("SELECT * FROM transaction_types")
        types = pd.DataFrame(cur2.fetchall(), columns=[desc[0] for desc in cur2.description])

        cur2.close()
        conn2.close()
    except Exception as e:
        st.error(f"❌ Error connecting to mapping database: {e}")
        categories = pd.DataFrame()
        subcategories = pd.DataFrame()
        types = pd.DataFrame()

    if transactions.empty:
        st.error(" No transaction data available. Please check your database connections.")
        return

    if categories.empty or types.empty:
        st.error(" No mapping data available. Please check your database connections.")
        return

    # --- Merge Mappings ---
    types = types.merge(categories, on="category_id", how="left")
    merged = transactions.merge(types, on="transaction_type_id", how="left")

    # --- Find Unmapped Transactions ---
    unmapped = merged[merged["category_name"].isnull()]

    # Create tabs for better organization
    tab1, tab2, tab3 = st.tabs(["Categorization", " Analytics", " Revenue Insights"])

    with tab1:
        st.subheader("Unmapped Transactions")
        if unmapped.empty:
            st.success("All transactions are mapped! ✅")
        else:
            st.warning(f"{len(unmapped)} transactions need mapping")

            # --- AI Suggestion Function ---
            def suggest_category_ai(name: str):
                prompt = f"""
                Categorize the following financial transaction into Category and Subcategory:

                Transaction: "{name}"

                Respond ONLY in valid JSON:
                {{
                "category": "...",
                "subcategory": "..."
                }}
                """
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a financial categorization assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=100
                    )
                    content = response.choices[0].message.content
                    data = json.loads(content)
                    return data.get("category", "Other"), data.get("subcategory", "Uncategorized")
                except Exception as e:
                    return "Other", "Uncategorized"

            # Apply AI categorization
            with st.spinner(" Generating AI suggestions..."):
                suggestions = []
                for idx, row in unmapped.iterrows():
                    category, subcategory = suggest_category_ai(row["transaction_type_name"])
                    suggestions.append({
                        'id': row['id'],
                        'transaction_type_name': row['transaction_type_name'],
                        'suggested_category': category,
                        'suggested_subcategory': subcategory
                    })
                
                suggestions_df = pd.DataFrame(suggestions)

            st.dataframe(suggestions_df)

            # --- Manual Override Form ---
            st.subheader(" Manual Mapping")
            with st.form("mapping_form"):
                selected_id = st.selectbox("Pick a transaction to map", unmapped["id"])
                selected_cat = st.selectbox("Category", categories["category_name"].unique())

                # Get category_id
                cat_id = categories[categories["category_name"] == selected_cat]["category_id"].iloc[0]
                sub_options = subcategories[subcategories["category_id"] == cat_id]

                selected_sub = st.selectbox("Subcategory", sub_options["subcategory_name"].unique())

                if st.form_submit_button("✅ Approve Mapping"):
                    sub_id = sub_options[sub_options["subcategory_name"] == selected_sub]["subcategory_id"].iloc[0]

                    # Update mapping in Neon (not dummydb)
                    try:
                        conn2 = psycopg2.connect(
                            host="ep-wispy-tooth-a4uiq32x.us-east-1.aws.neon.tech",
                            database="neondb",
                            user="neondb_owner",
                            password="npg_7AlUWE8wkigH",
                            port=5432
                        )
                        cur2 = conn2.cursor()
                        cur2.execute("""
                            UPDATE transaction_types 
                            SET category_id = %s, subcategory_id = %s
                            WHERE transaction_type_id = (
                                SELECT transaction_type_id FROM transactions WHERE id = %s
                            )
                        """, (cat_id, sub_id, selected_id))
                        conn2.commit()
                        cur2.close()
                        conn2.close()

                        st.success(f"Transaction {selected_id} mapped to {selected_cat} → {selected_sub}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating mapping: {e}")

    with tab2:
        # --- Revenue Analytics ---
        st.subheader(" Revenue Analytics")

        if "amount" in merged.columns:
            # Currency selection
            currency = st.selectbox("Display Currency", ["USD", "ZiG"])
            exchange_rate = 13.5 if currency == "ZiG" else 1.0
            
            # Convert amount based on currency - SAFELY
            merged['amount_numeric'] = pd.to_numeric(merged["amount"], errors='coerce')
            merged['amount_converted'] = merged['amount_numeric'] * exchange_rate

            # Filter out null categories and invalid amounts
            valid_data = merged[merged["category_name"].notna() & merged['amount_converted'].notna()]
            
            if not valid_data.empty:
                # Basic metrics
                total_revenue = valid_data['amount_converted'].sum()
                total_transactions = len(valid_data)
                avg_transaction = valid_data['amount_converted'].mean()
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Revenue", f"${total_revenue:,.2f}")
                with col2:
                    st.metric("Total Transactions", f"{total_transactions:,}")
                with col3:
                    st.metric("Avg Transaction", f"${avg_transaction:.2f}")

                # Revenue by category
                revenue_summary = valid_data.groupby("category_name")['amount_converted'].sum().reset_index().sort_values('amount_converted', ascending=False)

                # Create two columns for charts
                col1, col2 = st.columns(2)
                
                with col1:
                    # Pie chart
                    st.write("**Revenue Distribution**")
                    fig1, ax1 = plt.subplots(figsize=(8, 6))
                    ax1.pie(revenue_summary['amount_converted'], labels=revenue_summary["category_name"], autopct="%1.1f%%")
                    ax1.axis("equal")
                    st.pyplot(fig1)

                with col2:
                    # Bar chart
                    st.write("**Revenue by Category**")
                    fig2, ax2 = plt.subplots(figsize=(10, 6))
                    bars = ax2.bar(revenue_summary["category_name"], revenue_summary['amount_converted'])
                    ax2.set_xticks(range(len(revenue_summary["category_name"])))
                    ax2.set_xticklabels(revenue_summary["category_name"], rotation=45, ha="right")
                    ax2.set_ylabel(f"Revenue ({currency})")
                    
                    # Add value labels on bars
                    for bar in bars:
                        height = bar.get_height()
                        ax2.text(bar.get_x() + bar.get_width()/2., height,
                                f'${height:,.0f}',
                                ha='center', va='bottom')
                    
                    st.pyplot(fig2)

                # Trend chart
                if "created_at" in merged.columns:
                    st.write("**Revenue Trends Over Time**")
                    merged["created_at"] = pd.to_datetime(merged["created_at"], errors="coerce")
                    valid_trend_data = merged[merged["created_at"].notna() & merged["category_name"].notna() & merged['amount_converted'].notna()]
                    
                    if not valid_trend_data.empty:
                        # Daily trend
                        daily_revenue = valid_trend_data.groupby(valid_trend_data["created_at"].dt.date)['amount_converted'].sum().reset_index()
                        
                        fig3, ax3 = plt.subplots(figsize=(12, 6))
                        ax3.plot(daily_revenue["created_at"], daily_revenue['amount_converted'], 
                                marker="o", color='green', linewidth=2, markersize=4)
                        ax3.set_ylabel(f"Revenue ({currency})")
                        ax3.set_xlabel("Date")
                        ax3.set_title("Daily Revenue Trend")
                        ax3.grid(True, alpha=0.3)
                        plt.xticks(rotation=45)
                        plt.tight_layout()
                        st.pyplot(fig3)
            else:
                st.info("No valid data available for revenue analysis.")
        else:
            st.warning("No amount column found in transaction data.")

    with tab3:
        # --- Revenue Insights ---
        st.subheader(" Revenue Insights")

        def generate_revenue_insights(merged_df):
            """Generate insights from available transaction data"""
            if merged_df.empty:
                return None
            
            insights_data = {}
            
            # Safely convert amount to numeric
            merged_df['amount_numeric'] = pd.to_numeric(merged_df['amount'], errors='coerce')
            
            # Basic metrics
            valid_data = merged_df[merged_df['amount_numeric'].notna()]
            insights_data['total_revenue'] = valid_data['amount_numeric'].sum()
            insights_data['total_transactions'] = len(valid_data)
            insights_data['avg_transaction'] = valid_data['amount_numeric'].mean()
            
            # Category insights
            if 'category_name' in merged_df.columns:
                valid_cat_data = merged_df[merged_df['category_name'].notna() & merged_df['amount_numeric'].notna()]
                if not valid_cat_data.empty:
                    category_stats = valid_cat_data.groupby('category_name').agg({
                        'amount_numeric': ['sum', 'count', 'mean']
                    }).round(2)
                    
                    # Flatten column names
                    category_stats.columns = ['revenue', 'count', 'avg_amount']
                    insights_data['category_stats'] = category_stats.sort_values('revenue', ascending=False)
            
            # Time-based insights
            if 'created_at' in merged_df.columns:
                merged_df['created_at'] = pd.to_datetime(merged_df['created_at'], errors='coerce')
                valid_time_data = merged_df[merged_df['created_at'].notna() & merged_df['amount_numeric'].notna()]
                if not valid_time_data.empty:
                    # Monthly trends
                    valid_time_data['month'] = valid_time_data['created_at'].dt.to_period('M')
                    monthly_revenue = valid_time_data.groupby('month')['amount_numeric'].sum()
                    insights_data['monthly_revenue'] = monthly_revenue
                    
                    # Growth calculation
                    if len(monthly_revenue) > 1:
                        monthly_growth = monthly_revenue.pct_change().iloc[-1] * 100
                        insights_data['latest_growth'] = monthly_growth
            
            return insights_data

        # Generate insights
        insights_data = generate_revenue_insights(merged)

        if insights_data:
            # Key Metrics
            st.write("###  Performance Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Revenue", f"${insights_data['total_revenue']:,.2f}")
            
            with col2:
                st.metric("Total Transactions", f"{insights_data['total_transactions']:,}")
            
            with col3:
                st.metric("Avg Transaction", f"${insights_data['avg_transaction']:.2f}")
            
            with col4:
                if 'latest_growth' in insights_data:
                    growth_value = insights_data['latest_growth']
                    if not pd.isna(growth_value):
                        st.metric("Monthly Growth", f"{growth_value:.1f}%")
                else:
                    st.metric("Data Period", "Single Month")

            # Category Performance
            st.write("###  Category Performance")
            if 'category_stats' in insights_data:
                category_stats = insights_data['category_stats']
                
                # Display top categories
                st.dataframe(category_stats.head(10), use_container_width=True)
                
                # Visualize category performance
                col1, col2 = st.columns(2)
                
                with col1:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    top_categories = category_stats.head(8)
                    bars = ax.bar(top_categories.index, top_categories['revenue'])
                    ax.set_title("Top Revenue Categories")
                    ax.set_ylabel("Revenue ($)")
                    ax.tick_params(axis='x', rotation=45)
                    
                    # Add value labels
                    for bar in bars:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'${height:,.0f}', ha='center', va='bottom')
                    
                    st.pyplot(fig)
                
                with col2:
                    # Transaction count by category
                    fig, ax = plt.subplots(figsize=(10, 6))
                    top_categories = category_stats.head(8)
                    bars = ax.bar(top_categories.index, top_categories['count'])
                    ax.set_title("Transaction Count by Category")
                    ax.set_ylabel("Number of Transactions")
                    ax.tick_params(axis='x', rotation=45)
                    
                    # Add value labels
                    for bar in bars:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{height:.0f}', ha='center', va='bottom')
                    
                    st.pyplot(fig)

            # Monthly Trends
            st.write("###  Monthly Trends")
            if 'monthly_revenue' in insights_data:
                monthly_data = insights_data['monthly_revenue']
                
                fig, ax = plt.subplots(figsize=(12, 6))
                monthly_data.plot(kind='bar', ax=ax, color='skyblue')
                ax.set_title("Monthly Revenue Trend")
                ax.set_ylabel("Revenue ($)")
                ax.set_xlabel("Month")
                ax.tick_params(axis='x', rotation=45)
                
                # Add value labels on bars
                for i, v in enumerate(monthly_data):
                    ax.text(i, v, f'${v:,.0f}', ha='center', va='bottom')
                
                st.pyplot(fig)

            # AI-Powered Insights
            st.write("### AI Insights")
            
            # Generate simple insights based on data
            insights = []
            
            # Revenue concentration insight
            if 'category_stats' in insights_data:
                top_category_revenue = insights_data['category_stats']['revenue'].iloc[0] if len(insights_data['category_stats']) > 0 else 0
                revenue_share = (top_category_revenue / insights_data['total_revenue']) * 100 if insights_data['total_revenue'] > 0 else 0
                
                if revenue_share > 50:
                    top_cat_name = insights_data['category_stats'].index[0]
                    insights.append(f"**Revenue Concentration**: {top_cat_name} accounts for {revenue_share:.1f}% of total revenue")
                elif revenue_share < 20:
                    insights.append(" **Diversified Revenue**: Revenue is well distributed across categories")
            
            # Transaction size insight
            avg_tx = insights_data['avg_transaction']
            if avg_tx < 50:
                insights.append(" **Small Transactions**: Average transaction size is low - consider upselling strategies")
            elif avg_tx > 200:
                insights.append(" **Large Transactions**: High average transaction value - focus on retention")
            
            # Growth insight
            if 'latest_growth' in insights_data:
                growth = insights_data['latest_growth']
                if not pd.isna(growth):
                    if growth > 10:
                        insights.append(f" **Strong Growth**: Monthly revenue growing at {growth:.1f}%")
                    elif growth < 0:
                        insights.append(f"**Declining Revenue**: Monthly revenue down by {abs(growth):.1f}%")
            
            # Display insights
            if insights:
                for insight in insights:
                    st.info(insight)
            else:
                st.info(" Analyze more data to generate detailed insights")
                
        else:
            st.info("No transaction data available for insights generation.")

if __name__ == "__main__":
    main()