
import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Module 8: Enhanced Market Valuation Summary Report", layout="wide")
st.title("📊 Module 8: Enhanced Market Valuation Summary Report")

if "adjusted_comps" not in st.session_state or "subject_data" not in st.session_state or "online_avg" not in st.session_state:
    st.error("❌ Required data missing. Please complete prior modules.")
    st.stop()

comps = st.session_state["adjusted_comps"].copy()
subject = st.session_state["subject_data"]
online_avg = st.session_state["online_avg"]

# Add Days in MLS from original data if available
if "Days In MLS" in comps.columns:
    comps["days_in_mls"] = comps["Days In MLS"]
elif "days_in_mls" not in comps.columns:
    comps["days_in_mls"] = "N/A"

min_price = comps["adjusted_price"].min()
max_price = comps["adjusted_price"].max()
avg_ppsf = round(comps["adjusted_price"].sum() / comps["ag_sf"].sum(), 2)

days_list = comps["days_in_mls"].dropna()
try:
    avg_days = round(days_list.astype(float).mean()) if not days_list.empty else "N/A"
except:
    avg_days = "N/A"

# Show summary
st.subheader("🏠 Subject Property")
st.markdown(f"Address: {subject.get('address', 'N/A')}")
st.markdown(f"Above Grade SF: {subject.get('above_grade_sf', 'N/A')} | Bedrooms: {subject.get('bedrooms', 'N/A')} | Bathrooms: {subject.get('bathrooms', 'N/A')}")

st.subheader("📊 Valuation Summary")
st.markdown(f"Online Estimate Average: ${online_avg:,.0f}")
st.markdown(f"Adjusted Comp Range: {min_price:,.0f}–{max_price:,.0f}")
st.markdown(f"Average Price per SF: ${avg_ppsf}")
st.markdown(f"Average Days in MLS: {avg_days}")

st.subheader("🏘️ Adjusted Comparable Sales")
st.dataframe(comps[["full_address", "ag_sf", "net_price", "ag_adj", "bgf_adj", "bgu_adj", "total_adjustments", "adjusted_price", "days_in_mls"]])

# Save summary as JSON for Module 9
summary = {
    "subject_property": {
        "address": subject.get("address", "N/A"),
        "above_grade_sf": subject.get("above_grade_sf", "N/A"),
        "bedrooms": subject.get("bedrooms", "N/A"),
        "bathrooms": subject.get("bathrooms", "N/A")
    },
    "online_estimate_average": online_avg,
    "adjusted_price_range": [min_price, max_price],
    "average_ppsf": avg_ppsf,
    "average_days_in_mls": avg_days,
    "comps": comps.to_dict(orient="records")
}

with open("module8_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

st.success("✅ Summary JSON saved as 'module8_summary.json'")
