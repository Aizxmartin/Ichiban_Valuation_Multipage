import streamlit as st
import json
import docx
from docx.shared import Inches
from openai import OpenAI
import os

st.title("📄 Module 11: Final GPT-Enhanced Report")

# Load summary data from Module 10
summary_file = "module10_analysis.json"

if not os.path.exists(summary_file):
    st.error(f"{summary_file} not found. Please complete Module 10 first.")
else:
    with open(summary_file, "r") as f:
        summary = json.load(f)

    # Extract relevant data
    subject_info = summary.get("subject_property", {})
    valuation_info = summary.get("valuation", {})
    comps_info = summary.get("adjusted_comparables", [])
    ranges_info = summary.get("ranges", {})
    avg_days = valuation_info.get("average_days_in_mls", "N/A")

    st.subheader("Valuation Snapshot")
    st.write(f"**Online Estimate Average:** {valuation_info.get('online_estimate_average', 'N/A')}")
    st.write(f"**Average Price per SF:** {valuation_info.get('average_ppsf', 'N/A')}")
    st.write(f"**Average Days in MLS:** {avg_days}")

    # GPT API Call
    client = OpenAI(api_key=st.secrets["general"]["openai_key"])

    gpt_prompt = f"""You are a real estate pricing analyst. Your job is to review a property valuation summary and write a market overview and pricing strategy.

Subject Property:
Address: {subject_info.get('address', 'N/A')}
Above Grade SF: {subject_info.get('above_grade_sf', 'N/A')}
Bedrooms: {subject_info.get('bedrooms', 'N/A')}
Bathrooms: {subject_info.get('bathrooms', 'N/A')}
Below Grade Finished: {subject_info.get('below_grade_finished', 'N/A')}
Below Grade Unfinished: {subject_info.get('below_grade_unfinished', 'N/A')}

Valuation:
Online Estimate Average: {valuation_info.get('online_estimate_average', 'N/A')}
Adjusted Comparable Range: {ranges_info.get('raw_adjusted', 'N/A')}
Average Price Per SF: {valuation_info.get('average_ppsf', 'N/A')}
Average Days in MLS: {avg_days}

Guidelines:
- Summarize property pricing position based on data.
- Include narrative about supply/demand, pricing momentum, and typical buyer perception.
- Mention if $75K spread is exceeded and provide rationale.
- Keep it professional, informative, and seller-focused.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional real estate market analyst."},
                {"role": "user", "content": gpt_prompt}
            ],
            temperature=0.3
        )
        gpt_analysis = response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"GPT API call failed: {e}")
        gpt_analysis = "GPT analysis unavailable due to API error."

    # DOCX generation
    doc = docx.Document()
    doc.add_heading("Enhanced Market Valuation Summary", level=1)

    doc.add_heading("Subject Property Summary", level=2)
    for k, v in subject_info.items():
        doc.add_paragraph(f"{k.replace('_', ' ').title()}: {v}")

    doc.add_heading("Enhanced Property Overview", level=2)
    doc.add_paragraph(gpt_analysis)

    doc.add_heading("Online Estimates", level=2)
    table = doc.add_table(rows=1, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Source"
    hdr_cells[1].text = "Value"
    for src in ["Zillow", "Redfin", "Real AVM"]:
        row_cells = table.add_row().cells
        row_cells[0].text = src
        row_cells[1].text = str(valuation_info.get(src.lower(), "N/A"))

    doc.add_heading("Adjusted Comparable Properties", level=2)
    table = doc.add_table(rows=1, cols=4)
    hdr_cells = table.rows[0].cells
    hdr_cells[:] = ["Address", "AG SF", "Total Adjustments", "Adjusted Price"]
    for comp in comps_info:
        row_cells = table.add_row().cells
        row_cells[0].text = str(comp.get("address", ""))
        row_cells[1].text = str(comp.get("ag_sf", ""))
        row_cells[2].text = str(comp.get("total_adjustments", ""))
        row_cells[3].text = str(comp.get("adjusted_price", ""))

    doc.add_heading("Ranges", level=2)
    doc.add_paragraph(f"Raw Adjusted Comp Range: {ranges_info.get('raw_adjusted', 'N/A')}")
    doc.add_paragraph(f"Normalized Range (outlier-aware): {ranges_info.get('normalized', 'N/A')}")
    doc.add_paragraph(f"Recommended Market Range: {ranges_info.get('recommended', 'N/A')}")
    doc.add_paragraph(f"Average Days in MLS: {avg_days}")

    output_path = "enhanced_market_valuation_summary.docx"
    doc.save(output_path)
    st.success("Report generated successfully.")
    with open(output_path, "rb") as f:
        st.download_button("📥 Download DOCX Report", f, file_name=output_path)
