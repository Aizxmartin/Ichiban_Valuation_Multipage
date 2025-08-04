import streamlit as st
import openai
import json
from pathlib import Path

st.set_page_config(page_title="Module 9: GPT Review", layout="wide")
st.title("🧠 Module 9: GPT Review & Market Report Generator")

json_path = Path("module8_summary.json")
if not json_path.exists():
    st.error("❌ Could not find 'module8_summary.json'. Please run Module 8 first.")
    st.stop()

with open(json_path, "r") as f:
    summary_data = json.load(f)

# GPT review prompt
system_prompt = "You are a real estate valuation expert."
user_prompt = f"""
Please analyze this market valuation summary and provide insights:
1. Review pricing consistency.
2. Identify any large comp value outliers.
3. Analyze average Days in MLS.
4. Summarize notable remarks from comps.
5. Flag inconsistencies or suggested notes.
6. Confirm if the price range is reasonable or should shift up/down.

JSON Summary:
{json.dumps(summary_data)}
"""

with st.spinner("Running GPT analysis..."):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

gpt_review = response.choices[0].message.content
st.subheader("📋 GPT Market Commentary")
st.markdown(gpt_review)

# Save result for next module
with open("gpt_review.txt", "w") as f:
    f.write(gpt_review)

st.success("✅ GPT analysis saved to gpt_review.txt")
