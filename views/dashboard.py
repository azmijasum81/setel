import streamlit as st
import pandas as pd
from db import (
    query,
    GRAFANA_TABLE,
    SETEL_TABLE,
    GRAFANA_STATUS_COL,
    SETEL_STATUS_COL
)

st.title("Dashboard")

# =========================
# Total Setel Order
# =========================

total_order_sql = """
    SELECT
        COUNT(DISTINCT p.id) AS total_order
    FROM partner p
    INNER JOIN orders o
        ON CAST(p.id AS VARCHAR) = TRIM(o.externalid)
    WHERE o.externalid NOT LIKE 'SOS%'
"""

total_order_df = query(total_order_sql)

total_order = int(total_order_df.iloc[0]["total_order"])

st.metric(
    label="Total Setel Order",
    value=f"{total_order:,}"
)

