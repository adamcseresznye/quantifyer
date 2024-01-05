"""A module for testing the recovery.py module.

This module evaluates accurate recovery calculations by preventing the introduction of errors during the calculation process
"""

from io import StringIO
from pathlib import Path
from typing import Optional

import pandas as pd
import pytest

import data
import recovery


@pytest.fixture
def mock_peak_areas():
    return "name,type,QC_1,QC_2,QC_3,QC_4,QC_5,ISRS_1,ISRS_2,ISRS_3,ISRS_4,ISRS_5\n13C_HCB,Area,20,40,60,80,100,20,40,60,80,100\nCB_207,Area,100,100,100,100,100,1000,1000,1000,1000,1000"


@pytest.fixture
def mock_is_concentration_file():
    return "name,amount\n13C_HCB,1000\nCB_207,1000"


@pytest.fixture
def mock_sample_properties_file():
    return "sample_name,sample_type,volume\nQC_1,qc,0.5\nQC_2,qc,0.5\nQC_3,qc,0.5\nQC_4,qc,0.5\nQC_5,qc,0.5\nISRS_1,isrs,0.5\nISRS_2,isrs,0.5\nISRS_3,isrs,0.5\nISRS_4,isrs,0.5\nISRS_5,isrs,0.5"


@pytest.fixture
def mock_is_correspondence_file():
    return "native,internal_standard,external_standard\nalpaHCH,13C_HCB,CB_207"


def test_calculate_mean_RF(
    mock_peak_areas,
    mock_is_correspondence_file,
    mock_sample_properties_file,
    mock_is_concentration_file,
):
    # Create an instance of Data
    df = data.Data(
        quant_file=StringIO(mock_peak_areas),
        is_correspondence_file=StringIO(mock_is_correspondence_file),
        sample_properties_file=StringIO(mock_sample_properties_file),
        is_concentration_file=StringIO(mock_is_concentration_file),
    )

    df.validate_data()

    mean_RF = (
        recovery.Recovery(
            df.quant_file,
            df.is_concentration_file,
            df.sample_properties_file,
            df.is_correspondence_file,
        )
        .calculate_RF()
        .mean(axis="columns")
        .iloc[0]
    )
    assert pytest.approx(mean_RF, 0.01) == 0.06


def test_calculate_mean_recovery(
    mock_peak_areas,
    mock_is_correspondence_file,
    mock_sample_properties_file,
    mock_is_concentration_file,
):
    # Create an instance of Data
    df = data.Data(
        quant_file=StringIO(mock_peak_areas),
        is_correspondence_file=StringIO(mock_is_correspondence_file),
        sample_properties_file=StringIO(mock_sample_properties_file),
        is_concentration_file=StringIO(mock_is_concentration_file),
    )

    df.validate_data()

    mean_recovery = (
        recovery.Recovery(
            df.quant_file,
            df.is_concentration_file,
            df.sample_properties_file,
            df.is_correspondence_file,
        )
        .calculate_recovery()
        .mean(axis=1)
        .iloc[0]
    )
    assert pytest.approx(mean_recovery, 0.01) == 100


def test_calculate_sum_recovery(
    mock_peak_areas,
    mock_is_correspondence_file,
    mock_sample_properties_file,
    mock_is_concentration_file,
):
    # Create an instance of Data
    df = data.Data(
        quant_file=StringIO(mock_peak_areas),
        is_correspondence_file=StringIO(mock_is_correspondence_file),
        sample_properties_file=StringIO(mock_sample_properties_file),
        is_concentration_file=StringIO(mock_is_concentration_file),
    )

    df.validate_data()

    sum_recovery = (
        recovery.Recovery(
            df.quant_file,
            df.is_concentration_file,
            df.sample_properties_file,
            df.is_correspondence_file,
        )
        .calculate_recovery()
        .sum(axis=1)
        .iloc[0]
    )
    assert pytest.approx(sum_recovery, 0.01) == 500


def test_individual_recoveries(
    mock_peak_areas,
    mock_is_correspondence_file,
    mock_sample_properties_file,
    mock_is_concentration_file,
):
    # Create an instance of Data
    df = data.Data(
        quant_file=StringIO(mock_peak_areas),
        is_correspondence_file=StringIO(mock_is_correspondence_file),
        sample_properties_file=StringIO(mock_sample_properties_file),
        is_concentration_file=StringIO(mock_is_concentration_file),
    )

    df.validate_data()

    individual_recoveries = (
        recovery.Recovery(
            df.quant_file,
            df.is_concentration_file,
            df.sample_properties_file,
            df.is_correspondence_file,
        )
        .calculate_recovery()
        .values.flatten()
        .tolist()
    )
    expected_recoveries = [33.333, 66.667, 100.000, 133.333, 166.667]

    assert pytest.approx(individual_recoveries, 0.01) == expected_recoveries


def test_individual_RFs(
    mock_peak_areas,
    mock_is_correspondence_file,
    mock_sample_properties_file,
    mock_is_concentration_file,
):
    # Create an instance of Data
    df = data.Data(
        quant_file=StringIO(mock_peak_areas),
        is_correspondence_file=StringIO(mock_is_correspondence_file),
        sample_properties_file=StringIO(mock_sample_properties_file),
        is_concentration_file=StringIO(mock_is_concentration_file),
    )

    df.validate_data()

    individual_RFs = (
        recovery.Recovery(
            df.quant_file,
            df.is_concentration_file,
            df.sample_properties_file,
            df.is_correspondence_file,
        )
        .calculate_RF()
        .values.flatten()
        .tolist()
    )
    expected_RFs = [0.020, 0.040, 0.060, 0.080, 0.100]

    assert pytest.approx(individual_RFs, 0.01) == expected_RFs
