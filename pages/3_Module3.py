
import streamlit as st

st.set_page_config(page_title="Module 3: Online Estimate Averaging (with Save)", page_icon="📊")
st.title("📊 Module 3: Online Estimate Averaging")

st.markdown("Enter any or all of the following estimates:")

zillow = st.number_input("Zillow Zestimate ($)", min_value=0, step=1000, format="%i")
redfin = st.number_input("Redfin Estimate ($)", min_value=0, step=1000, format="%i")
real_avm = st.number_input("Real AVM Value ($)", min_value=0, step=1000, format="%i")

if st.button("Save & Calculate Online Estimate Average"):
    estimates = [val for val in [zillow, redfin, real_avm] if val > 0]
    if estimates:
        avg = round(sum(estimates) / len(estimates))
        st.session_state["online_avg"] = avg
        # NEW: persist individual inputs for downstream modules
        st.session_state["online_estimates"] = {
            "zillow": zillow if zillow > 0 else None,
            "redfin": redfin if redfin > 0 else None,
            "real_avm": real_avm if real_avm > 0 else None
        }
        st.success(f"✅ Online Estimate Average saved: ${avg:,}")
        st.info("Saved individual sources for Modules 8, 9 and 11.")
    else:
        st.warning("Please enter at least one estimate.")
