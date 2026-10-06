import streamlit as st
from db import query, GRAFANA_TABLE, SETEL_TABLE

st.title("Quick Insight")

limit = st.slider("Rows to preview", 5, 1000, 100)

st.subheader("Total Order : Non SOS")
total_order_sql = f"""
    SELECT
        p.id,
        p.status,
        p.vpn,
        p.username,
        o.externalid
    FROM partner p
    INNER JOIN orders o
        ON CAST(p.id AS VARCHAR) = o.externalid
    WHERE o.externalid NOT LIKE 'SOS%'
    LIMIT {limit}
"""
st.dataframe(
    query(total_order_sql),
    use_container_width=True
)
st.subheader("Total Order : SOS order")
total_order_SOS = f"""
SELECT
    o.*
FROM orders o
LEFT JOIN partner p
    ON CAST(p.id AS VARCHAR) = TRIM(o.externalid)
WHERE p.id IS NULL
LIMIT {limit}
"""
st.dataframe(
query(total_order_SOS),
    use_container_width=True  
)


