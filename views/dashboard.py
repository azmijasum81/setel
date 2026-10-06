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
# KPI: Total Setel Orders
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


# =========================
# KPI: Total Cancelled Orders
# =========================

total_cancel_order_sql = """
    SELECT
        COUNT(DISTINCT p.id) AS total_cancel_order
    FROM partner p
    INNER JOIN orders o
        ON CAST(p.id AS VARCHAR) = TRIM(o.externalid)
    WHERE o.externalid NOT LIKE 'SOS%'
      AND p.status = 'cancelled'
"""

total_cancel_order_df = query(total_cancel_order_sql)
total_cancel_order = int(
    total_cancel_order_df.iloc[0]["total_cancel_order"]
)

cancellation_rate = (
    total_cancel_order / total_order * 100
    if total_order > 0
    else 0
)
# =========================
# Display KPIs
# =========================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Setel Order",
        f"{total_order:,}"
    )

with col2:
    st.metric(
        "Total Cancelled Order",
        f"{total_cancel_order:,}"
    )

with col3:
    st.metric(
        "Cancellation Rate",
        f"{cancellation_rate:.2f}%"
    )