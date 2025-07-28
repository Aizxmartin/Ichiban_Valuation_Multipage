
import streamlit as st
import pandas as pd

st.title("Module 1: CSV Cleaner")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    expected_fields = {
        "Above Grade Finished Area": "ag_sf",
        "Net Close Price": "net_price",
        "Concessions Amount": "concessions",
        "Street Number": "street_number",
        "Street Dir Prefix": "street_prefix",
        "Street Name": "street_name",
        "Street Suffix": "street_suffix",
        "Bedrooms Total": "bedrooms",
        "Bathrooms Total Integer": "bathrooms"
    }

    df = df.rename(columns=expected_fields)
    for field in expected_fields.values():
        if field not in df.columns:
            df[field] = None

    df["address"] = df["street_number"].astype(str) + " " + df["street_prefix"].fillna("") + " " + df["street_name"] + " " + df["street_suffix"]
    df["address"] = df["address"].str.strip()

    def is_row_valid(row):
        return all(pd.notna(row[col]) and str(row[col]).strip() != '' for col in ["ag_sf", "net_price", "street_number", "street_name", "street_suffix"])

    df["valid"] = df.apply(is_row_valid, axis=1)

    excluded = df[~df["valid"]]
    clean_df = df[df["valid"]].sort_values(by="net_price")

    st.success(f"{len(clean_df)} comps loaded successfully. {len(excluded)} excluded due to missing required data.")
    st.dataframe(clean_df)
