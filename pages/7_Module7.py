
import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Module 7: Basement Adjustments", layout="wide")
st.title("🏗️ Module 7: Apply Basement Adjustments")

if "adjusted_comps" not in st.session_state:
    st.error("❌ Missing comps from Module 5. Please complete prior steps.")
    st.stop()

df = st.session_state.adjusted_comps.copy()
subject = st.session_state.subject_data
try:
    with open("market_adjustment_schema.json", "r") as f:
        schema = json.load(f)
except FileNotFoundError:
    st.error("Missing 'market_adjustment_schema.json' file.")
    st.stop()

# Get adjustment rates
rate_bgf = schema.get("below_grade_finished_adjustment", 25)
rate_bgu = schema.get("below_grade_unfinished_adjustment", 10)

# Safely handle basement data
if "below_grade_finished" in df.columns:
    df["bgf"] = df["below_grade_finished"].fillna(0)
else:
    df["bgf"] = 0

if "below_grade_unfinished" in df.columns:
    df["bgu"] = df["below_grade_unfinished"].fillna(0)
else:
    df["bgu"] = 0

# Apply basement adjustments
df["basement_adj"] = (df["bgf"] * rate_bgf) + (df["bgu"] * rate_bgu)

# Combine with previous AG adjustments
if "ag_adj" not in df.columns:
    df["ag_adj"] = 0

df["total_adjustments"] = df["ag_adj"] + df["basement_adj"]
df["adjusted_price"] = df["net_price"] + df["total_adjustments"]

# Save updated comps
st.session_state.adjusted_comps = df

# Display
st.success("✅ Basement adjustments applied.")
st.dataframe(df[["full_address", "ag_sf", "bgf", "bgu", "net_price", "ag_adj", "basement_adj", "total_adjustments", "adjusted_price"]])
