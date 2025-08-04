
import streamlit as st
import json
from pathlib import Path
from docx import Document

st.set_page_config(page_title="🧠 Module 9: GPT Review & Market Report Generator", layout="wide")
st.title("🧠 Module 9: GPT Review & Market Report Generator")

json_path = Path("module8_summary.json")

if not json_path.exists():
    st.error("module8_summary.json not found. Please complete Module 8 first.")
    st.stop()

with open(json_path, "r") as f:
    summary = json.load(f)

doc = Document()
doc.add_heading("Ichiban Market Ranger – Enhanced Valuation Summary", level=1)

sp = summary["subject_property"]
doc.add_heading("Subject Property", level=2)
doc.add_paragraph(f"Address: {sp['address']}")
doc.add_paragraph(f"Above Grade SF: {sp['above_grade_sf']} | Bedrooms: {sp['bedrooms']} | Bathrooms: {sp['bathrooms']}")

doc.add_heading("Valuation Summary", level=2)
doc.add_paragraph(f"Online Estimate Average: ${summary['online_estimate_average']:,}")
low, high = summary["adjusted_price_range"]
doc.add_paragraph(f"Adjusted Comp Range: ${low:,} – ${high:,}")
doc.add_paragraph(f"Average Price per SF: ${summary['average_ppsf']}")
days = summary.get("average_days_in_mls", "N/A")
doc.add_paragraph(f"Average Days in MLS: {days if days != None else 'N/A'}")

doc.add_heading("Adjusted Comparable Sales", level=2)
table = doc.add_table(rows=1, cols=9)
hdr_cells = table.rows[0].cells
headers = ["Address", "AG SF", "Net Price", "AG Adj", "BGF Adj", "BGU Adj", "Total Adj", "Adjusted Price", "Days MLS"]
for i, h in enumerate(headers):
    hdr_cells[i].text = h

for comp in summary["comps"]:
    row_cells = table.add_row().cells
    row_cells[0].text = str(comp.get("full_address", ""))
    row_cells[1].text = str(comp.get("ag_sf", ""))
    row_cells[2].text = f"${comp.get('net_price', 0):,}"
    row_cells[3].text = f"{comp.get('ag_adj', 0):,}"
    row_cells[4].text = f"{comp.get('bgf_adj', 0):,}"
    row_cells[5].text = f"{comp.get('bgu_adj', 0):,}"
    row_cells[6].text = f"{comp.get('total_adjustments', 0):,}"
    row_cells[7].text = f"${comp.get('adjusted_price', 0):,}"
    row_cells[8].text = str(comp.get("days_in_mls", "N/A"))

doc_path = "/mnt/data/Ichiban_Market_Summary_Module9.docx"
doc.save(doc_path)

st.success("✅ Market summary report generated successfully.")
st.download_button("📥 Download Market Summary DOCX", data=open(doc_path, "rb"), file_name="Ichiban_Market_Summary.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
