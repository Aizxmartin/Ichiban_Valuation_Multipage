
import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Module 7: Basement Adjustments", page_icon="🏗️")
st.title("🏗️ Module 7: Basement Adjustments")

# Confirm necessary inputs exist
if "adjusted_comps" not in st.session_state or "subject_data" not in st.session_state:
    st.error("❌ Missing adjusted comps or subject data. Complete prior modules.")
    st.stop()

# Load schema for basement adjustments
try:
    with open("market_adjustment_schema.json", "r") as f:
        schema = json.load(f)
except FileNotFoundError:
    st.error("Schema file missing: market_adjustment_schema.json")
    st.stop()

df = st.session_state["adjusted_comps"].copy()
subject = st.session_state["subject_data"]

# Extract subject basement info (assume 0 if not present)
subject_bgf = subject.get("below_grade_finished", 0)
subject_bgu = subject.get("below_grade_unfinished", 0)

# Schema rates
bgf_rate = schema.get("below_grade_finished_adjustment", 30)
bgu_rate = schema.get("below_grade_unfinished_adjustment", 15)

# Default fill
df["bgf"] = df.get("below_grade_finished", 0).fillna(0)
df["bgu"] = df.get("below_grade_unfinished", 0).fillna(0)

# Calculate differences
df["bgf_diff"] = df["bgf"] - subject_bgf
df["bgu_diff"] = df["bgu"] - subject_bgu

# Apply adjustments
df["bgf_adj"] = df["bgf_diff"] * bgf_rate
df["bgu_adj"] = df["bgu_diff"] * bgu_rate

# Combine adjustments
df["total_adjustments"] = df.get("ag_adj", 0) + df["bgf_adj"] + df["bgu_adj"]
df["adjusted_price"] = df["net_price"] + df["total_adjustments"]

# Display breakdown
st.subheader("🔍 Basement Adjustments Applied")
st.dataframe(df[[
    "full_address", "ag_sf", "net_price", "ag_adj",
    "bgf", "bgu", "bgf_adj", "bgu_adj", "total_adjustments", "adjusted_price"
]])

# Save for next module
st.session_state["adjusted_comps"] = df
