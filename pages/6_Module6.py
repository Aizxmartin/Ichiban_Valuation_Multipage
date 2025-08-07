import streamlit as st

st.set_page_config(page_title="Module 6: Subject Basement Details", page_icon="🏗️")
st.title("🏗️ Module 6: Enter Basement Information")

if "subject_data" not in st.session_state:
    st.error("❌ Please complete Module 2 first to enter basic subject property info.")
    st.stop()

# Retrieve and expand subject data
subject = st.session_state.subject_data

bgf = st.number_input("Below Grade Finished SF", min_value=0, value=subject.get("below_grade_finished", 0))
bgu = st.number_input("Below Grade Unfinished SF", min_value=0, value=subject.get("below_grade_unfinished", 0))

# Save updated subject data
subject["below_grade_finished"] = bgf
subject["below_grade_unfinished"] = bgu
st.session_state["subject_data"] = subject

st.success("✅ Subject Basement Info Updated")
st.json(subject)