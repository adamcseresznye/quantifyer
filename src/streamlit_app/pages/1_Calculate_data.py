import os
import sys
import tempfile
from io import StringIO
from pathlib import Path

import pandas as pd
import streamlit as st

import concentration_calculator
import data
import pipeline
import qc
import recovery

sys.path.append(str(Path(__file__).resolve().parent.parent))

st.set_page_config(
    page_title="Quantifyer",
    page_icon="🔥",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://adamcseresznye.github.io/blog/",
        "Report a bug": "https://github.com/adamcseresznye/house_price_prediction",
        "About": "Explore and Predict Belgian House Prices with Immoweb Data and CatBoost!",
    },
)
st.write("# Quantifyer")

st.subheader("Introduction")

with st.expander("### Mandatory files"):
    quant_file = st.file_uploader(
        "Upload your Quantitative data file (CSV/Excel) here:",
        accept_multiple_files=False,
    )
    is_correspondence_file = st.file_uploader(
        "Upload your Internal standard correspondence file (CSV/Excel) here:",
        accept_multiple_files=False,
    )
    sample_properties_file = st.file_uploader(
        "Upload your Sample properties file (CSV/Excel) here:",
        accept_multiple_files=False,
    )

with st.expander("### Optional files"):
    qc_file = st.file_uploader(
        "Upload your QC file (CSV/Excel) here:", accept_multiple_files=False
    )
    is_concentration_file = st.file_uploader(
        "Upload your Spike file (CSV/Excel) here:", accept_multiple_files=False
    )


def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(uploaded_file.name)[1]
        ) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    return None


# Use the save_uploaded_file function for each uploaded file
quant_file_path = save_uploaded_file(quant_file)
is_correspondence_file_path = save_uploaded_file(is_correspondence_file)
sample_properties_file_path = save_uploaded_file(sample_properties_file)

# click = st.button("Start Data Processing", key="start-button")

# Now you can pass the file paths to the Data class
if quant_file_path is not None:
    try:
        data_instance = data.Data(
            quant_file_path,
            is_correspondence_file_path,
            sample_properties_file_path,
        )
        # Use data_instance for further processing
    except Exception as e:
        st.error(f"An error occurred: {e}")

st.write(data_instance.quant_file)
st.write(data_instance.is_correspondence_file)
st.write(data_instance.sample_properties_file)
