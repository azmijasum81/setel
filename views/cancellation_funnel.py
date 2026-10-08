import json
import pandas as pd
import streamlit as st
from db import query, SETEL_TABLE, SETEL_STATUS_COL, SETEL_TIMELINE_COL
st.title("Cancellation Funnel")
st.markdown("---")
# ORDER CANCEL BEFORE PITSTOP ACCEPT
st.subheader("Pitstop analysis")
st.subheader("Order Cancel Before Pitstop Accept")
# KPI
kpi_sql = """
SELECT COUNT(*) AS pending_confirmation_count
FROM partner p
INNER JOIN orders o
    ON CAST(p.id AS VARCHAR) = o.externalid
WHERE o.externalid NOT LIKE 'SOS%'
  AND p.waiting_confirmation_on IS NULL;
"""
kpi_result = query(kpi_sql)

if isinstance(kpi_result, pd.DataFrame):
    pending_count = int(
        kpi_result.iloc[0]["pending_confirmation_count"]
    )
else:
    pending_count = int(
        kpi_result[0]["pending_confirmation_count"]
    )

st.metric(
    label="Customer cancel before pitstop accept",
    value=f"{pending_count:,}"
)

# DATA
data_sql = """
SELECT
    p.id,
    p.status,
    p.vpn,
    p.username,
    p.created_at,
    p.waiting_confirmation_on,
    o.externalid
FROM partner p
INNER JOIN orders o
    ON CAST(p.id AS VARCHAR) = o.externalid
WHERE o.externalid NOT LIKE 'SOS%'
  AND p.waiting_confirmation_on IS NULL
ORDER BY p.created_at DESC;
"""
df = query(data_sql)
# TABLE
if isinstance(df, pd.DataFrame):
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.dataframe(
        pd.DataFrame(df),
        use_container_width=True,
        hide_index=True,
    )
st.markdown("---")
# ORDER AFTER PITSTOP ACCEPT
st.subheader("Total Order After Pitstop Accept")
# KPI — TOTAL ORDER AFTER PITSTOP ACCEPT
total_complete_after_pitstop_sql = """
SELECT COUNT(*) AS total_complete_after_pitstop
FROM partner p
INNER JOIN orders o
    ON CAST(p.id AS VARCHAR) = o.externalid
WHERE o.externalid NOT LIKE 'SOS%'
  AND p.waiting_confirmation_on IS NOT NULL
  AND p.status = 'completed';
"""
total_complete_after_pitstop_result = query(
    total_complete_after_pitstop_sql
)
if isinstance(total_complete_after_pitstop_result, pd.DataFrame):
    total_complete_after_pitstop = int(
        total_complete_after_pitstop_result.iloc[0][
            "total_complete_after_pitstop"
        ]
    )
else:
    total_complete_after_pitstop = int(
        total_complete_after_pitstop_result[0][
            "total_complete_after_pitstop"
        ]
    )
# TOTAL CANCEL ORDER AFTER PITSTOP ACCEPT
total_cancel_after_pitstop_sql = """
SELECT COUNT(*) AS total_cancel_after_pitstop
FROM partner p
INNER JOIN orders o
    ON CAST(p.id AS VARCHAR) = o.externalid
WHERE o.externalid NOT LIKE 'SOS%'
  AND p.waiting_confirmation_on IS NOT NULL
  AND p.status = 'cancelled';
"""

total_cancel_after_pitstop_result = query(
    total_cancel_after_pitstop_sql
)

if isinstance(total_cancel_after_pitstop_result, pd.DataFrame):
    total_cancel_after_pitstop = int(
        total_cancel_after_pitstop_result.iloc[0][
            "total_cancel_after_pitstop"
        ]
    )
else:
    total_cancel_after_pitstop = int(
        total_cancel_after_pitstop_result[0][
            "total_cancel_after_pitstop"
        ]
    )
col1, col2 = st.columns(2)

col1.metric(
    label="Total Complete Order After Pitstop Accept",
    value=f"{total_complete_after_pitstop:,}"
)

col2.metric(
    label="Total Cancel Order After Pitstop Accept",
    value=f"{total_cancel_after_pitstop:,}"
)
st.markdown("### Cancel Waiting Time")

