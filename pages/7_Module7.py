
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Module 7: Basement Adjustments", layout="wide")
st.title("🏗️ Module 7: Adjust for Basement Differences")

if "adjusted_comps" not in st.session_state or "subject_data" not in st.session_state:
    st.error("❌ Missing adjusted comps or subject data. Please complete prior modules.")
    st.stop()

df = st.session_state.adjusted_comps.copy()
subject = st.session_state.subject_data

# Get subject basement data, fallback to 0 if missing
subject_bgf = subject.get("below_grade_finished", 0)
subject_bgu = subject.get("below_grade_unfinished", 0)

# Ensure required columns exist in DataFrame
if "below_grade_finished" not in df.columns:
    df["below_grade_finished"] = 0
if "below_grade_unfinished" not in df.columns:
    df["below_grade_unfinished"] = 0

# Fill missing values with 0
df["bgf"] = df["below_grade_finished"].fillna(0)
df["bgu"] = df["below_grade_unfinished"].fillna(0)

# Basement differences
df["bgf_diff"] = df["bgf"] - subject_bgf
df["bgu_diff"] = df["bgu"] - subject_bgu

# Apply adjustment rates
bgf_rate = 20
bgu_rate = 10

df["bgf_adj"] = df["bgf_diff"] * bgf_rate
df["bgu_adj"] = df["bgu_diff"] * bgu_rate

# Total adjustment combines AG, BGF, and BGU adjustments
df["total_adjustments"] = df["ag_adj"] + df["bgf_adj"] + df["bgu_adj"]
df["adjusted_price"] = df["net_price"] + df["total_adjustments"]

# Save updated comps
st.session_state.adjusted_comps = df

st.success("✅ Basement adjustments applied.")
st.dataframe(df[["full_address", "ag_sf", "net_price", "ag_adj", "bgf_adj", "bgu_adj", "total_adjustments", "adjusted_price"]])
