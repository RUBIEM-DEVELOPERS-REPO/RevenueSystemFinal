import os
import logging
from dotenv import load_dotenv
import pandas as pd

# --- Load environment variables ---
load_dotenv()

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("revenue_assurance.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Helper Functions ---
def load_env_var(name: str, default=None, required=True):
    """Fetch env var safely with default and error handling."""
    value = os.getenv(name, default)
    if required and value is None:
        logger.error(f"Missing required environment variable: {name}")
        raise ValueError(f"Missing required environment variable: {name}")
    return value

def df_summary(df: pd.DataFrame, name="DataFrame"):
    """Quick summary for debugging in logs."""
    logger.info(f"🔎 {name}: {len(df)} rows, {len(df.columns)} columns")
    if not df.empty:
        logger.info(f"Columns: {list(df.columns)}")
        logger.info(f"Head:\n{df.head(3)}")

def format_currency(value, currency="USD"):
    """Format numbers as currency for reports."""
    try:
        return f"{currency} {float(value):,.2f}"
    except Exception:
        return f"{currency} 0.00"

def safe_cast(val, to_type=float, default=0.0):
    """Safely cast values (avoids Decimal/NoneType errors)."""
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default
