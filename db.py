import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()  # Load credentials from .env

def get_connection(db_key="conn1"):
    configs = {
        "conn1": {
            "host": os.getenv("CORE_HOST"),
            "database": os.getenv("CORE_DB"),
            "user": os.getenv("CORE_USER"),
            "password": os.getenv("CORE_PASS"),
            "port": os.getenv("CORE_PORT"),
        },
        "conn2": {
            "host": os.getenv("NEON_HOST"),
            "database": os.getenv("NEON_DB"),
            "user": os.getenv("NEON_USER"),
            "password": os.getenv("NEON_PASS"),
            "port": os.getenv("NEON_PORT"),
        },
        "conn3": {
            "host": os.getenv("DUMMY_HOST"),
            "database": os.getenv("DUMMY_DB"),
            "user": os.getenv("DUMMY_USER"),
            "password": os.getenv("DUMMY_PASS"),
            "port": os.getenv("DUMMY_PORT"),
        }
    }
    return psycopg2.connect(**configs[db_key])

def fetch_dataframe(query, conn_key="conn1"):
    conn = get_connection(conn_key)
    df = pd.read_sql(query, conn)
    conn.close()
    return df
