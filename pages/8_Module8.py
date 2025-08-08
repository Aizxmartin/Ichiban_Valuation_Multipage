
import streamlit as st
import json
import numpy as np
import pandas as pd

st.set_page_config(page_title="Module 8: Final Summary (Complete JSON + UX)", page_icon="📊")
st.title("📊 Module 8: Final Valuation Summary – Complete JSON (Outliers, Estimates, Remarks)")

# --- Preconditions
missing = []
if "adjusted_comps" not in st.session_state:
    missing.append("adjusted_comps")
if "subject_data" not in st.session_state:
    missing.append("subject_data")
if "online_avg" not in st.session_state:
    missing.append("online_avg")
if missing:
    st.error("❌ Missing required data in session_state: " + ", ".join(missing) + ". Complete prior modules.")
    st.stop()

# Copies
comps = st.session_state["adjusted_comps"].copy()
subject = st.session_state["subject_data"]
online_avg = float(st.session_state["online_avg"])

# Optional: online estimates saved earlier (e.g., Module 3)
online_estimates = st.session_state.get("online_estimates", {})
zillow_val = online_estimates.get("zillow")
redfin_val = online_estimates.get("redfin")
real_avm_val = online_estimates.get("real_avm")

if not online_estimates:
    st.warning("ℹ️ Online Estimates are missing. If you want them in the report, set st.session_state['online_estimates'] in Module 3 (Zillow/Redfin/Real AVM).")

# --- Ensure numeric types
for col in ["ag_sf","net_price","ag_adj","bgf_adj","bgu_adj","adjusted_price"]:
    if col in comps.columns:
        comps[col] = pd.to_numeric(comps[col], errors="coerce")

# --- Total Adjustments column (fallback if missing)
for col in ["ag_adj","bgf_adj","bgu_adj"]:
    if col not in comps.columns:
        comps[col] = 0
if "total_adjustments" not in comps.columns:
    comps["total_adjustments"] = comps["ag_adj"].fillna(0) + comps["bgf_adj"].fillna(0) + comps["bgu_adj"].fillna(0)

# --- Days in MLS
days_series = None
if "Days In MLS" in comps.columns:
    days_series = pd.to_numeric(comps["Days In MLS"], errors="coerce")
elif "days_in_mls" in comps.columns:
    days_series = pd.to_numeric(comps["days_in_mls"], errors="coerce")
else:
    days_series = pd.Series(dtype="float64")
avg_days = int(days_series.mean()) if days_series.notna().any() else "N/A"
comps["days_in_mls"] = days_series

if avg_days == "N/A":
    st.warning("ℹ️ Average Days in MLS is N/A. Add a 'Days In MLS' column in your comps CSV for better commentary.")

# --- Public remarks (optional) + snippet
remarks_cols = ["Public Remarks", "PublicRemarks", "PUBLIC REMARKS", "public_remarks", "Remarks"]
remarks_found = [c for c in remarks_cols if c in comps.columns]
if remarks_found:
    comps["public_remarks"] = comps[remarks_found[0]].astype(str).fillna("")
else:
    comps["public_remarks"] = ""
comps["remarks_snippet"] = comps["public_remarks"].str.slice(0, 400)

if remarks_found:
    st.info(f"💬 Using remarks column: '{remarks_found[0]}' (truncated to 400 chars per comp).")
else:
    st.warning("ℹ️ No remarks column found. GPT will have less qualitative context.")

# --- Raw range
if len(comps) == 0:
    st.error("No comps available after adjustments.")
    st.stop()
prices = comps["adjusted_price"].astype(float)
raw_low = float(prices.min())
raw_high = float(prices.max())
raw_range = [raw_low, raw_high]

# --- Average PPSF
total_sf = float(comps["ag_sf"].sum())
avg_ppsf = round(float(comps["adjusted_price"].sum()) / total_sf, 2) if total_sf > 0 else 0.0

# --- Outlier filtering: IQR on adjusted_price + PPSF sanity check
q1, q3 = prices.quantile(0.25), prices.quantile(0.75)
iqr = q3 - q1
low_cut = float(q1 - 1.5 * iqr)
high_cut = float(q3 + 1.5 * iqr)
filtered = comps[(comps["adjusted_price"] >= low_cut) & (comps["adjusted_price"] <= high_cut)]

