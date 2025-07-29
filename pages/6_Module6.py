
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
total_sf = comps["ag_sf"].sum()
avg_ppsf = round(comps["adjusted_price"].sum() / total_sf, 2) if total_sf > 0 else 0

# Display comp price range
st.subheader("📈 Adjusted Comp Range")
col1, col2 = st.columns(2)
col1.metric("Low Adjusted Price", f"${min_price:,.0f}")
col2.metric("High Adjusted Price", f"${max_price:,.0f}")

# Online estimate
st.subheader("🏠 Online Estimate Average")
st.metric("Online Avg", f"${online_avg:,.0f}")

# Recommended Range
st.subheader("📐 Recommended Market Value Range")
st.metric("Suggested Range", f"${online_avg:,.0f} – ${max_price:,.0f}")

# Adjusted comps table
st.subheader("📄 Adjusted Comps Table")
st.dataframe(comps[["full_address", "ag_sf", "net_price", "adjusted_price"]])

# Save for future modules
st.session_state["valuation_range"] = (online_avg, max_price)
