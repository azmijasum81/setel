import json
import pandas as pd
import streamlit as st
from db import query, SETEL_TABLE, SETEL_STATUS_COL, SETEL_TIMELINE_COL

st.title("Cancellation Funnel")
st.caption("Stage = the last status an order reached before it was cancelled (from status_timeline).")

df = query(f"SELECT {SETEL_TIMELINE_COL} AS tl FROM {SETEL_TABLE} "
           f"WHERE UPPER({SETEL_STATUS_COL}) = 'CANCELLED'")


def stage_before_cancel(raw):
    try:
        steps = [s["status"] for s in json.loads(raw)]
    except Exception:
        return "UNKNOWN"
    if "CANCELLED" in steps:
        i = steps.index("CANCELLED")
        return steps[i - 1] if i > 0 else "CANCELLED_DIRECTLY"
    return steps[-1] if steps else "UNKNOWN"


df["stage"] = df["tl"].apply(stage_before_cancel)
funnel = df["stage"].value_counts().rename_axis("stage").reset_index(name="cancelled_orders")
funnel["%"] = (funnel["cancelled_orders"] / funnel["cancelled_orders"].sum() * 100).round(1)

st.metric("Total cancelled orders (Setel)", f"{len(df):,}")
st.bar_chart(funnel.set_index("stage")["cancelled_orders"], horizontal=True)
st.dataframe(funnel, use_container_width=True, hide_index=True)