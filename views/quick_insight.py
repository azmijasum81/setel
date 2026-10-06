import streamlit as st
from db import query, GRAFANA_TABLE, SETEL_TABLE

st.title("Quick Insight")

limit = st.slider("Rows to preview", 5, 1000, 100)

st.subheader("Raw data in Grafana")
st.dataframe(query(f"SELECT * FROM {GRAFANA_TABLE} LIMIT {limit}"), use_container_width=True)

st.subheader("Data from Setel")
st.dataframe(query(f"SELECT * FROM {SETEL_TABLE} LIMIT {limit}"), use_container_width=True)

st.subheader("Row counts (DuckDB)")
st.dataframe(
    query(f"""
        SELECT 'Grafana' AS source, COUNT(*) AS total_rows FROM {GRAFANA_TABLE}
        UNION ALL
        SELECT 'Setel', COUNT(*) FROM {SETEL_TABLE}
    """),
    use_container_width=True,
)