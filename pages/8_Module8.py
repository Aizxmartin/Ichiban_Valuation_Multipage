import streamlit as st
import json
import numpy as np
import pandas as pd

st.set_page_config(page_title="Module 8: Final Summary", page_icon="📊")
st.title("📊 Module 8: Final Valuation Summary")

if "adjusted_comps" not in st.session_state or "subject_data" not in st.session_state or "online_avg" not in st.session_state:
    st.error("❌ Missing required data. Complete prior modules.")
    st.stop()

comps = st.session_state["adjusted_comps"]
subject = st.session_state["subject_data"]
online_avg = st.session_state["online_avg"]

min_price = comps["adjusted_price"].min()
max_price = comps["adjusted_price"].max()
avg_ppsf = round(comps["adjusted_price"].sum() / comps["ag_sf"].sum(), 2)

days_list = comps.get("days_in_mls", [])
try:
    avg_days = round(comps["days_in_mls"].dropna().astype(float).mean()) if "days_in_mls" in comps.columns else "N/A"
except:
    avg_days = "N/A"

summary = {
    "subject_property": subject,
    "online_estimate_average": online_avg,
    "adjusted_price_range": [min_price, max_price],
    "average_ppsf": avg_ppsf,
    "average_days_in_mls": avg_days,
    "comps": comps.to_dict(orient="records"),
    "gpt_review": "• Adjusted comps show consistent market conditions.\n• Subject property appears well-positioned within the pricing range.\n• Average Days in MLS indicates moderate demand."
}

# Safe JSON serialization fix
def convert_to_native(obj):
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    return obj

with open("module9_analysis.json", "w") as f:
    json.dump(summary, f, indent=2, default=convert_to_native)

st.success("✅ Summary saved as 'module9_analysis.json'")
st.json(summary)