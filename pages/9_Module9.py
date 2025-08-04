import streamlit as st
import json
from openai import OpenAI
from docx import Document
from docx.shared import Inches

st.set_page_config(page_title="Module 9: GPT Review & Market Report Generator", layout="wide")
st.title("🧠 Module 9: GPT Review & Market Report Generator")

# Load JSON summary from Module 8
json_path = Path("module8_summary.json")
if not json_path.exists():
    st.error("❌ 'module8_summary.json' not found. Please complete Module 8 first.")
    st.stop()

with open(json_path, "r") as f:
    summary = json.load(f)

# Display subject and summary info
st.subheader("📍 Subject Property")
sp = summary["subject_property"]
st.markdown(f"**Address**: {sp['address']}")
st.markdown(f"**Above Grade SF**: {sp['above_grade_sf']} | **Bedrooms**: {sp['bedrooms']} | **Bathrooms**: {sp['bathrooms']}")

st.subheader("📊 Valuation Summary")
st.markdown(f"**Online Estimate Average**: ${summary['online_estimate_average']:,}")
low, high = summary["adjusted_price_range"]
st.markdown(f"**Adjusted Comp Range**: ${low:,}–${high:,}")
st.markdown(f"**Average Price per SF**: ${summary['average_ppsf']}")
if summary["average_days_in_mls"]:
    st.markdown(f"**Average Days in MLS**: {summary['average_days_in_mls']}")

# GPT-4 Review
client = OpenAI()
with st.spinner("🧠 Reviewing with GPT-4..."):
    comp_summary = "\n".join([
        f"{c['full_address']} | AG SF: {c['ag_sf']} | Net: ${c['net_price']:,} | Adjusted: ${c['adjusted_price']:,}\nRemarks: {c.get('public_remarks', '')[:200]}"
        for c in summary["comps"]
    ])

    messages = [{
        "role": "user",
        "content": f"""You are a valuation analyst. Review the following:
- Subject: {sp}
- Online Average: ${summary['online_estimate_average']:,}
- Adjusted Price Range: ${low:,} – ${high:,}
- Comp Data:
{comp_summary}

Tasks:
1. Check if price adjustments are logical.
2. Flag outliers.
3. Comment on pricing consistency.
4. Include average Days in MLS.
5. Extract any notable comp remarks.
6. Final recommendation: Keep range, go higher, or go lower? Explain.

Give a concise market summary as bullet points followed by a pricing recommendation.
"""}]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.4,
    )

    gpt_analysis = response.choices[0].message.content

# Show GPT analysis
st.subheader("📝 GPT Summary")
st.text_area("GPT Review", value=gpt_analysis, height=300)

# Export to DOCX
def generate_docx():
    doc = Document()
    doc.add_heading("Ichiban Market Ranger Report", 0)

    doc.add_heading("Subject Property", level=1)
    doc.add_paragraph(f"Address: {sp['address']}")
    doc.add_paragraph(f"Above Grade SF: {sp['above_grade_sf']} | Bedrooms: {sp['bedrooms']} | Bathrooms: {sp['bathrooms']}")

    doc.add_heading("Valuation Summary", level=1)
    doc.add_paragraph(f"Online Estimate Average: ${summary['online_estimate_average']:,}")
    doc.add_paragraph(f"Adjusted Comp Range: ${low:,}–${high:,}")
    doc.add_paragraph(f"Average PPSF: ${summary['average_ppsf']}")
    if summary["average_days_in_mls"]:
        doc.add_paragraph(f"Average Days in MLS: {summary['average_days_in_mls']}")

    doc.add_heading("GPT Market Analysis", level=1)
    doc.add_paragraph(gpt_analysis)

    output_path = Path("Ichiban_Market_Ranger_Report.docx")
    doc.save(output_path)
    return output_path

if st.button("📄 Export GPT Summary to DOCX"):
    output_file = generate_docx()
    with open(output_file, "rb") as f:
        st.download_button("📥 Download Ichiban Market Ranger Report", f, file_name=output_file.name)