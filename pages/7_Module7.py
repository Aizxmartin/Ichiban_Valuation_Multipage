
import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Module 7: Basement Adjustments", layout="wide")
st.title("🏗️ Module 7: Basement Adjustments")

# Ensure prior modules completed
if "adjusted_comps" not in st.session_state or "subject_data" not in st.session_state:
    st.error("❌ Missing adjusted comps or subject data. Please complete prior modules.")
    st.stop()

# Load schema
try:
    with open("market_adjustment_schema.json", "r") as f:
        schema = json.load(f)
except FileNotFoundError:
    st.error("Please upload 'market_adjustment_schema.json' in this directory.")
    st.stop()

comps = st.session_state["adjusted_comps"].copy()
subject = st.session_state["subject_data"]

# Fallbacks if not defined
subject_finished = subject.get("below_grade_finished_sf", 0)
subject_unfinished = subject.get("below_grade_unfinished_sf", 0)

# Ensure comps have needed columns
required_cols = ["Below Grade Finished Area", "Below Grade Unfinished Area"]
for col in required_cols:
    if col not in comps.columns:
        st.error(f"❌ Missing required field in comps: '{col}'")
        st.stop()

# Rename for ease
comps["bg_finished"] = pd.to_numeric(comps["Below Grade Finished Area"], errors="coerce").fillna(0)
comps["bg_unfinished"] = pd.to_numeric(comps["Below Grade Unfinished Area"], errors="coerce").fillna(0)

# Differences from subject
comps["bgf_diff"] = comps["bg_finished"] - subject_finished
comps["bgu_diff"] = comps["bg_unfinished"] - subject_unfinished

# Apply adjustments
rate_finished = schema.get("below_grade_finished_adjustment", 30)
rate_unfinished = schema.get("below_grade_unfinished_adjustment", 15)

comps["bgf_adj"] = comps["bgf_diff"] * rate_finished
comps["bgu_adj"] = comps["bgu_diff"] * rate_unfinished

# Update final price
comps["adjusted_price"] += comps["bgf_adj"] + comps["bgu_adj"]

# Save
st.session_state["adjusted_comps"] = comps

# Display
st.subheader("🏠 Adjusted for Basement Differences")
st.dataframe(comps[[
    "full_address", "ag_sf", "net_price", "adjusted_price", 
    "bg_finished", "bg_unfinished", "bgf_adj", "bgu_adj"
]])
