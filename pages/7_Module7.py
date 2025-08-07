import streamlit as st
import json

st.set_page_config(page_title="Module 7: Final Adjustments", page_icon="📐")
st.title("📐 Module 7: Apply All Adjustments (AG + Basement)")

if "filtered_comps_df" not in st.session_state or "subject_data" not in st.session_state:
    st.error("❌ Missing comps or subject data. Complete Modules 1–6 first.")
    st.stop()

# Load adjustment schema
try:
    with open("market_adjustment_schema.json", "r") as f:
        schema = json.load(f)
except FileNotFoundError:
    st.error("Please upload 'market_adjustment_schema.json'.")
    st.stop()

comps = st.session_state["filtered_comps_df"].copy()
subject = st.session_state["subject_data"]

# Safe defaults
subject_ag = subject.get("ag_sf", 0)
subject_bgf = subject.get("below_grade_finished", 0)
subject_bgu = subject.get("below_grade_unfinished", 0)

# Apply adjustments
comps["ag_diff"] = comps["ag_sf"] - subject_ag
comps["bgf_diff"] = comps.get("below_grade_finished", 0) - subject_bgf
comps["bgu_diff"] = comps.get("below_grade_unfinished", 0) - subject_bgu

comps["ag_adj"] = comps["ag_diff"] * schema.get("above_grade_adjustment", 40)
comps["bgf_adj"] = comps["bgf_diff"] * schema.get("below_grade_finished_adjustment", 25)
comps["bgu_adj"] = comps["bgu_diff"] * schema.get("below_grade_unfinished_adjustment", 10)

comps["total_adjustments"] = comps["ag_adj"] + comps["bgf_adj"] + comps["bgu_adj"]
comps["adjusted_price"] = comps["net_price"] + comps["total_adjustments"]

# Save to session
st.session_state["adjusted_comps"] = comps
st.dataframe(comps[["full_address", "ag_sf", "net_price", "ag_adj", "bgf_adj", "bgu_adj", "adjusted_price"]])
st.success("✅ Adjustments Applied")