ppsf = (filtered["adjusted_price"] / filtered["ag_sf"].replace(0, pd.NA)).astype(float)
ppsf_q1, ppsf_q3 = ppsf.quantile(0.25), ppsf.quantile(0.75)
ppsf_iqr = ppsf_q3 - ppsf_q1
ppsf_low = float(ppsf_q1 - 1.5 * ppsf_iqr)
ppsf_high = float(ppsf_q3 + 1.5 * ppsf_iqr)
filtered = filtered[(ppsf >= ppsf_low) & (ppsf <= ppsf_high)]

# --- Normalized range (20–80th) + $150K cap around median
if not filtered.empty:
    norm_low = float(filtered["adjusted_price"].quantile(0.20))
    norm_high = float(filtered["adjusted_price"].quantile(0.80))
    norm_median = float(filtered["adjusted_price"].median())
else:
    norm_low = float(prices.quantile(0.20))
    norm_high = float(prices.quantile(0.80))
    norm_median = float(prices.median())

MAX_SPREAD = 150_000.0
spread = norm_high - norm_low
if spread > MAX_SPREAD:
    half = MAX_SPREAD / 2.0
    norm_low = max(raw_low, norm_median - half)
    norm_high = min(raw_high, norm_median + half)

normalized_range = [norm_low, norm_high]

# --- Compose JSON
summary = {
    "subject_property": subject,
    "online_estimate_average": online_avg,
    "adjusted_price_range": raw_range,
    "normalized_range": normalized_range,
    "normalized_median": norm_median,
    "average_ppsf": avg_ppsf,
    "average_days_in_mls": avg_days,
    "outlier_notes": {
        "method": "IQR on adjusted_price + PPSF sanity band; normalized = 20–80th percentiles; $150K cap around median as needed.",
        "price_iqr_low_cut": low_cut,
        "price_iqr_high_cut": high_cut,
        "ppsf_low": ppsf_low,
        "ppsf_high": ppsf_high,
        "filtered_count": int(len(filtered)),
        "total_count": int(len(comps)),
    },
    "online_estimates": {
        "zillow": zillow_val,
        "redfin": redfin_val,
        "real_avm": real_avm_val
    },
    "comps": comps.to_dict(orient="records"),
    "gpt_review": "Complete JSON prepared for GPT review and backup report."
}

# --- JSON-safe converter
def convert_all(obj):
    if isinstance(obj, dict):
        return {k: convert_all(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_all(item) for item in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    elif isinstance(obj, pd.Series):
        return [None if (isinstance(x, float) and np.isnan(x)) else x for x in obj.tolist()]
    return obj

with open("module9_analysis.json", "w") as f:
    json.dump(convert_all(summary), f, indent=2)

st.success("✅ Summary saved as 'module9_analysis.json'")
st.info("🧷 Backup path: You can always generate a non-GPT report in **Module 9** if Module 11/API has issues.")

# --- Previews & Guidance
st.subheader("🔎 Preview — Adjusted Comps")
cols = [c for c in ["full_address","ag_sf","net_price","ag_adj","bgf_adj","bgu_adj","total_adjustments","adjusted_price","days_in_mls","remarks_snippet"] if c in comps.columns]
st.dataframe(comps[cols])

st.subheader("📏 Ranges")
st.write(f"Raw Range: ${raw_low:,.0f} – ${raw_high:,.0f}")
st.write(f"Normalized Range: ${norm_low:,.0f} – ${norm_high:,.0f} (median ${norm_median:,.0f})")
if abs(raw_low - norm_low) < 1 and abs(raw_high - norm_high) < 1:
    st.info("ℹ️ Normalized range matches raw range — no strong outliers were detected by IQR/PPSF filters.")

st.subheader("⏱️ Average Days in MLS")
st.write(avg_days)

st.subheader("💻 Online Estimates (captured)")
st.json(summary["online_estimates"])

st.subheader("🧪 Outlier Notes")
st.json(summary["outlier_notes"])

st.caption("Next: Open **Module 11** for GPT-enhanced report (with auto-fallback). If API fails, use **Module 9** for the backup report.")
