
import streamlit as st
import json
from docx import Document
from docx.shared import Inches
import datetime

st.set_page_config(page_title="Module 9: GPT Review & Market Report Generator", layout="wide")

st.title("🧠 Module 9: GPT Review & Market Report Generator")

# Load the JSON summary
json_path = Path("module8_summary.json")
if not json_path.exists():
    st.error("❌ 'module8_summary.json' not found. Please run Module 8 first.")
    st.stop()

with open(json_path, "r") as f:
    summary = json.load(f)

# Create DOCX report
doc = Document()
doc.add_heading("Ichiban Market Ranger™ - Enhanced Valuation Summary", 0)
doc.add_paragraph(f"📅 Report Date: {datetime.date.today()}")

# Subject Property Section
sp = summary["subject_property"]
doc.add_heading("🏠 Subject Property", level=1)
doc.add_paragraph(f"Address: {sp['address']}")
doc.add_paragraph(f"Above Grade SF: {sp['above_grade_sf']} | Bedrooms: {sp['bedrooms']} | Bathrooms: {sp['bathrooms']}")

# Valuation Summary
doc.add_heading("📊 Valuation Summary", level=2)
doc.add_paragraph(f"Online Estimate Average: ${summary['online_estimate_average']:,}")
low, high = summary["adjusted_price_range"]
doc.add_paragraph(f"Adjusted Comp Range: ${low:,} – ${high:,}")
doc.add_paragraph(f"Average Price per SF: ${summary['average_ppsf']}")
doc.add_paragraph(f"Average Days in MLS: {summary.get('average_days_in_mls', 'N/A')}")

# Adjusted Comp Table
doc.add_heading("🏘️ Adjusted Comparable Sales", level=2)
table = doc.add_table(rows=1, cols=9)
hdr_cells = table.rows[0].cells
hdr_cells[0].text = "Address"
hdr_cells[1].text = "AG SF"
hdr_cells[2].text = "Net Price"
hdr_cells[3].text = "AG Adj"
hdr_cells[4].text = "BGF Adj"
hdr_cells[5].text = "BGU Adj"
hdr_cells[6].text = "Total Adj"
hdr_cells[7].text = "Adj Price"
hdr_cells[8].text = "Days MLS"

for comp in summary["comps"]:
    row = table.add_row().cells
    row[0].text = str(comp["full_address"])
    row[1].text = str(comp["ag_sf"])
    row[2].text = f"${comp['net_price']:,}"
    row[3].text = f"{comp.get('ag_adj', 0):,}"
    row[4].text = f"{comp.get('bgf_adj', 0):,}"
    row[5].text = f"{comp.get('bgu_adj', 0):,}"
    row[6].text = f"{comp.get('total_adjustments', 0):,}"
    row[7].text = f"${comp['adjusted_price']:,}"
    row[8].text = str(comp.get("days_in_mls", "N/A"))

# Save file
output_path = "/mnt/data/Ichiban_Market_Ranger_Report.docx"
doc.save(output_path)
st.success("✅ Report generated!")
st.download_button("⬇️ Download DOCX", data=open(output_path, "rb"), file_name="Ichiban_Market_Ranger_Report.docx")
