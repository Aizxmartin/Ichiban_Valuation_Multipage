import streamlit as st
import json
from docx import Document

st.set_page_config(page_title="Module 9: Market Report", page_icon="📄")
st.title("📄 Module 9: Generate Market Report (.docx)")

try:
    with open("module9_analysis.json", "r") as f:
        data = json.load(f)
except FileNotFoundError:
    st.error("❌ module9_analysis.json not found. Please complete Module 8 first.")
    st.stop()

doc = Document()
doc.add_heading("Ichiban Market Valuation Report", 0)

sp = data["subject_property"]
doc.add_heading("Subject Property", level=1)
doc.add_paragraph(f"Address: {sp['address']}")
doc.add_paragraph(f"Above Grade SF: {sp['ag_sf']} | Bedrooms: {sp['bedrooms']} | Bathrooms: {sp['bathrooms']}")
doc.add_paragraph(f"BGF: {sp.get('below_grade_finished', 0)} | BGU: {sp.get('below_grade_unfinished', 0)}")

doc.add_heading("Valuation Summary", level=1)
doc.add_paragraph(f"Online Estimate Average: ${data['online_estimate_average']:,}")
doc.add_paragraph(f"Adjusted Comp Range: ${data['adjusted_price_range'][0]:,} – ${data['adjusted_price_range'][1]:,}")
doc.add_paragraph(f"Average PPSF: ${data['average_ppsf']:,}")
doc.add_paragraph(f"Average Days in MLS: {data['average_days_in_mls']}")

doc.add_heading("GPT Market Commentary", level=1)
doc.add_paragraph(data.get("gpt_review", "No commentary available."))

doc.add_heading("Adjusted Comparable Sales", level=1)
table = doc.add_table(rows=1, cols=8)
hdr_cells = table.rows[0].cells
headers = ["Address", "AG SF", "Net Price", "AG Adj", "BGF Adj", "BGU Adj", "Total Adj", "Adjusted Price"]
for i, header in enumerate(headers):
    hdr_cells[i].text = header

for c in data["comps"]:
    row = table.add_row().cells
    row[0].text = c["full_address"]
    row[1].text = str(c["ag_sf"])
    row[2].text = f"${c['net_price']:,}"
    row[3].text = f"${c.get('ag_adj', 0):,}"
    row[4].text = f"${c.get('bgf_adj', 0):,}"
    row[5].text = f"${c.get('bgu_adj', 0):,}"
    row[6].text = f"${c['total_adjustments']:,}"
    row[7].text = f"${c['adjusted_price']:,}"

output_path = "Ichiban_Final_Report.docx"
doc.save(output_path)
st.success("✅ Report Created")
with open(output_path, "rb") as f:
    st.download_button("📥 Download Report", f, file_name=output_path)