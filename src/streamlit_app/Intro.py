import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

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


st.write("# 🔥Quantifyer🔥")

st.subheader("Introduction")

st.markdown(
    """
    **What** : Quantifyer streamlines the data analysis process for targeted LC/GC-MS applications, enabling rapid calculation of key metrics like recovery,
    correction factor, and concentration values. Additionally, it provides informative plots.
    **Why** :  Manually calculating metrics in Excel can be a tedious and error-prone process, often leading to inconsistencies due to copy-paste errors
    and repetitive operations. Quantifyer eliminates these challenges by automating the calculations, ensuring accuracy and reproducibility.
    Additionally, its rapid processing speed significantly reduces turnaround time, compared to manual quantitation.
    **How** : The Quantifyer app requires only three simple input files: a file containing concentrations and peak areas for each analyte in the samples,
      a file indicating whether each sample is a blank, QC, sample, or standard mix, and a file specifying which analyte is quantitated by which internal standard. See below.

    Link to [GitHub repository](https://github.com/adamcseresznye/quantifyer).
    *Disclaimer: The developer is not liable for errors. This app is provided without any warranties or guarantees.*
"""
)

st.subheader("Expected Files and Formats")

st.markdown(
    """
    Quantifyer requires three mandatory input files:
    * Quantitative data file (CSV/Excel): This file contains peak area and concentration data for each analyte in the samples.
    * Internal standard correspondence file (CSV/Excel): This file specifies which analyte is quantitated by which internal standard and the reconstitution standard used.
    * Sample properties file (CSV/Excel): This file categorizes each sample as blank, QC, sample, or standard, and indicates the extraction volume (mL).

    The app also accepts two optional input files:
    * QC file (CSV/Excel): This file is optional and contains the measured QC concentration for each analyte. If not provided, all analytes will have a correction factor of 1, indicating no correction is applied. This file is used exclusively for calculating correction factors.
    * Spike file (CSV/Excel): This optional file contains the amount of internal standard and reconstitution standard spiked in each sample (in pg). It is used only for calculating recoveries.
"""
)

st.subheader("Examples")

file_path = Path(__file__).parent
quantitative_data_file_path = file_path.joinpath(
    "example_images/quantitative_data_file_example.png"
)
quantitative_data_image = Image.open(quantitative_data_file_path)

st.image(
    quantitative_data_image,
    caption="""Quantitative data file (CSV/Excel). The first two columns should be labeled 'name' and 'type',
    followed by the sample names. In this example, the first two compounds were the internal standards, while the
    third was the reconstitution standard (CB 207). The 'type' column should contain the values 'Area' and 'Concentration' where concentration is expressed in pg. Avoid using whitespaces.""",
)

quantitative_data_file_path = file_path.joinpath(
    "example_images/internal_standard_correspondence_file _example.png"
)
quantitative_data_image = Image.open(quantitative_data_file_path)

st.image(
    quantitative_data_image,
    caption="""Internal standard correspondence file (CSV/Excel). The first column should list the native analytes targeted by the LC/GC-MS analysis.
      The second column (internal_standard) should identify the corresponding internal standards used for quantitation, while the third column (external_standard)
      should specify the reconstitution standard employed.
    """,
)

sample_properties_file_path = file_path.joinpath(
    "example_images/sample_properties_file_example.png"
)
sample_properties_file_image = Image.open(sample_properties_file_path)

st.image(
    sample_properties_file_image,
    caption="""Sample properties file (CSV/Excel). The first column ('sample_name') should correspond
    to the sample names used in the quantitative data file. The second column ('sample_type') should
    identify the type of each sample, which can be either blank, QC, sample, or ISRS. ISRS samples
    contain a mix of internal standards and reconstitution standards and are not extracted; they are
    used for calculating recoveries. The third column ('sample_volume') should indicate the extraction
    volume in milliliters for each sample.
    """,
)

qc_file_path = file_path.joinpath("example_images/qc_file_example.png")
qc_file_image = Image.open(qc_file_path)

st.image(
    qc_file_image,
    caption="""QC file (CSV/Excel), optional. The 'native' column of the internal standard correspondence
    file lists the analytes that were measured in the samples. The 'concentration' column provides the
    known concentration of each analyte in a reference material or quality control sample. Concentrations
    are expressed in micrograms per liter (µg/L) or nanograms per milliliter (ng/mL).
    """,
)

spike_file_path = file_path.joinpath("example_images/spike_file_example.png")
spike_file_image = Image.open(spike_file_path)

st.image(
    spike_file_image,
    caption="""Spike file (CSV/Excel), optional. The 'name' column in the spiked sample file specifies the
      name of the internal standard and reconstitution standard used. The 'amount' column indicates the
      quantity of material spiked during sample preparation in picograms (pg). For instance, if 50
      microliters (µL) of an internal standard mix containing 25 pg/µL of 13C_HCB is spiked into the samples,
      then the corresponding value in the 'amount' column would be 50 x 20 = 1250 pg.
    """,
)
