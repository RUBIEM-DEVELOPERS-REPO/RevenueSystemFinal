import pandas as pd
import numpy as np

def validate_fee_compliance(charges_df, recommendations_df):
    """Validate fee compliance between charges and recommendations"""
    
    # Merge charges with recommendations
    merged = pd.merge(
        charges_df,
        recommendations_df,
        on="transaction_type_id",
        how="left"
    )
    
    # Apply validation
    if not merged.empty:
        merged["status"] = merged.apply(_validate_fee_row, axis=1)
    
    return merged

def _validate_fee_row(row):
    """Validate individual fee row"""
    try:
        amount = float(row["charge_amount"]) if row["charge_amount"] is not None else 0
        min_fee = float(row["recommended_min_fee"]) if row["recommended_min_fee"] is not None else 0
        max_fee = float(row["recommended_max_fee"]) if row["recommended_max_fee"] is not None else float("inf")
        flat_fee = float(row["recommended_flat_fee"]) if row["recommended_flat_fee"] is not None else None
        perc = float(row["recommended_percentage_fee"]) if row["recommended_percentage_fee"] is not None else None

        # Rule 1: Min/Max validation
        if min_fee <= amount <= max_fee:
            return "Valid"
        
        # Rule 2: Flat fee validation
        if flat_fee is not None:
            if amount == flat_fee:
                return "Valid"
            elif amount > flat_fee:
                return "Overcharge"
            else:
                return "Undercharge"

        # Rule 3: Percentage fee validation
        if perc is not None:
            expected_fee = (amount * perc)
            tolerance = expected_fee * 0.1  # 10% tolerance
            if abs(amount - expected_fee) <= tolerance:
                return "Valid"
            elif amount < expected_fee - tolerance:
                return "Undercharge"
            else:
                return "Overcharge"

        return "No Rule"
    except Exception as e:
        return f"Error: {e}"