import streamlit as st
import pandas as pd

st.set_page_config(page_title="Module 4: Comp Filtering", layout="wide")

st.title("📏 Module 4: Comp Filtering by Above Grade SF")

# Ensure cleaned comps exist in session state
if "cleaned_comps" not in st.session_state:
    st.error("❌ No cleaned comp data found. Please complete Module 1 first.")
    st.stop()

df = st.session_state.cleaned_comps.copy()

# Get Subject Above Grade SF
subject_ag_sf = st.number_input("Enter Subject Above Grade Finished SF", min_value=0, value=1800)

# Filter range: 85% to 110%
low, high = 0.85 * subject_ag_sf, 1.10 * subject_ag_sf
filtered_df = df[(df['ag_sf'] >= low) & (df['ag_sf'] <= high)]

st.success(f"{len(filtered_df)} comps within 85–110% of {subject_ag_sf} SF")

# Show filtered comps
st.dataframe(filtered_df)

# Save to session_state for next module
st.session_state.filtered_comps = filtered_df
