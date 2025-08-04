
import streamlit as st
import json
from docx import Document
from io import BytesIO

st.set_page_config(page_title="Module 9: Ichiban Market Ranger Report", layout="wide")
st.title("🧠 Module 9: Generate Final Report")

# Load summary JSON from Module 8
try:
    with open("module8_summary.json", "r") as f:
        summary = json.load(f)
except FileNotFoundError:
    st.error("❌ 'module8_summary.json' not found. Please complete Module 8.")
    st.stop()

# Start creating DOCX
doc = Document()
doc.add_heading("Ichiban Market Ranger Report", 0)

# Subject Property Section
sp = summary["subject_property"]
doc.add_heading("🏠 Subject Property", level=1)
doc.add_paragraph(f"Address: {sp['address']}")
doc.add_paragraph(f"Above Grade SF: {sp['above_grade_sf']} | Bedrooms: {sp['bedrooms']} | Bathrooms: {sp['bathrooms']}")

# Valuation Summary
doc.add_heading("📊 Valuation Summary", level=1)
doc.add_paragraph(f"Online Estimate Average: ${summary['online_estimate_average']:,}")
low, high = summary["adjusted_price_range"]
doc.add_paragraph(f"Adjusted Comp Range: ${low:,} – ${high:,}")
doc.add_paragraph(f"Average Price per SF: ${summary['average_ppsf']:,}")
doc.add_paragraph(f"Average Days in MLS: {summary['average_days_in_mls']}")

# Adjusted Comps Table
doc.add_heading("🏘️ Adjusted Comparable Sales", level=1)
table = doc.add_table(rows=1, cols=10)
hdr_cells = table.rows[0].cells
headers = ["Address", "AG SF", "Net Price", "AG Adj", "BGF Adj", "BGU Adj", "Total Adj", "Adj Price", "Days MLS", "Public Remarks"]
for i, h in enumerate(headers):
    hdr_cells[i].text = h

for comp in summary["comps"]:
    row_cells = table.add_row().cells
    row_cells[0].text = comp.get("full_address", "")
    row_cells[1].text = str(comp.get("ag_sf", ""))
    row_cells[2].text = f"${comp.get('net_price', 0):,}"
    row_cells[3].text = f"{comp.get('ag_adj', 0):,}"
    row_cells[4].text = f"{comp.get('bgf_adj', 0):,}"
    row_cells[5].text = f"{comp.get('bgu_adj', 0):,}"
    row_cells[6].text = f"{comp.get('total_adjustments', 0):,}"
    row_cells[7].text = f"${comp.get('adjusted_price', 0):,}"
    row_cells[8].text = str(comp.get("days_in_mls", "N/A"))
    row_cells[9].text = comp.get("public_remarks", "")[:300] + "..."

# Save DOCX and allow download
buffer = BytesIO()
doc.save(buffer)
st.success("✅ Report successfully created.")

st.download_button(
    label="📥 Download Ichiban Market Ranger Report (.docx)",
    data=buffer.getvalue(),
    file_name="Ichiban_Market_Ranger_Report_Module9.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
