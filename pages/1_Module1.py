
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Module 1: Load and Clean Comps", page_icon="📥")
st.title("📥 Module 1: Load and Preview Comp Data")

uploaded_file = st.file_uploader("Upload Comp CSV File", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Rename commonly used fields for internal consistency
    rename_map = {
        "Above Grade Finished Area": "ag_sf",
        "Net Close Price": "net_price",
        "Concessions Amount": "concessions",
        "Bedrooms Total": "bedrooms",
        "Bathrooms Total Integer": "bathrooms"
    }
    df.rename(columns=rename_map, inplace=True)

    # Combine address fields safely
    if all(col in df.columns for col in ["Street Number", "Street Name", "Street Suffix"]):
        df["full_address"] = (
            df["Street Number"].astype(str).str.strip()
            + " "
            + df.get("Street Dir Prefix", "").fillna("").astype(str).str.strip()
            + " "
            + df["Street Name"].astype(str).str.strip()
            + " "
            + df["Street Suffix"].astype(str).str.strip()
        ).str.replace("  ", " ").str.strip()
    else:
        st.warning("Some address components are missing. 'full_address' will not be generated.")
        df["full_address"] = "Unknown"

    # Drop rows with missing critical values
    required_fields = ["ag_sf", "net_price", "bedrooms", "bathrooms"]
    initial_count = len(df)
    df.dropna(subset=required_fields, inplace=True)
    removed = initial_count - len(df)

    if removed > 0:
        st.info(f"{removed} comps removed due to missing critical fields.")

    df.sort_values(by="net_price", inplace=True)
    st.dataframe(df)

    # Save to session
    st.session_state.cleaned_comp_data = df
    st.success("Comp data loaded and cleaned successfully.")
