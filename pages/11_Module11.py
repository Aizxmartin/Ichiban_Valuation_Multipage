import json
from pathlib import Path

import streamlit as st
from docx import Document

# OpenAI SDK v1+
try:
    from openai import OpenAI
except Exception as e:
    OpenAI = None

st.set_page_config(page_title="Module 11: GPT Market Review (v2)", page_icon="🤖")
st.title("🤖 Module 11: GPT-Based Market Commentary and Final Report (v2)")

# --- Load API key from secrets ---
api_key = st.secrets.get("general", {}).get("openai_key", "")

with st.expander("🔐 API Key Status", expanded=True):
    if api_key:
        st.success("OpenAI API key was found in secrets ✅")
        masked = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 12 else "********"
        st.write(f"Loaded key (masked): `{masked}`")
    else:
        st.error("No API key found at st.secrets['general']['openai_key']. Add it in your Streamlit Cloud Secrets.")
        st.stop()

# --- Load JSON from Module 8 ---
json_path = Path("module9_analysis.json")
if not json_path.exists():
    st.error("❌ Could not find 'module9_analysis.json'. Please run Module 8 first.")
    st.stop()

with open(json_path, "r") as f:
    summary = json.load(f)

subject = summary.get("subject_property", {})
online_avg = summary.get("online_estimate_average", 0)
adj_low, adj_high = summary.get("adjusted_price_range", [0, 0])
avg_ppsf = summary.get("average_ppsf", 0)
days_mls = summary.get("average_days_in_mls", "N/A")
comps = summary.get("comps", [])

# --- Helper: build recommended range ---
def build_recommendation_range(online_avg_val, adj_high_val):
    try:
        spread = float(adj_high_val) - float(online_avg_val)
    except Exception:
        spread = 0
    if spread > 75000:
        return f"${online_avg_val:,.0f} – ${adj_high_val:,.0f} (⚠️ Spread > $75K — qualify/justify in remarks.)"
    return f"${online_avg_val:,.0f} – ${adj_high_val:,.0f}"

# --- Build GPT Prompt ---
prompt = f"""
You are a real estate pricing analyst. Review the valuation summary and write a concise, seller-facing market overview and pricing strategy.

Subject Property:
- Address: {subject.get("address", "N/A")}
- Above Grade SF: {subject.get("ag_sf", "N/A")}
- Bedrooms: {subject.get("bedrooms", "N/A")}
- Bathrooms: {subject.get("bathrooms", "N/A")}
- Below Grade Finished: {subject.get("below_grade_finished", 0)}
- Below Grade Unfinished: {subject.get("below_grade_unfinished", 0)}

Valuation:
- Online Estimate Average: ${online_avg:,.0f}
- Adjusted Comparable Range: ${adj_low:,.0f} – ${adj_high:,.0f}
- Average Price Per SF: ${avg_ppsf}
- Average Days in MLS: {days_mls}

Guidelines:
- Summarize pricing position vs comps and online estimates.
- Comment on supply/demand momentum using only the provided data (no external claims).
- If the recommended range spread would exceed $75K, call it out and suggest how to tighten it.
- Keep the tone professional, confident, and data-driven.
Output 4–7 short bullets followed by a brief 2–3 sentence paragraph.
""".strip()

st.subheader("🔎 Prompt Preview")
st.code(prompt)

# --- Client init ---
client = None
if OpenAI is not None:
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {e}")
        st.stop()
else:
    st.error("OpenAI SDK not found. Add `openai>=1.0.0` to requirements.txt.")
    st.stop()

# --- One-time key test ---
st.markdown("### ✅ One-time Connection Test")
if st.button("Test API Key"):
    with st.spinner("Testing connection to OpenAI..."):
        try:
            test_resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Reply with 'pong' only."}
                ],
                max_tokens=5,
                temperature=0
            )
            txt = test_resp.choices[0].message.content.strip()
            if "pong" in txt.lower():
                st.success("API key works! Received response from OpenAI ✅")
            else:
                st.warning(f"Connected, but unexpected reply: {txt}")
        except Exception as e:
            st.error(f"API test failed: {e}")

# --- Generate report ---
if st.button("Run GPT Analysis and Generate Enhanced Report"):
    with st.spinner("Contacting OpenAI and generating report..."):
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a senior real estate pricing analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=900
            )
            gpt_commentary = resp.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"GPT API call failed: {e}")
            st.stop()

        # Build DOCX
        doc = Document()
        doc.add_heading("Enhanced Market Valuation Summary", 0)

        # Subject header
        doc.add_heading("Subject Property Summary", level=1)
        doc.add_paragraph(f"Address: {subject.get('address', 'N/A')}")
        doc.add_paragraph(f"Above Grade SF: {subject.get('ag_sf', 'N/A')}")
        doc.add_paragraph(f"Bedrooms: {subject.get('bedrooms', 'N/A')}")
        doc.add_paragraph(f"Bathrooms: {subject.get('bathrooms', 'N/A')}")
        doc.add_paragraph(f"Below Grade Finished: {subject.get('below_grade_finished', 0)}")
        doc.add_paragraph(f"Below Grade Unfinished: {subject.get('below_grade_unfinished', 0)}")

        # GPT Overview
        doc.add_heading("Enhanced Property Overview", level=1)
        doc.add_paragraph(gpt_commentary)

        # Online estimates table (placeholders)
        doc.add_heading("Online Estimates", level=1)
        est = doc.add_table(rows=4, cols=2)
        est.cell(0, 0).text = "Source"
        est.cell(0, 1).text = "Value"
        est.cell(1, 0).text = "Zillow"
        est.cell(2, 0).text = "Redfin"
        est.cell(3, 0).text = "Real AVM"
        est.cell(1, 1).text = "To be filled"
        est.cell(2, 1).text = "To be filled"
        est.cell(3, 1).text = "To be filled"

        # Adjusted comps (Address, AG SF, Adjusted Price)
        doc.add_heading("Adjusted Comparable Properties", level=1)
        comp_table = doc.add_table(rows=1, cols=3)
        hdrs = comp_table.rows[0].cells
        hdrs[0].text = "Address"
        hdrs[1].text = "AG SF"
        hdrs[2].text = "Adjusted Price"
        for c in comps:
            row = comp_table.add_row().cells
            row[0].text = str(c.get("full_address", ""))
            row[1].text = str(c.get("ag_sf", ""))
            row[2].text = f"${c.get('adjusted_price', 0):,}"

        # Recommended range
        doc.add_heading("Recommended Market Range", level=1)
        doc.add_paragraph(f"Online Estimate Average: ${online_avg:,.0f}")
        doc.add_paragraph(f"Adjusted Comp Range: ${adj_low:,.0f} – ${adj_high:,.0f}")
        doc.add_paragraph(f"Recommended Range: {build_recommendation_range(online_avg, adj_high)}")

        # Save & serve
        out_path = "Enhanced_GPT_Market_Report_v2.docx"
        doc.save(out_path)
        with open(out_path, "rb") as f:
            st.download_button("📥 Download Enhanced GPT Report", f, file_name=out_path)

        st.success("✅ Enhanced GPT Report Created")