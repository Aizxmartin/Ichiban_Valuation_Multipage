import streamlit as st
import pandas as pd

st.set_page_config(page_title="Module 4: Comp Filtering", page_icon="📏")
st.title("📏 Module 4: Comp Filtering by Above Grade SF")

# Load cleaned comp data from session_state
if "cleaned_comp_data" not in st.session_state:
    st.error("❌ No cleaned comp data found. Please complete Module 1 first.")
    st.stop()

df = st.session_state.cleaned_comp_data

# Input: Subject Above Grade Finished SF
subject_sf = st.number_input("Enter Subject Above Grade Finished SF", min_value=0)

# Filter logic: 85% to 110% of subject_sf
lower_bound = subject_sf * 0.85
upper_bound = subject_sf * 1.10

filtered_df = df[
    (df["ag_sf"] >= lower_bound) & (df["ag_sf"] <= upper_bound)
]

st.session_state.filtered_comps = filtered_df  # Save to state for next module

# Display result
st.success(f"{len(filtered_df)} comps match the filtering range ({lower_bound:.0f} - {upper_bound:.0f} SF).")
st.dataframe(filtered_df)
