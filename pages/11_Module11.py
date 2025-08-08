
import json
from pathlib import Path
import streamlit as st
from docx import Document

# OpenAI (optional)
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

st.set_page_config(page_title="Module 11: GPT Market Review (Fixed JSON Source)", page_icon="🤖")
st.title("🤖 Module 11: GPT Commentary & Enhanced Report — Fixed JSON Source")

# --- Load JSON produced by Module 8
json_path = Path("module9_analysis.json")
if not json_path.exists():
    st.error("❌ Could not find 'module9_analysis.json'. Please run Module 8 first.")
    st.stop()

with open(json_path, "r") as f:
    summary = json.load(f)

subject = summary.get("subject_property", {})
online_avg = summary.get("online_estimate_average", 0)
raw_low, raw_high = summary.get("adjusted_price_range", [0, 0])
norm_low, norm_high = summary.get("normalized_range", [raw_low, raw_high])
norm_median = summary.get("normalized_median", (norm_low + norm_high) / 2)
avg_ppsf = summary.get("average_ppsf", 0)
days_mls = summary.get("average_days_in_mls", "N/A")
comps = summary.get("comps", [])
outlier_notes = summary.get("outlier_notes", {})
estimates = summary.get("online_estimates", {})

zillow_val = estimates.get("zillow")
redfin_val = estimates.get("redfin")
real_avm_val = estimates.get("real_avm")

def money(v):
    try:
        return f"${float(v):,.0f}"
    except Exception:
        return str(v)

# Snapshot (shows Days in MLS explicitly)
st.subheader("📊 Valuation Snapshot")
st.write(f"Online Estimate Avg: {money(online_avg)}")
st.write(f"Average Price per SF: ${avg_ppsf}")
st.write(f"Average Days in MLS: {days_mls}")
st.write(f"Raw Range: {money(raw_low)} – {money(raw_high)}")
st.write(f"Normalized Range: {money(norm_low)} – {money(norm_high)} (median {money(norm_median)})")

# Remarks block (limited)
remarks_snippets = [c.get("remarks_snippet", "") for c in comps if c.get("remarks_snippet")]
remarks_snippets = remarks_snippets[:5]
remarks_block = "\n".join(f"- {s}" for s in remarks_snippets) if remarks_snippets else "No notable public remarks provided."

# Recommend range inside normalized (≤ $75K target)
def propose_list_range(low, high, median, target=75_000.0):
    spread = float(high - low)
    if spread <= target:
        return float(low), float(high), False
    half = target / 2.0
    return max(float(low), float(median) - half), min(float(high), float(median) + half), True

rec_low, rec_high, wider_flag = propose_list_range(norm_low, norm_high, norm_median)

rules = """
Final Review Rules:
1) Show Raw vs Normalized ranges.
2) Recommend a list-price range INSIDE normalized; aim ≤ $75K spread.
3) If >$75K (up to $150K), justify clearly; avoid >$150K without compelling rationale.
4) Use Average Days in MLS to frame pacing.
5) Use comp remarks for qualitative nuance.
"""

prompt = f"""
You are a senior real estate pricing analyst. Produce:
- 4–7 bullets (market position, comp alignment, demand cues, risks)
- Short paragraph with strategy and recommended range

Subject Property:
- Address: {subject.get("address", "N/A")}
- Above Grade SF: {subject.get("ag_sf", "N/A")}
- Bedrooms: {subject.get("bedrooms", "N/A")}
- Bathrooms: {subject.get("bathrooms", "N/A")}
- Below Grade Finished: {subject.get("below_grade_finished", 0)}
- Below Grade Unfinished: {subject.get("below_grade_unfinished", 0)}

Valuation:
- Online Estimate Average: {money(online_avg)}
- Raw Adjusted Comp Range: {money(raw_low)} – {money(raw_high)}
- Normalized Range: {money(norm_low)} – {money(norm_high)} (median {money(norm_median)})
- Average Price Per SF: ${avg_ppsf}
- Average Days in MLS: {days_mls}

Online Estimates:
- Zillow: {money(zillow_val) if zillow_val is not None else "N/A"}
- Redfin: {money(redfin_val) if redfin_val is not None else "N/A"}
- Real AVM: {money(real_avm_val) if real_avm_val is not None else "N/A"}

Comp Remarks (snippets):
{remarks_block}

Outlier Notes:
{json.dumps(outlier_notes, indent=2)}

{rules}

Your response must:
- Recommend a range inside the normalized band: {money(rec_low)} – {money(rec_high)}
- If this still exceeds $75K, explain why it is acceptable or propose a tightened alternative.
""".strip()

st.subheader("🔎 Prompt Preview")
st.code(prompt)

# GPT call with auto-fallback
api_key = st.secrets.get("general", {}).get("openai_key", "")
gpt_commentary = None
used_fallback = False