cancel_waiting_sql = """
WITH waiting_time AS (
    SELECT
        date_diff(
            'minute',
            CAST(p.created_at AS TIMESTAMP),
            CAST(p.waiting_confirmation_on AS TIMESTAMP)
        ) AS waiting_minutes

    FROM partner p
    INNER JOIN orders o
        ON CAST(p.id AS VARCHAR) = o.externalid

    WHERE o.externalid NOT LIKE 'SOS%'
    AND p.waiting_confirmation_on IS NOT NULL
    AND p.status = 'cancelled'
),

bucketed AS (
    SELECT
        CASE
            WHEN waiting_minutes < 10 THEN '<10 min'
            WHEN waiting_minutes < 20 THEN '10–20 min'
            WHEN waiting_minutes < 30 THEN '20–30 min'
            WHEN waiting_minutes < 45 THEN '30–45 min'
            WHEN waiting_minutes < 60 THEN '45–60 min'
            ELSE '>60 min'
        END AS waiting_time
    FROM waiting_time
)

SELECT
    waiting_time AS "Waiting Time",
    COUNT(*) AS "Cancel Order"
FROM bucketed
GROUP BY waiting_time
ORDER BY
    CASE waiting_time
        WHEN '<10 min' THEN 1
        WHEN '10–20 min' THEN 2
        WHEN '20–30 min' THEN 3
        WHEN '30–45 min' THEN 4
        WHEN '45–60 min' THEN 5
        WHEN '>60 min' THEN 6
    END;
"""
cancel_waiting_df = query(cancel_waiting_sql)
st.table(cancel_waiting_df)
st.markdown("---")
# ORDER CANCEL BEFORE RIDER ACCEPT
st.subheader("Cancel Before Rider Accept")
# KPI
kpi_rider_cancel_sql = """
SELECT COUNT(*) AS cancel_before_rider_accept_count
FROM partner p
INNER JOIN orders o
    ON CAST(p.id AS VARCHAR) = o.externalid
WHERE o.externalid NOT LIKE 'SOS%'
  AND p.ready_to_dispatch_on IS NULL;
"""
kpi_rider_cancel_result = query(kpi_rider_cancel_sql)

if isinstance(kpi_rider_cancel_result, pd.DataFrame):
    cancel_before_rider_accept_count = int(
        kpi_rider_cancel_result.iloc[0]["cancel_before_rider_accept_count"]
    )
else:
    cancel_before_rider_accept_count = int(
        kpi_rider_cancel_result[0]["cancel_before_rider_accept_count"]
    )

