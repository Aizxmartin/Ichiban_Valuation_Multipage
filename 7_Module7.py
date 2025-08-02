
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Module 7: Basement Adjustments", layout="wide")
st.title("🏗️ Module 7: Adjust for Basement Differences")

# Ensure previous data is available
if "adjusted_comps" not in st.session_state or "subject_data" not in st.session_state:
    st.error("❌ Missing data. Please run Module 5 and Module 2 first.")
    st.stop()

df = st.session_state["adjusted_comps"].copy()
subject = st.session_state["subject_data"]

# Calculate subject basement areas
subject_bgf = subject.get("below_grade_finished", 0)
subject_bgu = subject.get("below_grade_unfinished", 0)

# Load values for adjustments
bgf_rate = 20  # Finished basement adjustment rate
bgu_rate = 10  # Unfinished basement adjustment rate

# Calculate differences and adjustments
df["bgf_diff"] = df.get("below_grade_finished", 0).fillna(0) - subject_bgf
df["bgu_diff"] = df.get("below_grade_unfinished", 0).fillna(0) - subject_bgu

df["bgf_adj"] = df["bgf_diff"] * bgf_rate
df["bgu_adj"] = df["bgu_diff"] * bgu_rate

# Recalculate adjusted price
df["total_adjustments"] = df.get("ag_adj", 0) + df["bgf_adj"] + df["bgu_adj"]
df["adjusted_price"] = df["net_price"] + df["total_adjustments"]

# Store updated comps
st.session_state["adjusted_comps"] = df

# Display result
st.dataframe(df[["full_address", "ag_sf", "net_price", "ag_adj", "bgf_adj", "bgu_adj", "total_adjustments", "adjusted_price"]])
