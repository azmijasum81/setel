import duckdb
import pandas as pd
import streamlit as st

# ---- CONFIG: change these to match your DuckDB ----
DB_PATH = "setel.duckdb"
GRAFANA_TABLE = "partner"   # from partner_data.csv (83959 rows)
SETEL_TABLE = "orders"      # from the Excel file (3175 rows)

GRAFANA_STATUS_COL = "status"          # values like completed / cancelled
SETEL_STATUS_COL = "job_status"        # values like COMPLETED / CANCELLED
SETEL_TIMELINE_COL = "status_timeline" # JSON text: [{"status":"CREATED","createdAt":"..."}]
# ---------------------------------------------------


@st.cache_data(show_spinner=False)
def query(sql: str) -> pd.DataFrame:
    # read_only so Streamlit never locks the file for load_data.py
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        return con.execute(sql).df()
    finally:
        con.close()