st.metric(
    label="Customer Cancel Before Rider Accept",
    value=f"{cancel_before_rider_accept_count:,}"
)
# DETAIL DATA
rider_cancel_data_sql = """
SELECT
    p.id,
    p.status,
    p.vpn,
    p.username,
    p.created_at,
    p.ready_to_dispatch_on,
    o.externalid
FROM partner p
INNER JOIN orders o
    ON CAST(p.id AS VARCHAR) = o.externalid
WHERE o.externalid NOT LIKE 'SOS%'
  AND p.ready_to_dispatch_on IS NULL
ORDER BY p.created_at DESC;
"""
rider_cancel_df = query(rider_cancel_data_sql)
# TABLE
if isinstance(rider_cancel_df, pd.DataFrame):
    st.dataframe(
        rider_cancel_df,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.dataframe(
        pd.DataFrame(rider_cancel_df),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("---")
st.subheader("Rider Accept Analysis")
# 3. TOTAL COMPLETED AFTER RIDER ACCEPT
total_completed_after_rider_accept_sql = """
SELECT COUNT(*) AS total_completed_after_rider_accept
FROM partner p
INNER JOIN orders o
    ON CAST(p.id AS VARCHAR) = o.externalid
WHERE o.externalid NOT LIKE 'SOS%'
  AND p.ready_to_dispatch_on IS NOT NULL
  AND p.status = 'completed';
"""

total_completed_after_rider_accept_result = query(
    total_completed_after_rider_accept_sql
)

if isinstance(total_completed_after_rider_accept_result, pd.DataFrame):
    total_completed_after_rider_accept = int(
        total_completed_after_rider_accept_result.iloc[0][
            "total_completed_after_rider_accept"
        ]
    )
else:
    total_completed_after_rider_accept = int(
        total_completed_after_rider_accept_result[0][
            "total_completed_after_rider_accept"
        ]
    )
# 4. TOTAL CANCELLED AFTER RIDER ACCEPT
total_cancelled_after_rider_accept_sql = """
SELECT COUNT(*) AS total_cancelled_after_rider_accept
FROM partner p
INNER JOIN orders o
    ON CAST(p.id AS VARCHAR) = o.externalid
WHERE o.externalid NOT LIKE 'SOS%'
  AND p.ready_to_dispatch_on IS NOT NULL
  AND p.status = 'cancelled';
"""

total_cancelled_after_rider_accept_result = query(
    total_cancelled_after_rider_accept_sql
)

if isinstance(total_cancelled_after_rider_accept_result, pd.DataFrame):
    total_cancelled_after_rider_accept = int(
        total_cancelled_after_rider_accept_result.iloc[0][
            "total_cancelled_after_rider_accept"
        ]
    )
else:
    total_cancelled_after_rider_accept = int(
        total_cancelled_after_rider_accept_result[0][
            "total_cancelled_after_rider_accept"
        ]
    )
# DISPLAY KPI
col1, col2 = st.columns(2)
col1.metric(
    label="Total Completed After Rider Accept",
    value=f"{total_completed_after_rider_accept:,}"
)

col2.metric(
    label="Total Cancelled After Rider Accept",
    value=f"{total_cancelled_after_rider_accept:,}"
)
# 5. CANCELLED ORDER SUMMARY — WAITING TIME
st.markdown("### Cancelled Order Summary")
cancelled_rider_waiting_sql = """
WITH customer_waiting AS (
    SELECT
        date_diff(
            'minute',
            CAST(p.created_at AS TIMESTAMP),
            CAST(p.ready_to_dispatch_on AS TIMESTAMP)
        ) AS waiting_minutes

    FROM partner p

    INNER JOIN orders o
        ON CAST(p.id AS VARCHAR) = o.externalid

    WHERE o.externalid NOT LIKE 'SOS%'
      AND p.ready_to_dispatch_on IS NOT NULL
      AND p.status = 'cancelled'
),

bucketed AS (
    SELECT
        CASE
            WHEN waiting_minutes < 10 THEN '<10 min'
            WHEN waiting_minutes < 20 THEN '10–20 min'
            WHEN waiting_minutes < 30 THEN '20–30 min'
            WHEN waiting_minutes < 45 THEN '30–45 min'
            WHEN waiting_minutes < 60 THEN '45–60 min'
            ELSE '>60 min'
        END AS waiting_time
    FROM customer_waiting
)

SELECT
    waiting_time AS "Waiting Time",
    COUNT(*) AS "Cancelled Order"

FROM bucketed

GROUP BY waiting_time

ORDER BY
    CASE waiting_time
        WHEN '<10 min' THEN 1
        WHEN '10–20 min' THEN 2
        WHEN '20–30 min' THEN 3
        WHEN '30–45 min' THEN 4
        WHEN '45–60 min' THEN 5
        WHEN '>60 min' THEN 6
    END;
"""

cancelled_rider_waiting_df = query(
    cancelled_rider_waiting_sql
)
st.table(cancelled_rider_waiting_df)
st.markdown("---")
# analysis on rider arrived
st.subheader("Analysis on Rider Arrived")
st.subheader("Order Cancel before rider arrived")

# ============================================================
# KPI
# ============================================================

order_cancel_before_arrived_kpi_sql = """
SELECT COUNT(*) AS cancel_before_rider_arrived_count
FROM partner p
INNER JOIN orders o
    ON CAST(p.id AS VARCHAR) = o.externalid
WHERE o.externalid NOT LIKE 'SOS%'
  AND p.arrived_on IS NULL;
"""

order_cancel_before_arrived_kpi_result = query(
    order_cancel_before_arrived_kpi_sql
)

if isinstance(order_cancel_before_arrived_kpi_result, pd.DataFrame):
    cancel_before_rider_arrived_count = int(
        order_cancel_before_arrived_kpi_result.iloc[0][
            "cancel_before_rider_arrived_count"
        ]
    )
else:
    cancel_before_rider_arrived_count = int(
        order_cancel_before_arrived_kpi_result[0][
            "cancel_before_rider_arrived_count"
        ]
    )


st.metric(
    label="Order Cancel Before Rider Arrived",
    value=f"{cancel_before_rider_arrived_count:,}"
)


# ============================================================
# DETAIL DATA
# ============================================================

order_cancel_before_arrived_sql = """
SELECT
    p.id,
    p.status,
    p.vpn,
    p.username,
    p.created_at,
    p.arrived_on,
    o.externalid
FROM partner p
INNER JOIN orders o
    ON CAST(p.id AS VARCHAR) = o.externalid
WHERE o.externalid NOT LIKE 'SOS%'
  AND p.arrived_on IS NULL
ORDER BY p.created_at DESC;
"""

order_cancel_before_arrived_df = query(
    order_cancel_before_arrived_sql
)


# ============================================================
# DETAIL TABLE
# ============================================================

if isinstance(order_cancel_before_arrived_df, pd.DataFrame):
    st.dataframe(
        order_cancel_before_arrived_df,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.dataframe(
        pd.DataFrame(order_cancel_before_arrived_df),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("---")


# ============================================================
# ORDER MATCH WITHOUT SOS
# ORDER CANCEL AFTER RIDER ARRIVED
# ============================================================

# ============================================================
# RIDER ARRIVED ANALYSIS
# ============================================================

st.subheader("Analysis on Rider Arrived")
# 1. TOTAL COMPLETED AFTER RIDER ARRIVED
total_completed_after_rider_arrived_sql = """
SELECT COUNT(*) AS total_completed
FROM partner p
INNER JOIN orders o
    ON CAST(p.id AS VARCHAR) = o.externalid
WHERE o.externalid NOT LIKE 'SOS%'
  AND p.arrived_on IS NOT NULL
  AND p.status = 'completed';
"""

total_completed_after_rider_arrived_df = query(
    total_completed_after_rider_arrived_sql
)

total_completed_after_rider_arrived = (
    int(total_completed_after_rider_arrived_df.iloc[0]["total_completed"])
    if not total_completed_after_rider_arrived_df.empty
    else 0
)

# 2. TOTAL CANCELLED AFTER RIDER ARRIVED
total_cancelled_after_rider_arrived_sql = """
SELECT COUNT(*) AS total_cancelled
FROM partner p
INNER JOIN orders o
    ON CAST(p.id AS VARCHAR) = o.externalid
WHERE o.externalid NOT LIKE 'SOS%'
  AND p.arrived_on IS NOT NULL
  AND p.status = 'cancelled';
"""

total_cancelled_after_rider_arrived_df = query(
    total_cancelled_after_rider_arrived_sql
)

total_cancelled_after_rider_arrived = (
    int(total_cancelled_after_rider_arrived_df.iloc[0]["total_cancelled"])
    if not total_cancelled_after_rider_arrived_df.empty
    else 0
)

# KPI
col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Total Completed After Rider Arrived",
        total_completed_after_rider_arrived
    )

with col2:
    st.metric(
        "Total Cancelled After Rider Arrived",
        total_cancelled_after_rider_arrived
    )
# 3. CANCELLED ORDER SUMMARY
st.subheader("Cancelled Order Summary")

cancelled_rider_arrived_waiting_sql = """
WITH customer_waiting AS (
    SELECT
        date_diff(
            'minute',
            CAST(p.created_at AS TIMESTAMP),
            CAST(p.arrived_on AS TIMESTAMP)
        ) AS waiting_minutes

    FROM partner p
    INNER JOIN orders o
        ON CAST(p.id AS VARCHAR) = o.externalid

    WHERE o.externalid NOT LIKE 'SOS%'
      AND p.arrived_on IS NOT NULL
      AND p.status = 'cancelled'
),

bucketed AS (
    SELECT
        CASE
            WHEN waiting_minutes < 10 THEN '<10 min'
            WHEN waiting_minutes < 20 THEN '10–20 min'
            WHEN waiting_minutes < 30 THEN '20–30 min'
            WHEN waiting_minutes < 45 THEN '30–45 min'
            WHEN waiting_minutes < 60 THEN '45–60 min'
            ELSE '>60 min'
        END AS waiting_time

    FROM customer_waiting
)

SELECT
    waiting_time AS "Waiting Time",
    COUNT(*) AS "Cancelled Order"

FROM bucketed

GROUP BY waiting_time

ORDER BY
    CASE waiting_time
        WHEN '<10 min' THEN 1
        WHEN '10–20 min' THEN 2
        WHEN '20–30 min' THEN 3
        WHEN '30–45 min' THEN 4
        WHEN '45–60 min' THEN 5
        WHEN '>60 min' THEN 6
    END;
"""
cancelled_rider_arrived_waiting_df = query(
    cancelled_rider_arrived_waiting_sql
)
st.table(cancelled_rider_arrived_waiting_df)
st.markdown("---")