import streamlit as st

st.set_page_config(page_title="Setel Analysis", layout="wide")

pg = st.navigation([
    st.Page("views/quick_insight.py", title="Quick Insight", icon="🔎"),
    st.Page("views/dashboard.py", title="Dashboard", icon="📊"),
    st.Page("views/cancellation_funnel.py", title="Cancellation Funnel", icon="🔻"),
])
pg.run()