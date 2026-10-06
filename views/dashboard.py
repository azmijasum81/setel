import streamlit as st
import pandas as pd

from db import (
    query,
    GRAFANA_TABLE,
    SETEL_TABLE,
    GRAFANA_STATUS_COL,
    SETEL_STATUS_COL,
)

# =========================================================
# PAGE TITLE
# =========================================================

st.title("Dashboard")


# =========================================================
# TOTAL ORDER
# =========================================================

total_order_sql = """
    SELECT
        COUNT(DISTINCT p.id) AS total_order
    FROM partner p
    INNER JOIN orders o
        ON CAST(p.id AS VARCHAR) = TRIM(o.externalid)
    WHERE o.externalid NOT LIKE 'SOS%'
"""

total_order_df = query(total_order_sql)

total_order = int(
    total_order_df.iloc[0]["total_order"]
)


# =========================================================
# COMPLETED ORDER
# =========================================================

total_completed_order_sql = """
    SELECT
        COUNT(DISTINCT p.id) AS total_completed_order
    FROM partner p
    INNER JOIN orders o
        ON CAST(p.id AS VARCHAR) = TRIM(o.externalid)
    WHERE o.externalid NOT LIKE 'SOS%'
      AND p.status = 'completed'
"""

total_completed_order_df = query(total_completed_order_sql)

total_completed_order = int(
    total_completed_order_df.iloc[0]["total_completed_order"]
)


# =========================================================
# CANCELLED ORDER
# =========================================================

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


# =========================================================
# REFUNDED ORDER
# =========================================================

total_refunded_order_sql = """
    SELECT
        COUNT(DISTINCT p.id) AS total_refunded_order
    FROM partner p
    INNER JOIN orders o
        ON CAST(p.id AS VARCHAR) = TRIM(o.externalid)
    WHERE o.externalid NOT LIKE 'SOS%'
      AND p.status = 'refunded'
"""

total_refunded_order_df = query(total_refunded_order_sql)

total_refunded_order = int(
    total_refunded_order_df.iloc[0]["total_refunded_order"]
)


# =========================================================
# PERCENTAGE CALCULATION
# =========================================================

completion_rate = (
    total_completed_order / total_order * 100
    if total_order > 0
    else 0
)

cancellation_rate = (
    total_cancel_order / total_order * 100
    if total_order > 0
    else 0
)

refunded_rate = (
    total_refunded_order / total_order * 100
    if total_order > 0
    else 0
)


# =========================================================
# KPI DISPLAY
# =========================================================

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        label="Total Order",
        value=f"{total_order:,}"
    )

with col2:
    st.metric(
        label="Completed",
        value=f"{total_completed_order:,}"
    )

with col3:
    st.metric(
        label="Completion Rate",
        value=f"{completion_rate:.2f}%"
    )

with col4:
    st.metric(
        label="Cancelled",
        value=f"{total_cancel_order:,}"
    )

with col5:
    st.metric(
        label="Cancellation Rate",
        value=f"{cancellation_rate:.2f}%"
    )

with col6:
    st.metric(
        label="Refunded",
        value=f"{total_refunded_order:,}"
    )


# =========================================================
# ORDER STATUS SUMMARY
# =========================================================

st.divider()

st.subheader("Order Status Summary")

status_sql = """
    SELECT
        p.status,
        COUNT(DISTINCT p.id) AS total_order
    FROM partner p
    INNER JOIN orders o
        ON CAST(p.id AS VARCHAR) = TRIM(o.externalid)
    WHERE o.externalid NOT LIKE 'SOS%'
    GROUP BY p.status
    ORDER BY total_order DESC
"""

status_df = query(status_sql)

st.dataframe(
    status_df,
    use_container_width=True,
    hide_index=True
)