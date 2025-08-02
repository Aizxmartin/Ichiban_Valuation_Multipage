
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Module 7: Basement Adjustments", layout="wide")
st.title("🏗️ Module 7: Basement Adjustments")

if "adjusted_comps" not in st.session_state or "subject_data" not in st.session_state:
    st.error("❌ Adjusted comps or subject data not found. Complete previous modules.")
    st.stop()

df = st.session_state.adjusted_comps.copy()
subject = st.session_state.subject_data

# Get subject's basement values (default to 0 if not present)
subject_bgf = subject.get("below_grade_finished", 0)
subject_bgu = subject.get("below_grade_unfinished", 0)

# PATCH: Use original .csv headers if remapped names are missing
if "below_grade_finished" not in df.columns and "Below Grade Finished Area" in df.columns:
    df["below_grade_finished"] = df["Below Grade Finished Area"]

if "below_grade_unfinished" not in df.columns and "Below Grade Unfinished Area" in df.columns:
    df["below_grade_unfinished"] = df["Below Grade Unfinished Area"]

# Fill missing with 0
df["below_grade_finished"] = df["below_grade_finished"].fillna(0)
df["below_grade_unfinished"] = df["below_grade_unfinished"].fillna(0)

# Get schema values
bgf_rate = st.session_state.get("schema", {}).get("below_grade_finished_adjustment", 25)
bgu_rate = st.session_state.get("schema", {}).get("below_grade_unfinished_adjustment", 10)

# Calculate adjustments
df["bgf_diff"] = df["below_grade_finished"] - subject_bgf
df["bgu_diff"] = df["below_grade_unfinished"] - subject_bgu
df["bgf_adj"] = df["bgf_diff"] * bgf_rate
df["bgu_adj"] = df["bgu_diff"] * bgu_rate

# Total adjustments (combine with existing ag_adj if present)
df["total_adjustments"] = df.get("ag_adj", 0) + df["bgf_adj"] + df["bgu_adj"]
df["adjusted_price"] = df["net_price"] + df["total_adjustments"]

# Display
st.subheader("Adjusted Comps with Basement Adjustments")
st.dataframe(df[[
    "full_address", "ag_sf", "net_price", "ag_adj",
    "bgf_adj", "bgu_adj", "total_adjustments", "adjusted_price"
]])

# Save to state for Module 8
st.session_state["adjusted_comps"] = df
