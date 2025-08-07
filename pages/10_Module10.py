import streamlit as st
import json

st.set_page_config(page_title="Module 10: Review JSON", page_icon="🧾")
st.title("🧾 Module 10: Review Valuation JSON")

try:
    with open("module9_analysis.json", "r") as f:
        data = json.load(f)
    st.json(data)
except Exception as e:
    st.error(f"Error reading JSON: {e}")