
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Module 8: Enhanced Valuation Summary", page_icon="📄")
st.title("📄 Module 8: Enhanced Market Valuation Summary Report")

# Check session state for necessary components
if "adjusted_comps" not in st.session_state or "online_avg" not in st.session_state:
    st.error("❌ Missing adjusted comps or online average. Please complete prior modules.")
    st.stop()

# Load data
comps = st.session_state["adjusted_comps"].copy()
online_avg = st.session_state["online_avg"]
subject = st.session_state.get("subject_data", {})

# Compute range and stats
min_price = comps["adjusted_price"].min()
max_price = comps["adjusted_price"].max()
avg_ppsf = round(comps["adjusted_price"].sum() / comps["ag_sf"].sum(), 2)

# GPT-style review placeholder
review_notes = []
if (max_price - online_avg) > 75000:
    review_notes.append("⚠️ The adjusted comp range exceeds $75,000 above the online estimate average. Consider qualifying this wide range in the report.")
else:
    review_notes.append("✅ The price range falls within a reasonable spread of the online average.")

# Display subject property
st.subheader("🏠 Subject Property")
st.write(f"**Address**: {subject.get('address', 'N/A')}")
st.write(f"**Above Grade SF**: {subject.get('ag_sf', 'N/A')}  |  **Bedrooms**: {subject.get('bedrooms', 'N/A')}  |  **Bathrooms**: {subject.get('bathrooms', 'N/A')}")

# Valuation Summary
st.subheader("📊 Valuation Summary")
st.markdown(f"**Online Estimate Average**: ${online_avg:,.0f}")
st.markdown(f"**Adjusted Comp Range**: ${min_price:,.0f} – ${max_price:,.0f}")
st.markdown(f"**Average Price per SF**: ${avg_ppsf:,.2f}")
st.markdown(f"**Recommended Market Range**: ${online_avg:,.0f} – ${max_price:,.0f}")

# Show comp table
st.subheader("🏘️ Adjusted Comparable Sales")
st.dataframe(comps[[
    "full_address", "ag_sf", "net_price", "ag_adj",
    "bgf_adj", "bgu_adj", "total_adjustments", "adjusted_price"
]])

# GPT-style interpretation
st.subheader("💡 AI Observations")
for note in review_notes:
    st.markdown(note)

# Save to session state
st.session_state["valuation_summary"] = {
    "online_avg": online_avg,
    "adjusted_low": min_price,
    "adjusted_high": max_price,
    "avg_ppsf": avg_ppsf,
    "ai_review": review_notes
}
