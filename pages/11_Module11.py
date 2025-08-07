import streamlit as st
import json
import openai
from docx import Document
from pathlib import Path

st.set_page_config(page_title="Module 11: GPT Market Review", page_icon="🤖")
st.title("🤖 Module 11: GPT-Based Market Commentary and Final Report")

# Load API key securely
openai.api_key = st.secrets.get("openai_key", "")

# Load JSON data
json_path = Path("module9_analysis.json")
if not json_path.exists():
    st.error("❌ Could not find 'module9_analysis.json'. Please run Module 8 first.")
    st.stop()

with open(json_path, "r") as f:
    summary = json.load(f)

subject = summary["subject_property"]
online_avg = summary["online_estimate_average"]
adj_low, adj_high = summary["adjusted_price_range"]
avg_ppsf = summary["average_ppsf"]
days_mls = summary.get("average_days_in_mls", "N/A")
comps = summary["comps"]

# Limit recommended range to 75K unless justified
def build_recommendation_range(online_avg, adj_high):
    if adj_high - online_avg > 75000:
        return f"${online_avg:,} – ${adj_high:,} (⚠️ Note: this spread exceeds $75K. Consider refining pricing strategy.)"
    else:
        return f"${online_avg:,} – ${adj_high:,}"

# Build GPT prompt
prompt = f'''
You are a real estate pricing analyst. Your job is to review a property valuation summary and write a market overview and pricing strategy.

Subject Property:
- Address: {subject.get("address", "N/A")}
- Above Grade SF: {subject.get("ag_sf", "N/A")}
- Bedrooms: {subject.get("bedrooms", "N/A")}
- Bathrooms: {subject.get("bathrooms", "N/A")}
- Below Grade Finished: {subject.get("below_grade_finished", 0)}
- Below Grade Unfinished: {subject.get("below_grade_unfinished", 0)}

Valuation:
- Online Estimate Average: ${online_avg:,}
- Adjusted Comparable Range: ${adj_low:,} – ${adj_high:,}
- Average Price Per SF: ${avg_ppsf}
- Average Days in MLS: {days_mls}

Guidelines:
- Summarize property pricing position based on data.
- Include narrative about supply/demand, pricing momentum, and typical buyer perception.
- Mention if $75K spread is exceeded and provide rationale.
- Keep it professional, informative, and seller-focused.

Begin your commentary below:
'''

st.subheader("🔎 Prompt Preview")
st.code(prompt, language="markdown")

if st.button("Run GPT Analysis and Generate Report"):
    with st.spinner("Contacting ChatGPT and generating report..."):
        try:
            # Run GPT call
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            gpt_commentary = response.choices[0].message.content.strip()

            # Save to Word doc
            doc = Document()
            doc.add_heading("Enhanced Market Valuation Summary", 0)

            doc.add_heading("Subject Property Summary", level=1)
            doc.add_paragraph(f"Address: {subject.get('address', 'N/A')}")
            doc.add_paragraph(f"Above Grade SF: {subject.get('ag_sf', 'N/A')}")
            doc.add_paragraph(f"Bedrooms: {subject.get('bedrooms', 'N/A')}")
            doc.add_paragraph(f"Bathrooms: {subject.get('bathrooms', 'N/A')}")

            doc.add_heading("Enhanced Property Overview", level=1)
            doc.add_paragraph(gpt_commentary)

            doc.add_heading("Online Estimates", level=1)
            table = doc.add_table(rows=4, cols=2)
            table.cell(0, 0).text = "Source"
            table.cell(0, 1).text = "Value"
            table.cell(1, 0).text = "Zillow"
            table.cell(2, 0).text = "Redfin"
            table.cell(3, 0).text = "Real AVM"
            table.cell(1, 1).text = "To be filled"
            table.cell(2, 1).text = "To be filled"
            table.cell(3, 1).text = "To be filled"

            doc.add_heading("Adjusted Comparable Properties", level=1)
            comp_table = doc.add_table(rows=1, cols=3)
            hdrs = comp_table.rows[0].cells
            hdrs[0].text = "Address"
            hdrs[1].text = "AG SF"
            hdrs[2].text = "Adjusted Price"
            for c in comps:
                row = comp_table.add_row().cells
                row[0].text = c.get("full_address", "")
                row[1].text = str(c.get("ag_sf", ""))
                row[2].text = f"${c.get('adjusted_price', 0):,}"

            doc.add_heading("Recommended Market Range", level=1)
            doc.add_paragraph(f"Online Estimate Average: ${online_avg:,}")
            doc.add_paragraph(f"Adjusted Comp Range: ${adj_low:,} – ${adj_high:,}")
            doc.add_paragraph(f"Recommended Range: {build_recommendation_range(online_avg, adj_high)}")

            # Save and serve
            final_path = "Enhanced_GPT_Market_Report.docx"
            doc.save(final_path)
            with open(final_path, "rb") as f:
                st.download_button("📥 Download Enhanced GPT Report", f, file_name=final_path)

            st.success("✅ Enhanced GPT Report Created")
        except Exception as e:
            st.error(f"❌ GPT API call failed: {e}")
