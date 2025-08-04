
import streamlit as st
import json
from pathlib import Path
from docx import Document

st.title("🧠 Module 9: GPT Review & Market Report Generator")

json_path = Path("module8_summary.json")
if not json_path.exists():
    st.error("module8_summary.json not found. Run Module 8 first.")
    st.stop()

with open(json_path, "r") as f:
    summary = json.load(f)

sp = summary["subject_property"]
doc = Document()
doc.add_heading("Ichiban Market Ranger Report", 0)

# Subject Property Summary
doc.add_heading("🏠 Subject Property", level=1)
doc.add_paragraph(f"Address: {sp['address']}")
doc.add_paragraph(f"Above Grade SF: {sp['above_grade_finished']} | Bedrooms: {sp['bedrooms']} | Bathrooms: {sp['bathrooms']}")

# Valuation Summary
doc.add_heading("📊 Valuation Summary", level=1)
doc.add_paragraph(f"Online Estimate Average: ${summary['online_estimate_average']:,}")
doc.add_paragraph(f"Adjusted Comp Range: {summary['adjusted_price_range'][0]:,}–{summary['adjusted_price_range'][1]:,}")
doc.add_paragraph(f"Average Price per SF: ${summary['average_ppsf']}")
doc.add_paragraph(f"Average Days in MLS: {summary.get('average_days_in_mls', 'N/A')}")

# Save DOCX
doc_path = Path("Ichiban_Market_Ranger_Report.docx")
doc.save(doc_path)

st.success("✅ DOCX report generated.")
with open(doc_path, "rb") as file:
    st.download_button("📥 Download Market Report", file, file_name=doc_path.name)
