from dash import Dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
import numpy as np
from sklearn.ensemble import IsolationForest
from flask import Flask

# Create a Flask app
server = Flask(__name__)

# Create a Dash app
app = Dash(__name__, server=server)

# Create a SQLAlchemy engine
engine = create_engine('postgresql://bankuser:Test123@localhost:5433/zimbabwe_banks')
engine2 = create_engine('postgresql://bankuser:Test123@localhost:5433/core_banking_system')

# Function to validate data
def validate_data(df):
    # Check for missing values
    if df.isnull().values.any():
        print("Missing values detected. Filling with mean/median values...")
        df = df.fillna(df.mean(numeric_only=True))
    
    # Validate data types
    expected_dtypes = {
        "charge_type": "object",
        "charge_amount": "float64",
        "charge_percentage": "float64"
    }
    for col, dtype in expected_dtypes.items():
        if col in df.columns and df[col].dtype != dtype:
            print(f"Invalid data type for column {col}. Converting to {dtype}...")
            df[col] = df[col].astype(dtype)
    
    return df

# Function to update data
def update_data():
    global mean_charges, mean_values, mean_charge_amounts, mean_charge_percentages, charges
    
    # Calculate the mean charge amount and mean charge percentage per transaction type
    mean_charges = pd.read_sql_query("SELECT * FROM charges", engine)
    mean_charges = validate_data(mean_charges)
    mean_values = mean_charges.groupby("charge_type").agg({
        "charge_amount": "mean",
        "charge_percentage": "mean"
    }).to_dict()

    # Store the same mean values in separate dictionaries
    mean_charge_amounts = mean_values["charge_amount"]
    mean_charge_percentages = mean_values["charge_percentage"]

    # Read the charges table from the second database
    charges = pd.read_sql_query("SELECT * FROM charges", engine2)
    charges = validate_data(charges)

    # Add new charge types to mean dictionaries
    for charge_type in charges["charge_type"].unique():
        if charge_type not in mean_charge_amounts:
            mean_charge_amounts[charge_type] = charges.loc[charges["charge_type"] == charge_type, "charge_amount"].mean()
        if charge_type not in mean_charge_percentages:
            mean_charge_percentages[charge_type] = charges.loc[charges["charge_type"] == charge_type, "charge_percentage"].mean()

    # Compare charges
    charges["charge_amount_flag"] = np.where(charges["charge_amount"] < charges["charge_type"].map(mean_charge_amounts), "below", 
                                            np.where(charges["charge_amount"] == charges["charge_type"].map(mean_charge_amounts), "same", "above"))

    charges["charge_percentage_flag"] = np.where(charges["charge_percentage"] < charges["charge_type"].map(mean_charge_percentages), "below", 
                                                np.where(charges["charge_percentage"] == charges["charge_type"].map(mean_charge_percentages), "same", "above"))

    # Anomaly detection using Isolation Forest
    iforest = IsolationForest(contamination=0.01, random_state=42)
    iforest.fit(charges[["charge_amount", "charge_percentage"]])
    anomaly_scores = iforest.decision_function(charges[["charge_amount", "charge_percentage"]])
    anomaly_predictions = iforest.predict(charges[["charge_amount", "charge_percentage"]])

    # Add anomaly predictions to the charges dataframe
    charges["anomaly"] = np.where(anomaly_predictions == -1, "Anomaly", "Normal")

    return charges

charges = update_data()

# Define the layout
app.layout = html.Div([
    # Comparison Section
    html.Div([
        html.H2("Comparison of Charge Amounts and Percentages", style={"textAlign": "center"}),
        html.P("This section compares the charge amounts and percentages with the mean values calculated from the first database.", style={"textAlign": "center"}),
        html.Div([
            dcc.Graph(id="charge-amount-pie", figure=px.pie(charges, names="charge_amount_flag", title="Charge Amount Comparison")),
            dcc.Graph(id="charge-percentage-pie", figure=px.pie(charges, names="charge_percentage_flag", title="Charge Percentage Comparison"))
        ], style={"display": "flex", "justify-content": "space-around"})
    ], style={"margin-bottom": "50px"}),

    # Anomaly Detection Section
html.Div([
    html.H2("Anomaly Detection", style={"textAlign": "center"}),
    html.P("This section detects anomalies in the charge amounts and percentages using Isolation Forest.", style={"textAlign": "center"}),
    html.Div([
        dcc.Graph(id="charge-amount-line", figure=px.line(charges, x="charge_type", y="charge_amount", color="anomaly", title="Charge Amount Line Plot")),
        dcc.Graph(id="charge-percentage-line", figure=px.line(charges, x="charge_type", y="charge_percentage", color="anomaly", title="Charge Percentage Line Plot"))
    ], style={"display": "flex", "justify-content": "space-around"})
], style={"margin-bottom": "50px"}),

# Table Section
html.Div([
    html.H2("Charge Amount and Percentage Table", style={"textAlign": "center"}),
    html.P("This table shows the charge amounts and percentages with their corresponding flags and anomaly predictions.", style={"textAlign": "center"}),
    html.Div([
        html.Table([
            html.Thead([
                html.Tr([html.Th(col) for col in charges.columns])
            ]),
            html.Tbody([
                html.Tr([html.Td(charges.iloc[i][col]) for col in charges.columns]) for i in range(len(charges))
            ])
        ], style={"width": "100%", "border-collapse": "collapse"})
    ], style={"overflow-x": "auto"})
])
])

if __name__ == '__main__':
    server.run(debug=True, port=5000)