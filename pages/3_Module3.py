
import streamlit as st

st.set_page_config(page_title="Module 3: Online Estimate Averaging", page_icon="📊")
st.title("📊 Module 3: Online Estimate Averaging")

st.markdown("Enter any or all of the following estimates:")

zillow = st.number_input("Zillow Zestimate ($)", min_value=0, step=1000, format="%i")
redfin = st.number_input("Redfin Estimate ($)", min_value=0, step=1000, format="%i")
real_avm = st.number_input("Real AVM Value ($)", min_value=0, step=1000, format="%i")

submitted = st.button("Calculate Online Estimate Average")

if submitted:
    estimates = [val for val in [zillow, redfin, real_avm] if val > 0]
    if estimates:
        avg = round(sum(estimates) / len(estimates))
        st.session_state["online_avg"] = avg  # ✅ Save for use in Module 6
        st.success(f"✅ Online Estimate Average: ${avg:,}")
    else:
        st.warning("Please enter at least one estimate.")
