import streamlit as st
import duckdb
import pandas as pd

st.title("Setel Cancellation Analysis")

df_partner = pd.read_csv("data/partner_data.csv")
df_orders = pd.read_excel("data/List of orders - jun - sep.xlsx")

st.subheader("Partner data")
st.dataframe(df_partner.head())
st.write("Columns:", list(df_partner.columns))

st.subheader("Orders")
st.dataframe(df_orders.head())
st.write("Columns:", list(df_orders.columns))

st.subheader("Row counts (DuckDB)")
result = duckdb.sql("""
    SELECT 'Partner' AS source, COUNT(*) AS total_rows FROM df_partner
    UNION ALL
    SELECT 'Orders' AS source, COUNT(*) AS total_rows FROM df_orders
""").df()
st.dataframe(result)