
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Module 8: Enhanced Market Valuation Summary", layout="wide")
st.title("📊 Module 8: Enhanced Market Valuation Summary Report")

# Check data availability
if "adjusted_comps" not in st.session_state or "online_avg" not in st.session_state or "subject_data" not in st.session_state:
    st.error("❌ Missing required data. Ensure Modules 2, 3, 5, and 7 have been completed.")
    st.stop()

comps = st.session_state["adjusted_comps"]
online_avg = st.session_state["online_avg"]
subject = st.session_state["subject_data"]

# Summary stats
min_price = comps["adjusted_price"].min()
max_price = comps["adjusted_price"].max()
avg_ppsf = round(comps["adjusted_price"].sum() / comps["ag_sf"].sum(), 2)

# Display summary
st.subheader("🏠 Subject Property")
st.markdown(f"**Address**: {subject.get('address', 'N/A')}")
st.markdown(f"**Above Grade SF**: {subject.get('ag_sf', 'N/A')} | Bedrooms: {subject.get('bedrooms', 'N/A')} | Bathrooms: {subject.get('bathrooms', 'N/A')}")

st.subheader("📊 Valuation Summary")
st.markdown(f"**Online Estimate Average**: ${online_avg:,.0f}")
st.markdown(f"**Adjusted Comp Range**: {min_price:,.0f}–{max_price:,.0f}")
st.markdown(f"**Average Price per SF**: ${avg_ppsf:,.2f}")
st.markdown(f"**Recommended Market Range**: {online_avg:,.0f}–{max_price:,.0f}")

st.subheader("🏘️ Adjusted Comparable Sales")
cols_to_display = ["full_address", "ag_sf", "net_price", "ag_adj", "bgf_adj", "bgu_adj", "total_adjustments", "adjusted_price"]
cols_present = [col for col in cols_to_display if col in comps.columns]
st.dataframe(comps[cols_present])
