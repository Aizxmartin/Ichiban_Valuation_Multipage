import streamlit as st
import json
import numpy as np
import pandas as pd

st.set_page_config(page_title="Module 8: Final Summary", page_icon="📊")
st.title("📊 Module 8: Final Valuation Summary")

if "adjusted_comps" not in st.session_state or "subject_data" not in st.session_state or "online_avg" not in st.session_state:
    st.error("❌ Missing required data. Complete prior modules.")
    st.stop()

comps = st.session_state["adjusted_comps"].copy()
subject = st.session_state["subject_data"]
online_avg = st.session_state["online_avg"]

# --- Robust Average Days in MLS handling ---
if "Days In MLS" in comps.columns:
    s = pd.to_numeric(comps["Days In MLS"], errors="coerce")
elif "days_in_mls" in comps.columns:
    s = pd.to_numeric(comps["days_in_mls"], errors="coerce")
else:
    s = pd.Series(dtype="float64")

avg_days = int(s.mean()) if s.notna().any() else "N/A"
# Normalize column for downstream modules
comps["days_in_mls"] = s

# --- Core summary stats ---
min_price = float(comps["adjusted_price"].min()) if len(comps) else 0.0
max_price = float(comps["adjusted_price"].max()) if len(comps) else 0.0
total_sf = float(comps["ag_sf"].sum()) if len(comps) else 0.0
avg_ppsf = round(float(comps["adjusted_price"].sum()) / total_sf, 2) if total_sf > 0 else 0.0

# --- Build summary dict ---
summary = {
    "subject_property": subject,
    "online_estimate_average": float(online_avg),
    "adjusted_price_range": [min_price, max_price],
    "average_ppsf": avg_ppsf,
    "average_days_in_mls": avg_days,
    "comps": comps.to_dict(orient="records"),
    "gpt_review": "• Adjusted comps show consistent market conditions.\n• Subject appears well-positioned within the range.\n• Days in MLS indicates demand consistent with area norms."
}

# --- Recursive converter for JSON-safe types ---
def convert_all(obj):
    if isinstance(obj, dict):
        return {k: convert_all(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_all(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    elif isinstance(obj, pd.Series):
        return obj.fillna("").tolist()
    return obj

# --- Save JSON ---
with open("module9_analysis.json", "w") as f:
    json.dump(convert_all(summary), f, indent=2)

st.success("✅ Summary saved as 'module9_analysis.json'")
st.dataframe(comps[["full_address", "ag_sf", "net_price", "adjusted_price", "days_in_mls"]])
st.json(summary)