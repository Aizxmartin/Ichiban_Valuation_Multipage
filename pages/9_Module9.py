import streamlit as st
import json
from pathlib import Path
import openai
import os

st.set_page_config(page_title="Module 9: GPT Review", layout="wide")
st.title("🧠 Module 9: GPT Review & Market Summary Generator")

# Load JSON summary from Module 8
json_path = Path("module8_summary.json")
if not json_path.exists():
    st.error("module8_summary.json not found. Please complete Module 8 first.")
    st.stop()

with open(json_path, "r") as f:
    summary_data = json.load(f)

# Construct prompt
subject = summary_data["subject_property"]
comps = summary_data["comps"]
remarks = [c.get("public_remarks", "") for c in comps if c.get("public_remarks")]
days_list = [c.get("days_in_mls") for c in comps if isinstance(c.get("days_in_mls"), (int, float))]

prompt = f"""
You are an expert real estate valuation analyst. Review the following market data and provide a clear assessment with:
1. Price consistency analysis and outlier detection
2. Days in MLS commentary
3. Summary of notable remarks
4. Your opinion on pricing confidence (stay, increase, or decrease)

Subject Property:
- Address: {subject["address"]}
- Above Grade SF: {subject["above_grade_sf"]}
- Bedrooms: {subject["bedrooms"]}
- Bathrooms: {subject["bathrooms"]}

Online Estimate Average: ${summary_data["online_estimate_average"]:,}
Adjusted Price Range: {summary_data["adjusted_price_range"]}
Average PPSF: ${summary_data["average_ppsf"]}

Average Days in MLS: {round(sum(days_list)/len(days_list), 1) if days_list else "N/A"}

Public Remarks:
{chr(10).join(remarks)}
"""

st.subheader("AI Market Review Summary")
if "openai_api_key" not in st.secrets:
    st.error("Please set your OpenAI API key in Streamlit secrets.")
    st.stop()

openai.api_key = st.secrets["openai_api_key"]

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a real estate valuation expert."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7
)

analysis = response.choices[0].message.content.strip()
st.text_area("GPT Review Output", analysis, height=300)

# Save new analysis file
summary_data["gpt_review"] = analysis
with open("module9_analysis.json", "w") as f:
    json.dump(summary_data, f, indent=2)

st.success("✅ Enhanced analysis saved to 'module9_analysis.json'")
