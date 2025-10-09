import plotly.express as px

def plot_anomalies(df):
    fig = px.scatter(
        df,
        x="hour_of_day",
        y="amount",
        color="anomaly",
        title="Transaction Amount vs Hour of Day",
        hover_data=["transaction_type_id"]
    )
    return fig

def plot_fee_validation(df):
    fig = px.bar(
        df,
        x="transaction_type_id",
        color="status",
        title="Fee Validation Results"
    )
    return fig
