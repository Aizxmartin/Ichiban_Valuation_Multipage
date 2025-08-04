
import streamlit as st
import json
from docx import Document
from docx.shared import Pt

st.set_page_config(page_title="Module 9: AI Review & DOCX Export", layout="wide")
st.title("🧠 Module 9: GPT Review & Market Report Generator")

# Load the JSON file
try:
    with open("module8_summary.json", "r") as f:
        summary = json.load(f)
except FileNotFoundError:
    st.error("❌ JSON summary file not found. Please complete Module 8 first.")
    st.stop()

# --- Begin Report Composition ---
doc = Document()

# Title
doc.add_heading("Ichiban Market Ranger™", level=1)
doc.add_paragraph("GPT-Enhanced Market Valuation Summary Report", style="Intense Quote")

# Subject Property
sp = summary["subject_property"]
doc.add_heading("📍 Subject Property", level=2)
doc.add_paragraph(f"Address: {sp['address']}")
doc.add_paragraph(f"Above Grade SF: {sp['ag_sf']} | Bedrooms: {sp['bedrooms']} | Bathrooms: {sp['bathrooms']}")

# Valuation Summary
doc.add_heading("📊 Valuation Summary", level=2)
doc.add_paragraph(f"Online Estimate Average: ${summary['online_avg']:,}")
doc.add_paragraph(f"Adjusted Price Range: ${summary['adjusted_range']['low']:,} – ${summary['adjusted_range']['high']:,}")
doc.add_paragraph(f"Average Price per SF: ${summary['average_ppsf']}")
doc.add_paragraph(f"Average Days in MLS: {summary['average_days_in_mls']}")

# Adjusted Comps Table
doc.add_heading("🏘️ Adjusted Comparable Sales", level=2)
table = doc.add_table(rows=1, cols=9)
table.style = 'Light Grid Accent 1'
hdr_cells = table.rows[0].cells
hdr_cells[0].text = 'Address'
hdr_cells[1].text = 'AG SF'
hdr_cells[2].text = 'Net Price'
hdr_cells[3].text = 'AG Adj'
hdr_cells[4].text = 'BGF Adj'
hdr_cells[5].text = 'BGU Adj'
hdr_cells[6].text = 'Total Adj'
hdr_cells[7].text = 'Final Price'
hdr_cells[8].text = 'Days in MLS'

for comp in summary["comps"]:
    row = table.add_row().cells
    row[0].text = str(comp.get("full_address", ""))
    row[1].text = str(comp.get("ag_sf", ""))
    row[2].text = f"${comp.get('net_price', 0):,}"
    row[3].text = f"{comp.get('ag_adj', 0):,.0f}"
    row[4].text = f"{comp.get('bgf_adj', 0):,.0f}"
    row[5].text = f"{comp.get('bgu_adj', 0):,.0f}"
    row[6].text = f"{comp.get('total_adjustments', 0):,.0f}"
    row[7].text = f"${comp.get('adjusted_price', 0):,}"
    row[8].text = str(comp.get("Days in MLS", "N/A"))

# Public Remarks Summary
doc.add_heading("📝 Notable Remarks", level=2)
for comp in summary["comps"]:
    remarks = comp.get("Public Remarks", "")
    if remarks:
        doc.add_paragraph(f"{comp.get('full_address', '')}: {remarks}", style="List Bullet")

# Final Advisory Note
doc.add_heading("📣 GPT Advisory Summary", level=2)
doc.add_paragraph(
    "The suggested price range is intended to support strategic decision-making when listing your home. "
    "The lower end of the range reflects conservative pricing aligned with broader market averages. The higher end includes premiums for superior condition or features. "
    "If the price range exceeds $75,000, agents should explain any outliers due to location, updates, or adjustments. "
    "Days on MLS provides insight into demand trends, but your agent’s pricing and positioning strategy will impact results."
)

# Save and Download
doc_path = "Ichiban_Enhanced_Valuation_Report.docx"
doc.save(doc_path)
with open(doc_path, "rb") as f:
    st.download_button("📥 Download Final DOCX Report", f, file_name=doc_path, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

st.success("✅ GPT-enhanced valuation report created.")
