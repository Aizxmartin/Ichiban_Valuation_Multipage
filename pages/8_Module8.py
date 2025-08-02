
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Module 8: Enhanced Market Valuation Summary", layout="wide")
st.title("📊 Module 8: Enhanced Market Valuation Summary Report")

# Check required session state
if "subject_data" not in st.session_state or "adjusted_comps" not in st.session_state or "online_avg" not in st.session_state:
    st.error("❌ Missing required data. Please complete Modules 1–7 first.")
    st.stop()

subject = st.session_state.subject_data
comps = st.session_state.adjusted_comps.copy()
online_avg = st.session_state.online_avg

# Calculate average PPSF
ppsf_avg = round(comps["adjusted_price"].sum() / comps["ag_sf"].sum(), 2)

# Calculate avg days in MLS if available
if "Days in MLS" in comps.columns:
    try:
        comps["Days in MLS"] = pd.to_numeric(comps["Days in MLS"], errors="coerce")
        avg_days = int(comps["Days in MLS"].mean())
        st.session_state["avg_days_in_mls"] = avg_days
    except:
        avg_days = "N/A"
else:
    avg_days = "N/A"

# Display summary
st.subheader("🏠 Subject Property")
st.markdown(f"**Address**: {subject.get('address', 'N/A')}")
st.markdown(f"**Above Grade SF**: {subject.get('ag_sf', 'N/A')} | **Bedrooms**: {subject.get('bedrooms', 'N/A')} | **Bathrooms**: {subject.get('bathrooms', 'N/A')}")

st.subheader("📊 Valuation Summary")
st.markdown(f"**Online Estimate Average**: ${online_avg:,.0f}")
st.markdown(f"**Adjusted Comp Range**: ${comps['adjusted_price'].min():,.0f}–${comps['adjusted_price'].max():,.0f}")
st.markdown(f"**Average Price per SF**: ${ppsf_avg}")
st.markdown(f"**Average Days in MLS**: {avg_days}")

st.subheader("🏘️ Adjusted Comparable Sales")
display_cols = ["full_address", "ag_sf", "net_price", "ag_adj", "bgf_adj", "bgu_adj", "total_adjustments", "adjusted_price"]
if "Public Remarks" in comps.columns:
    display_cols.append("Public Remarks")

st.dataframe(comps[display_cols], use_container_width=True)

# Export summary to JSON for GPT review
export = {
    "subject_property": subject,
    "online_avg": online_avg,
    "adjusted_range": {
        "low": comps["adjusted_price"].min(),
        "high": comps["adjusted_price"].max()
    },
    "average_ppsf": ppsf_avg,
    "average_days_in_mls": avg_days,
    "comps": comps[display_cols].to_dict(orient="records")
}

import json
with open("module8_summary.json", "w") as f:
    json.dump(export, f, indent=2)

st.success("✅ Summary JSON saved as 'module8_summary.json'")
