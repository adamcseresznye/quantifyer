"""A module for testing the qc.py module."""

from io import StringIO

import numpy as np
import pandas as pd
import pytest

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


################################################
# calculate_measured_qc_concentration
################################################


def test_calculate_measured_qc_concentration(data_obj):
    calculated_qc_concentrations = (
        qc.CorrectionFactor(data_obj).calculate_measured_qc_concentration().values
    )
    expected_qc_concentrations = np.array([0.0998, 0.0998, 0.0998])
    assert (
        calculated_qc_concentrations == expected_qc_concentrations
    ).all()  # test if measured qc concentrations are calculated correctly


################################################
# calculate_correction_factor
################################################


def test_calculate_correction_factor(data_obj):
    calculated_correction_factor = (
        qc.CorrectionFactor(data_obj).calculate_correction_factor().values
    )
    expected_qc_correction_factor = np.array([1.002])
    assert np.isclose(calculated_correction_factor, expected_qc_correction_factor).all()
