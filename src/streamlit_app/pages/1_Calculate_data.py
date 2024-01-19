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
st.set_option("deprecation.showPyplotGlobalUse", False)

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


def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(uploaded_file.name)[1]
        ) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    return None


def display_data(df, get_summary, get_plot, job, output_type, by_sample=False):
    st.markdown("### *Calculated Values:*")
    st.write(df)
    if get_summary:
        st.markdown("### *Summary Statistics:*")
        st.write(df.describe())
    if get_plot:
        st.markdown("### *Plot:*")
        if output_type.lower().replace(" ", "_") != "correction_factor":
            st.pyplot(
                job.display_plot(
                    f"{output_type.lower().replace(' ', '_')}", by_sample=by_sample
                )
            )
        else:
            st.pyplot(job.display_plot(f"{output_type.lower().replace(' ', '_')}"))


def app():
    st.write("# 🔥Quantifyer🔥")

    st.subheader("Input Files")

    with st.container(border=True):
        st.markdown(
            "Required Files (templates are available [here](https://github.com/adamcseresznye/quantifyer/tree/main/src/streamlit_app/example_data))"
        )
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

    st.subheader("Select Metrics to Calculate")

    with st.container(border=True):
        desired_output = st.radio(
            "",
            ["Recovery", "Correction Factor", "Concentration"],
            captions=[
                "Calculate recovery values if Spike file is provided.",
                "Calculate correction factors if QC file is provided.",
                "Calculate blank corrected concentrations.",
            ],
            label_visibility="collapsed",
        )

    st.subheader("Additional Options")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            get_plot = st.checkbox("Get plot")
            by_sample = False
            if get_plot:
                by_sample = st.checkbox("Plot by sample")
        with col2:
            get_summary = st.checkbox("Get summary statistics")

    click = st.button("Calculate data")

    if click:
        if (
            quant_file is None
            or is_correspondence_file is None
            or sample_properties_file is None
        ):
            st.error(
                "Please provide the required files to start the calculation.", icon="⚠️"
            )
            return

        # Use the save_uploaded_file function for each uploaded file
        quant_file_path = save_uploaded_file(quant_file)
        is_correspondence_file_path = save_uploaded_file(is_correspondence_file)
        sample_properties_file_path = save_uploaded_file(sample_properties_file)
        qc_file_file_path = save_uploaded_file(qc_file)
        is_concentration_file_file_path = save_uploaded_file(is_concentration_file)

        # pass the file paths to the Data class
        if quant_file_path is not None:
            try:
                data_instance = data.Data(
                    quant_file=quant_file_path,
                    is_correspondence_file=is_correspondence_file_path,
                    sample_properties_file=sample_properties_file_path,
                    qc_file=qc_file_file_path,
                    is_concentration_file=is_concentration_file_file_path,
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")

        data_validator = data.DataValidator(data_instance)
        recovery_calculator = recovery.Recovery(data_instance)
        correction_factor_calculator = qc.CorrectionFactor(data_instance)
        concentration_calc = concentration_calculator.MassBasedConcentrationCalculator(
            data_instance,
            correction_factor_calculator.calculate_correction_factor(),
        )

        # initialize pipeline
        mass_based_calculator = pipeline.MassBasedCalculatorPipeline(
            data_instance,
            data_validator,
            recovery_calculator,
            correction_factor_calculator,
            concentration_calc,
        )

        # select strategy and execute pipeline
        job = pipeline.StrategySelector(mass_based_calculator)

        # display results as a tuple of dataframes returning recovery, correction_factors, concentrations if applicable
        recovery_df, correction_factor_df, concentration_df = job.execute()

        with st.container(border=True):
            st.success("Find your results below 👇", icon="✅")
            if desired_output == "Recovery":
                display_data(
                    recovery_df, get_summary, get_plot, job, desired_output, by_sample
                )
            elif desired_output == "Correction Factor":
                display_data(
                    correction_factor_df, get_summary, get_plot, job, desired_output
                )
            elif desired_output == "Concentration":
                display_data(
                    concentration_df,
                    get_summary,
                    get_plot,
                    job,
                    desired_output,
                    by_sample,
                )


if __name__ == "__main__":
    app()
