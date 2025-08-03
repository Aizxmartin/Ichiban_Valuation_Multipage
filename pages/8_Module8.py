import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Module 8: Enhanced Market Valuation Summary Report", layout="wide")
st.title("📊 Module 8: Enhanced Market Valuation Summary Report")

# Check session state for required data
required_keys = ["adjusted_comps", "subject_data", "online_avg"]
missing = [key for key in required_keys if key not in st.session_state]
if missing:
    st.error(f"❌ Missing required data: {', '.join(missing)}. Please complete prior modules.")
    st.stop()

comps = st.session_state["adjusted_comps"].copy()
subject_data = st.session_state["subject_data"]
online_avg = st.session_state["online_avg"]

# Summary stats
min_price = comps["adjusted_price"].min()
max_price = comps["adjusted_price"].max()
avg_ppsf = round(comps["adjusted_price"].sum() / comps["ag_sf"].sum(), 2)
avg_days_in_mls = comps["days_in_mls"].mean() if "days_in_mls" in comps.columns else None

# Display Summary
st.subheader("🏠 Subject Property")
st.markdown(f"**Address:** {subject_data.get('address', 'N/A')}")
st.markdown(f"**Above Grade SF:** {subject_data.get('ag_sf', 'N/A')} | **Bedrooms:** {subject_data.get('bedrooms', 'N/A')} | **Bathrooms:** {subject_data.get('bathrooms', 'N/A')}")

st.subheader("📊 Valuation Summary")
st.markdown(f"**Online Estimate Average:** ${online_avg:,.0f}")
st.markdown(f"**Adjusted Comp Range:** {min_price:,.0f}–{max_price:,.0f}")
st.markdown(f"**Average Price per SF:** ${avg_ppsf:,.2f}")
st.markdown(f"**Average Days in MLS:** {round(avg_days_in_mls, 1) if avg_days_in_mls is not None else 'N/A'}")

# Show comps table
st.subheader("🏘️ Adjusted Comparable Sales")
cols_to_show = ["full_address", "ag_sf", "net_price", "ag_adj", "bgf_adj", "bgu_adj", "total_adjustments", "adjusted_price", "days_in_mls", "public_remarks"]
cols_existing = [col for col in cols_to_show if col in comps.columns]
st.dataframe(comps[cols_existing])

# Save JSON summary
summary = {
    "subject_property": subject_data,
    "online_estimate_average": online_avg,
    "adjusted_price_range": [min_price, max_price],
    "average_ppsf": avg_ppsf,
    "average_days_in_mls": round(avg_days_in_mls, 1) if avg_days_in_mls is not None else None,
    "comps": comps.to_dict(orient="records")
}

json_path = "module8_summary.json"
with open(json_path, "w") as f:
    json.dump(summary, f, indent=2)

st.success(f"✅ Summary JSON saved as '{json_path}'")

# --- ✅ Add download button ---
with open(json_path, "rb") as f:
    st.download_button(
        label="📥 Download Module 8 Summary JSON",
        data=f,
        file_name="module8_summary.json",
        mime="application/json"
    )

# (Optional) Preview JSON structure
with st.expander("📄 Preview JSON Summary"):
    st.json(summary)
