"""A module for testing the data.py module.

This module ensures that data integrity is thoroughly assessed when reading files before any processing occurs.
"""

from io import StringIO
from pathlib import Path
from typing import Optional

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

import data


@pytest.fixture
def mock_results_csv():
    return "Name,Type,QC/1,BLaNk:3,SamPLe!25\n13C*HCB,AREA,123,125,542\nCB!143,CONC,6,666,84"


@pytest.fixture
def expected_results_csv():
    return "name,type,qc_1,blank_3,sample_25\n13c_hcb,area,123, 125,542\ncb_143,conc,6,666,84"


@pytest.fixture
def mock_is_correspondence_file_csv():
    return "naTiVe,intERNal*STANdard,exterNAL STANdard\nalpaHCH,13C-HCB,CB/207\nBDE_100,BDE^103,CB%207"


@pytest.fixture
def expected_is_correspondence_file_csv():
    return "native,internal_standard,external_standard\nalpahch,13c_hcb,cb_207\nbde_100,bde_103,cb_207"


@pytest.fixture
def mock_sample_properties_file_csv():
    return "saMPle)name,sample}Type,volume\nQC_1,QC,0.5\nSample_5,sample,0.5\nBlanK_3,BLANK,0.5"


@pytest.fixture
def expected_sample_properties_file_csv():
    return "sample_name,sample_type,volume\nqc_1,qc,0.5\nsample_5,sample,0.5\nblank_3,blank,0.5"


@pytest.fixture
def mock_qc_file_csv():
    return "natIVe,CONcentration\nBDE_100,0.529125198"


@pytest.fixture
def mock_is_concentration_file_csv():
    return "nAMe,AMOunt\nCB_207,1000"


def test_preprocess_results_csv(mock_results_csv, expected_results_csv):
    # Use test_data and expected_data inside the function
    preprocessed_df = data.preprocess_file(StringIO(mock_results_csv))
    expected_df = pd.read_csv(StringIO(expected_results_csv))

    assert_frame_equal(expected_df, preprocessed_df)


def test_preprocess_is_correspondence_file_csv(
    mock_is_correspondence_file_csv, expected_is_correspondence_file_csv
):
    # Use test_data and expected_data inside the function
    preprocessed_df = data.preprocess_file(StringIO(mock_is_correspondence_file_csv))
    expected_df = pd.read_csv(StringIO(expected_is_correspondence_file_csv))

    assert_frame_equal(expected_df, preprocessed_df)


def test_preprocess_sample_properties_file_csv(
    mock_sample_properties_file_csv, expected_sample_properties_file_csv
):
    # Use test_data and expected_data inside the function
    preprocessed_df = data.preprocess_file(StringIO(mock_sample_properties_file_csv))
    expected_df = pd.read_csv(StringIO(expected_sample_properties_file_csv))

    assert_frame_equal(expected_df, preprocessed_df)


def test_validate_data_with_required_args(
    mock_results_csv,
    mock_is_correspondence_file_csv,
    mock_sample_properties_file_csv,
):
    # Create an instance of Data
    df = data.Data(
        quant_file=StringIO(mock_results_csv),
        is_correspondence_file=StringIO(mock_is_correspondence_file_csv),
        sample_properties_file=StringIO(mock_sample_properties_file_csv),
    )

    df.validate_data()


def test_validate_data_with_all_args(
    mock_results_csv,
    mock_is_correspondence_file_csv,
    mock_sample_properties_file_csv,
    mock_qc_file_csv,
    mock_is_concentration_file_csv,
):
    # Create an instance of Data
    df = data.Data(
        quant_file=StringIO(mock_results_csv),
        is_correspondence_file=StringIO(mock_is_correspondence_file_csv),
        sample_properties_file=StringIO(mock_sample_properties_file_csv),
        qc_file=StringIO(mock_qc_file_csv),
        is_concentration_file=StringIO(mock_is_concentration_file_csv),
    )

    df.validate_data()