def fallback_commentary():
    bullets = []
    bullets.append(f"Subject sits between the online estimate {money(online_avg)} and normalized band {money(norm_low)}–{money(norm_high)} (median {money(norm_median)}).")
    bullets.append(f"Average PPSF ≈ ${avg_ppsf}.")
    if str(days_mls) != "N/A":
        bullets.append(f"Average Days in MLS ≈ {days_mls}; pricing can lean higher for patient timelines, lower for faster absorption.")
    else:
        bullets.append("Average Days in MLS unavailable; consider a conservative initial stance until market feedback is clear.")
    if remarks_snippets:
        bullets.append("Comp remarks indicate notable features/upgrades; position the subject relative to these differentiators.")
    spread = rec_high - rec_low
    if spread > 75_000:
        bullets.append("Recommended range exceeds the $75K target; tighten near the median unless variability justifies width.")
    para = (
        f"Given the outlier-aware range {money(norm_low)}–{money(norm_high)}, a recommended window of "
        f"{money(rec_low)}–{money(rec_high)} balances reach and price protection. Adjust toward the lower half if showings lag the area's pace; "
        f"test the upper half if interest is brisk."
    )
    return "\n".join([f"- {b}" for b in bullets]) + "\n\n" + para

if st.button("Run Analysis and Generate Enhanced Report"):
    if api_key and OpenAI is not None:
        try:
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a senior real estate pricing analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1000
            )
            gpt_commentary = resp.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"❌ GPT call failed. Fallback will be used. Details: {e}")
            used_fallback = True
    else:
        used_fallback = True
        if not api_key:
            st.warning("No API key found; using fallback commentary.")
        elif OpenAI is None:
            st.warning("OpenAI SDK not available; using fallback commentary.")

    if used_fallback or not gpt_commentary:
        gpt_commentary = fallback_commentary()

    # Build DOCX
    doc = Document()
    title = "Enhanced Market Valuation Summary (Auto-Fallback)" if used_fallback else "Enhanced Market Valuation Summary"
    doc.add_heading(title, 0)

    # Subject
    doc.add_heading("Subject Property Summary", level=1)
    doc.add_paragraph(f"Address: {subject.get('address', 'N/A')}")
    doc.add_paragraph(f"Above Grade SF: {subject.get('ag_sf', 'N/A')}")
    doc.add_paragraph(f"Bedrooms: {subject.get('bedrooms', 'N/A')}")
    doc.add_paragraph(f"Bathrooms: {subject.get('bathrooms', 'N/A')}")
    doc.add_paragraph(f"Below Grade Finished: {subject.get('below_grade_finished', 0)}")
    doc.add_paragraph(f"Below Grade Unfinished: {subject.get('below_grade_unfinished', 0)}")

    # Valuation summary (explicit Days in MLS)
    doc.add_heading("Valuation Summary", level=1)
    doc.add_paragraph(f"Online Estimate Average: {money(online_avg)}")
    doc.add_paragraph(f"Average Price Per SF: ${avg_ppsf}")
    doc.add_paragraph(f"Average Days in MLS: {days_mls}")

    # GPT Overview
    doc.add_heading("Enhanced Property Overview", level=1)
    doc.add_paragraph(gpt_commentary)

    # Online estimates
    doc.add_heading("Online Estimates", level=1)
    est = doc.add_table(rows=4, cols=2)
    est.cell(0, 0).text = "Source"; est.cell(0, 1).text = "Value"
    est.cell(1, 0).text = "Zillow";  est.cell(1, 1).text = money(zillow_val) if zillow_val is not None else "N/A"
    est.cell(2, 0).text = "Redfin";  est.cell(2, 1).text = money(redfin_val) if redfin_val is not None else "N/A"
    est.cell(3, 0).text = "Real AVM";est.cell(3, 1).text = money(real_avm_val) if real_avm_val is not None else "N/A"

    # Adjusted comps table (with Total Adjustments)
    doc.add_heading("Adjusted Comparable Properties", level=1)
    comp_table = doc.add_table(rows=1, cols=4)
    hdrs = comp_table.rows[0].cells
    hdrs[0].text = "Address"
    hdrs[1].text = "AG SF"
    hdrs[2].text = "Total Adjustments"
    hdrs[3].text = "Adjusted Price"
    for c in comps:
        row = comp_table.add_row().cells
        row[0].text = str(c.get("full_address", ""))
        row[1].text = str(c.get("ag_sf", ""))
        ta = c.get("total_adjustments", (c.get("ag_adj", 0) + c.get("bgf_adj", 0) + c.get("bgu_adj", 0)))
        row[2].text = money(ta)
        row[3].text = money(c.get("adjusted_price", 0))

    # Ranges + recommendation
    doc.add_heading("Ranges", level=1)
    doc.add_paragraph(f"Raw Adjusted Comp Range: {money(raw_low)} – {money(raw_high)}")
    doc.add_paragraph(f"Normalized Range (outlier-aware): {money(norm_low)} – {money(norm_high)} (median {money(norm_median)})")
    if abs(raw_low - norm_low) < 1 and abs(raw_high - norm_high) < 1:
        doc.add_paragraph("Note: Normalized range equals raw range; no strong outliers were detected by the filters.")
    doc.add_heading("Recommended Market Range", level=1)
    doc.add_paragraph(f"Recommended Listing Range: {money(rec_low)} – {money(rec_high)}")
    doc.add_paragraph("Policy: Target ≤ $75K spread. Wider ranges require explicit data-based rationale; avoid > $150K unless compelling reasons exist.")

    out_name = "Enhanced_GPT_Market_Report_Fixed_JSON.docx"
    with open(out_name, "wb") as f:
        doc.save(f)
    with open(out_name, "rb") as f:
        st.download_button("📥 Download Enhanced Report (Fixed JSON Source)", f, file_name=out_name)

    st.success("✅ Enhanced report created.")
