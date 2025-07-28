import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Module 5: Apply Comp Adjustments", layout="wide")
st.title("📐 Module 5: Comp Adjustments Using Schema")

# Ensure required data exists
if "filtered_comps_df" not in st.session_state or "subject_data" not in st.session_state:
    st.error("❌ Missing filtered comps or subject data. Please complete Modules 1–4.")
    st.stop()

# Load schema
try:
    with open("market_adjustment_schema.json", "r") as f:
        schema = json.load(f)
except FileNotFoundError:
    st.error("Please upload 'market_adjustment_schema.json' in this directory.")
    st.stop()

comps = st.session_state["filtered_comps_df"].copy()
subject = st.session_state["subject_data"]

# Above Grade SF adjustment
rate = schema.get("above_grade_adjustment", 40)
comps["ag_diff"] = comps["ag_sf"] - subject["ag_sf"]
comps["ag_adj"] = comps["ag_diff"] * rate

# Final adjusted price
comps["adjusted_price"] = comps["net_price"] + comps["ag_adj"]

# Display
st.dataframe(comps[["full_address", "ag_sf", "net_price", "ag_diff", "ag_adj", "adjusted_price"]])

# Save for next module
st.session_state["adjusted_comps"] = comps
