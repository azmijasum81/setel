import json
import pandas as pd
import streamlit as st
from db import query, SETEL_TABLE, SETEL_STATUS_COL, SETEL_TIMELINE_COL


st.title("Cancellation Funnel")
st.markdown("---")


# ============================================================
# ORDER CANCEL BEFORE PITSTOP ACCEPT
# ============================================================

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


# ============================================================
# ORDER CANCEL AFTER PITSTOP ACCEPT
# ============================================================

st.subheader("Order Cancel After Pitstop Accept")


# ============================================================
# WAITING TIME BUCKET
# ============================================================

bucket_sql = """
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
)

SELECT
    CASE
        WHEN waiting_minutes < 10 THEN '<10 min'
        WHEN waiting_minutes < 20 THEN '10–20 min'
        WHEN waiting_minutes < 30 THEN '20–30 min'
        WHEN waiting_minutes < 45 THEN '30–45 min'
        WHEN waiting_minutes < 60 THEN '45–60 min'
        ELSE '>60 min'
    END AS waiting_bucket,

    COUNT(*) AS total

FROM waiting_time

GROUP BY waiting_bucket

ORDER BY
    CASE waiting_bucket
        WHEN '<10 min' THEN 1
        WHEN '10–20 min' THEN 2
        WHEN '20–30 min' THEN 3
        WHEN '30–45 min' THEN 4
        WHEN '45–60 min' THEN 5
        WHEN '>60 min' THEN 6
    END;
"""

bucket_df = query(bucket_sql)


# Make sure all buckets always appear
bucket_order = [
    "<10 min",
    "10–20 min",
    "20–30 min",
    "30–45 min",
    "45–60 min",
    ">60 min",
]

bucket_df = (
    bucket_df
    .set_index("waiting_bucket")
    .reindex(bucket_order, fill_value=0)
    .reset_index()
)


# ============================================================
# KPI CARDS
# ============================================================

cols = st.columns(6)

for col, (_, row) in zip(cols, bucket_df.iterrows()):
    col.metric(
        label=row["waiting_bucket"],
        value=f"{int(row['total']):,}"
    )


# ============================================================
# DETAILED DATA
# ============================================================

st.markdown("### Waiting Time Details")


detail_sql = """
WITH waiting_time AS (
    SELECT
        p.id,
        p.status,
        p.vpn,
        p.username,
        p.created_at,
        p.waiting_confirmation_on,
        o.externalid,

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
)

SELECT
    id,
    status,
    vpn,
    username,
    created_at,
    waiting_confirmation_on,
    externalid,
    waiting_minutes,

    CASE
        WHEN waiting_minutes < 10 THEN '<10 min'
        WHEN waiting_minutes < 20 THEN '10–20 min'
        WHEN waiting_minutes < 30 THEN '20–30 min'
        WHEN waiting_minutes < 45 THEN '30–45 min'
        WHEN waiting_minutes < 60 THEN '45–60 min'
        ELSE '>60 min'
    END AS waiting_bucket

FROM waiting_time

ORDER BY waiting_minutes DESC;
"""

detail_df = query(detail_sql)


# ============================================================
# TABLE
# ============================================================

if isinstance(detail_df, pd.DataFrame):
    st.dataframe(
        detail_df,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.dataframe(
        pd.DataFrame(detail_df),
        use_container_width=True,
        hide_index=True,
    )
st.markdown("---")
st.markdown("---")


# ============================================================
# ORDER CANCEL BEFORE RIDER ACCEPT
# ============================================================

st.subheader("Cancel Before Rider Accept")


# ============================================================
# KPI
# ============================================================

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


# ============================================================
# DETAIL DATA
# ============================================================

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


# ============================================================
# TABLE
# ============================================================

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