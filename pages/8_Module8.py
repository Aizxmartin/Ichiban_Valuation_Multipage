
import streamlit as st
import json
import numpy as np
import pandas as pd

st.set_page_config(page_title="Module 8: Final Summary (Complete JSON + Inline Estimates)", page_icon="📊")
st.title("📊 Module 8: Final Valuation Summary – Complete JSON")

# Preconditions
if "adjusted_comps" not in st.session_state or "subject_data" not in st.session_state or "online_avg" not in st.session_state:
    st.error("❌ Missing required data. Complete Modules 1–7 and 3.")
    st.stop()

comps = st.session_state["adjusted_comps"].copy()
subject = st.session_state["subject_data"]
online_avg = float(st.session_state["online_avg"])

# Inline Online Estimates (if missing)
est = st.session_state.get("online_estimates", {})
if not est or all(v in (None, 0, "") for v in est.values()):
    st.warning("ℹ️ Online Estimates are missing. You can optionally enter them here.")
    c1, c2, c3 = st.columns(3)
    with c1:
        z_in = st.number_input("Zillow ($)", min_value=0, step=1000, format="%i")
    with c2:
        r_in = st.number_input("Redfin ($)", min_value=0, step=1000, format="%i")
    with c3:
        a_in = st.number_input("Real AVM ($)", min_value=0, step=1000, format="%i")
    if st.button("Save Estimates to Session"):
        st.session_state["online_estimates"] = {
            "zillow": z_in if z_in > 0 else None,
            "redfin": r_in if r_in > 0 else None,
            "real_avm": a_in if a_in > 0 else None
        }
        st.success("✅ Online estimates saved to session. Re-run this module to include them in JSON.")
est = st.session_state.get("online_estimates", {})  # refresh

# Ensure numeric types
for col in ["ag_sf","net_price","ag_adj","bgf_adj","bgu_adj","adjusted_price"]:
    if col in comps.columns:
        comps[col] = pd.to_numeric(comps[col], errors="coerce")

# Total Adjustments
for col in ["ag_adj","bgf_adj","bgu_adj"]:
    if col not in comps.columns:
        comps[col] = 0
if "total_adjustments" not in comps.columns:
    comps["total_adjustments"] = comps["ag_adj"].fillna(0) + comps["bgf_adj"].fillna(0) + comps["bgu_adj"].fillna(0)

# Days in MLS
if "Days In MLS" in comps.columns:
    s = pd.to_numeric(comps["Days In MLS"], errors="coerce")
elif "days_in_mls" in comps.columns:
    s = pd.to_numeric(comps["days_in_mls"], errors="coerce")
else:
    s = pd.Series(dtype="float64")
avg_days = int(s.mean()) if s.notna().any() else "N/A"
comps["days_in_mls"] = s

# Remarks
remarks_cols = ["Public Remarks", "PublicRemarks", "PUBLIC REMARKS", "public_remarks", "Remarks"]
remarks_found = [c for c in remarks_cols if c in comps.columns]
if remarks_found:
    comps["public_remarks"] = comps[remarks_found[0]].astype(str).fillna("")
else:
    comps["public_remarks"] = ""
comps["remarks_snippet"] = comps["public_remarks"].str.slice(0, 400)

# Raw range
if len(comps) == 0:
    st.error("No comps available after adjustments.")
    st.stop()
prices = comps["adjusted_price"].astype(float)
raw_low = float(prices.min()); raw_high = float(prices.max())

# Avg PPSF
total_sf = float(comps["ag_sf"].sum())
avg_ppsf = round(float(comps["adjusted_price"].sum()) / total_sf, 2) if total_sf > 0 else 0.0

# Outlier filter (IQR + PPSF)
q1, q3 = prices.quantile(0.25), prices.quantile(0.75)
iqr = q3 - q1
low_cut = float(q1 - 1.5 * iqr); high_cut = float(q3 + 1.5 * iqr)
filtered = comps[(comps["adjusted_price"] >= low_cut) & (comps["adjusted_price"] <= high_cut)]
ppsf = (filtered["adjusted_price"] / filtered["ag_sf"].replace(0, pd.NA)).astype(float)
ppsf_q1, ppsf_q3 = ppsf.quantile(0.25), ppsf.quantile(0.75)
ppsf_iqr = ppsf_q3 - ppsf_q1
ppsf_low = float(ppsf_q1 - 1.5 * ppsf_iqr); ppsf_high = float(ppsf_q3 + 1.5 * ppsf_iqr)
filtered = filtered[(ppsf >= ppsf_low) & (ppsf <= ppsf_high)]

# Normalized range + 150k cap
if not filtered.empty:
    norm_low = float(filtered["adjusted_price"].quantile(0.20))
    norm_high = float(filtered["adjusted_price"].quantile(0.80))
    norm_median = float(filtered["adjusted_price"].median())
else:
    norm_low = float(prices.quantile(0.20))
    norm_high = float(prices.quantile(0.80))
    norm_median = float(prices.median())
MAX_SPREAD = 150_000.0
if norm_high - norm_low > MAX_SPREAD:
    half = MAX_SPREAD / 2.0
    norm_low = max(raw_low, norm_median - half)
    norm_high = min(raw_high, norm_median + half)

summary = {
    "subject_property": subject,
    "online_estimate_average": online_avg,
    "adjusted_price_range": [raw_low, raw_high],
    "normalized_range": [norm_low, norm_high],
    "normalized_median": norm_median,
    "average_ppsf": avg_ppsf,
    "average_days_in_mls": avg_days,
    "outlier_notes": {
        "method": "IQR + PPSF band; normalized 20–80th; $150K cap around median",
        "price_iqr_low_cut": low_cut, "price_iqr_high_cut": high_cut,
        "ppsf_low": ppsf_low, "ppsf_high": ppsf_high,
        "filtered_count": int(len(filtered)), "total_count": int(len(comps))
    },
    "online_estimates": {
        "zillow": est.get("zillow"),
        "redfin": est.get("redfin"),
        "real_avm": est.get("real_avm")
    },
    "comps": comps.to_dict(orient="records")
}

# JSON-safe convert
def convert_all(o):
    import numpy as np, pandas as pd
    if isinstance(o, dict):
        return {k: convert_all(v) for k, v in o.items()}
    if isinstance(o, list):
        return [convert_all(v) for v in o]
    if hasattr(o, "tolist"):  # pandas/numpy
        try: return o.tolist()
        except Exception: pass
    if str(type(o)).startswith("<class 'numpy."):
        try: return o.item()
        except Exception: return float(o)
    return o

with open("module9_analysis.json", "w") as f:
    json.dump(convert_all(summary), f, indent=2)

st.success("✅ Summary saved as 'module9_analysis.json' (with Online Estimates if provided)")

# Previews
st.subheader("Online Estimates")
st.json(summary["online_estimates"])
st.subheader("Ranges")
st.write(f"Raw: ${raw_low:,.0f} – ${raw_high:,.0f}")
st.write(f"Normalized: ${norm_low:,.0f} – ${norm_high:,.0f} (median ${norm_median:,.0f})")
