import streamlit as st
import pandas as pd
from db import (query, GRAFANA_TABLE, SETEL_TABLE,
                GRAFANA_STATUS_COL, SETEL_STATUS_COL)

st.title("Dashboard")


def summary(table, status_col):
    df = query(f"""
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN LOWER({status_col}) = 'cancelled' THEN 1 ELSE 0 END) AS cancelled
        FROM {table}
    """)
    total, cancelled = int(df.total[0]), int(df.cancelled[0] or 0)
    rate = cancelled / total * 100 if total else 0
    return total, cancelled, rate


g_total, g_cancel, g_rate = summary(GRAFANA_TABLE, GRAFANA_STATUS_COL)
s_total, s_cancel, s_rate = summary(SETEL_TABLE, SETEL_STATUS_COL)

c1, c2, c3 = st.columns(3)
c1.metric("Total orders (Grafana)", f"{g_total:,}")
c2.metric("Total orders (Setel)", f"{s_total:,}")
c3.metric("Difference", f"{g_total - s_total:,}")

c4, c5 = st.columns(2)
c4.metric("Cancellation rate (Grafana)", f"{g_rate:.1f}%", f"{g_cancel:,} cancelled", delta_color="off")
c5.metric("Cancellation rate (Setel)", f"{s_rate:.1f}%", f"{s_cancel:,} cancelled", delta_color="off")

st.subheader("Comparison")
comp = pd.DataFrame({
    "source": ["Grafana", "Setel"],
    "total_orders": [g_total, s_total],
    "cancelled": [g_cancel, s_cancel],
    "cancellation_rate_%": [round(g_rate, 2), round(s_rate, 2)],
}).set_index("source")
st.dataframe(comp, use_container_width=True)
st.bar_chart(comp[["total_orders", "cancelled"]])