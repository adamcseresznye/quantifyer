"""A module for testing the recovery.py module."""


from io import StringIO

import matplotlib.pylab as plt
import numpy as np
import pandas as pd
import pytest

import data
import recovery


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
# calculate_response_factor
################################################


def test_calculate_response_factor_missing_file(data_obj):
    del data_obj.is_concentration_file
    with pytest.raises(ValueError):
        recovery.Recovery(
            data_obj
        ).calculate_response_factor()  # tests if exception is raised when is_concentration_file is missing


def test_calculate_response_factor(data_obj):
    assert (
        recovery.Recovery(data_obj).calculate_response_factor().values
        == [0.2, 0.4, 0.6]
    ).all()  # tests if response factor is calculated correctly for all samples


################################################
# plot_response_factor
################################################


def test_plot_response_factor_missing_file(data_obj):
    del data_obj.is_concentration_file
    with pytest.raises(ValueError):
        recovery.Recovery(
            data_obj
        ).plot_response_factor()  # tests if exception is raised when is_concentration_file is missing


def test_plot_response_factor(data_obj):
    with plt.ion():
        recovery.Recovery(data_obj).plot_response_factor()


################################################
# calculate_recovery
################################################


def test_calculate_recovery_missing_file(data_obj):
    del data_obj.is_concentration_file
    with pytest.raises(ValueError):
        recovery.Recovery(
            data_obj
        ).calculate_recovery()  # tests if exception is raised when is_concentration_file is missing


def test_calculate_recovery(data_obj):
    calculated_recovery = recovery.Recovery(data_obj).calculate_recovery()
    expected_recovery = np.array([50.0, 100, 150, 50, 100, 150, 50, 100, 150])
    assert np.isclose(
        calculated_recovery, expected_recovery
    ).all()  # tests if all recoveries are calculated correctly for all samples


################################################
# plot_recovery
################################################


def test_plot_recovery_missing_file(data_obj):
    del data_obj.is_concentration_file
    with pytest.raises(ValueError):
        recovery.Recovery(
            data_obj
        ).plot_recovery()  # tests if exception is raised when is_concentration_file is missing


def test_plot_recovery(data_obj):
    with plt.ion():
        recovery.Recovery(data_obj).plot_recovery()
