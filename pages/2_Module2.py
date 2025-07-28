import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="Module 2: Subject Property", page_icon="🏠")
st.title("🏠 Module 2: Subject Property Details")

def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def parse_subject_data(text):
    data = {}
    match = re.search(r"(\d{3,5}\s+\w+\s+\w+\s+(St|Ave|Blvd|Rd|Dr).+)", text)
    if match:
        data["address"] = match.group(1).strip()
    sf_match = re.search(r"(Finished Area|Bldg Sq Ft)[^\d]*(\d{3,5})", text)
    if sf_match:
        data["ag_sf"] = int(sf_match.group(2))
    bed_match = re.search(r"Beds?:?\s+(\d+)", text)
    if bed_match:
        data["bedrooms"] = int(bed_match.group(1))
    bath_match = re.search(r"(Full Baths|Bathrooms):?\s*(\d+)", text)
    if bath_match:
        data["bathrooms"] = int(bath_match.group(2))
    return data

uploaded_pdf = st.file_uploader("Upload Subject Property PDF", type=["pdf"])
subject_data = {}

if uploaded_pdf:
    text = extract_text_from_pdf(uploaded_pdf)
    parsed = parse_subject_data(text)

    st.subheader("Review or Manually Complete Extracted Info:")
    subject_data["address"] = parsed.get("address", st.text_input("Address", ""))
    subject_data["ag_sf"] = parsed.get("ag_sf", st.number_input("Above Grade SF", min_value=0))
    subject_data["bedrooms"] = parsed.get("bedrooms", st.number_input("Bedrooms", min_value=0, step=1))
    subject_data["bathrooms"] = parsed.get("bathrooms", st.number_input("Bathrooms", min_value=0, step=1))

    st.session_state['subject_data'] = subject_data

    st.success("Subject Property Data Saved to Session")
    st.json(subject_data)
