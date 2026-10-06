import json
import pandas as pd
import streamlit as st
from db import query, SETEL_TABLE, SETEL_STATUS_COL, SETEL_TIMELINE_COL


st.title("Cancellation Funnel")
st.subheader("Order cancel Before Pitstop accept")
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
    pending_count = int(kpi_result.iloc[0]["pending_confirmation_count"])
else:
    pending_count = int(kpi_result[0]["pending_confirmation_count"])

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