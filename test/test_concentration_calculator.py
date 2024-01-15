"""A module for testing the concentration_calculator.py module."""

from io import StringIO

import numpy as np
import pandas as pd
import pytest

import concentration_calculator
import data
import qc


# Fixture to initialize Data object
@pytest.fixture
def data_obj():
    csv_data = {
        "quant_file": (
            "name,type,QC_1,QC_2,QC_3,ISRS_1,ISRS_2,ISRS_3,blank_1,blank_2,blank_3,sample_1,sample_2,sample_3\n"
            "internal_standard_name,Area,20,40,60,20,40,60,20,40,60,20,40,60\n"
            "reconstitution_standard_name,Area,100,100,100,100,100,100,100,100,100,100, 100, 100\n"
            "native_name,area,50,50,50,50,50,50,50,50,50,50,50,50\n"
            "native_name,concentration,50,50,50,0,0,0,0.1,0.1,0.1,45,45,45"
        ),
        "is_correspondence_file": (
            "native,internal_standard,external_standard\n"
            "native_name,internal_standard_name,reconstitution_standard_name"
        ),
        "sample_properties_file": (
            "sample_name,sample_type,volume\n"
            "QC_1,qc,0.5\nQC_2,qc,0.5\nQC_3,qc,0.5\n"
            "ISRS_1,isrs,0.5\nISRS_2,isrs,0.5\nISRS_3,isrs,0.5\n"
            "blank_1,blank,0.5\nblank_2,blank,0.5\nblank_3,blank,0.5\n"
            "sample_1,sample,0.5\nsample_2,sample,0.5\nsample_3,sample,0.5"
        ),
        "qc_file": "native,concentration\nnative_name,0.1",
        "is_concentration_file": "name,amount\ninternal_standard_name,1000\nreconstitution_standard_name,1000",
    }
    return data.Data(**{key: StringIO(value) for key, value in csv_data.items()})


def test_calculate_concentration_with_QC(data_obj):
    calculated_concentration = concentration_calculator.ConcentrationCalculator(
        data_obj, qc.CorrectionFactor(data_obj).calculate_correction_factor()
    ).calculate_concentration()
    expected_concentration = np.array([89.98, 89.98, 89.98])
    assert np.isclose(
        calculated_concentration, expected_concentration
    ).all()  # test that the calculated concentration is equal to the expected concentration


def test_calculate_concentration_without_QC(data_obj):
    del data_obj.qc_file
    calculated_concentration = concentration_calculator.ConcentrationCalculator(
        data_obj, qc.CorrectionFactor(data_obj).calculate_correction_factor()
    ).calculate_concentration()
    expected_concentration = np.array([89.8, 89.8, 89.8])
    assert np.isclose(
        calculated_concentration, expected_concentration
    ).all()  # test that the calculated concentration is equal to the expected concentration if QC is not present (ie: correction factor is 1)
