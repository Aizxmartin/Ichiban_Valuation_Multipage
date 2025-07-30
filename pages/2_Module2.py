import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="Module 2: Subject Property Details", page_icon="🏠")
st.title("🏠 Module 2: Subject Property Details")

# Upload PDF
uploaded_pdf = st.file_uploader("Upload Subject Property PDF", type=["pdf"])

# Extract text if PDF is uploaded
extracted_text = ""
if uploaded_pdf:
    with fitz.open(stream=uploaded_pdf.read(), filetype="pdf") as doc:
        for page in doc:
            extracted_text += page.get_text()

# Manual Entry Inputs (Default)
st.subheader("Review or Manually Complete Extracted Info:")
address = st.text_input("Address", "")
ag_sf = st.number_input("Above Grade SF", min_value=0)
bedrooms = st.number_input("Bedrooms", min_value=0, step=1)
bathrooms = st.number_input("Bathrooms", min_value=0, step=1)

# Save to session state
if st.button("Save Subject Property Info"):
    subject_data = {
        "address": address,
        "ag_sf": ag_sf,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
    }
    st.session_state["subject_data"] = subject_data
    st.success("✅ Subject Property Data Saved to Session")
    st.json(subject_data)
