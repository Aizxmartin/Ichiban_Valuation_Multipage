import streamlit as st
import pandas as pd

st.set_page_config(page_title="Module 6: Final Summary", layout="wide")
st.title("📊 Module 6: Final Valuation Summary Report")

# Check for required data
if "adjusted_comps" not in st.session_state or "online_avg" not in st.session_state:
    st.error("❌ Missing adjusted comps or online average. Complete prior modules.")
    st.stop()

comps = st.session_state.adjusted_comps.copy()
online_avg = st.session_state.online_avg

# Summary statistics
min_price = comps["adjusted_price"].min()
max_price = comps["adjusted_price"].max()
avg_ppsf = round(comps["adjusted_price"].sum() / comps["ag_sf"].sum(), 2)

# Summary display
st.subheader("📈 Adjusted Comp Range")
st.markdown(f"**Low**: ${min_price:,.0f} &nbsp;&nbsp;&nbsp; **High**: ${max_price:,.0f}")

st.subheader("🏠 Online Estimate Average")
st.markdown(f"**Online Avg**: ${online_avg:,.0f}")

st.subheader("📐 Recommended Market Value Range")
st.markdown(f"**Range**: ${online_avg:,.0f} – ${max_price:,.0f}")

st.subheader("📄 Adjusted Comps Table")
st.dataframe(comps[["full_address", "ag_sf", "net_price", "adjusted_price"]])

# Save to session_state
st.session_state.valuation_range = (online_avg, max_price)
