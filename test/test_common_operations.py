"""A module for testing the common_operations.py module."""

from io import StringIO

import pandas as pd
import pytest

import common_operations
import data


# Fixture to initialize Data object
@pytest.fixture
def data_obj():
    test_data = {
        "quant_file": StringIO(
            "Name,type,sample_1\ncompound_1,area,100\ncompound_1,concentration,100"
        ),
        "is_correspondence_file": StringIO(
            "native,internal_standard,external_standard\ncompound_1,IS_1,RS_1"
        ),
        "sample_properties_file": StringIO(
            "sample_name,sample_type,volume\nsample_1,blank,10\nsample_2,QC,10\nsample_3,sample,10"
        ),
        "qc_file": StringIO("native,concentration\ncompound_1,10"),
        "is_concentration_file": StringIO("name,amount\nIS_1,10\nRS_1,10"),
    }
    return data.Data(**test_data)


################################################
# get_is_rs_name
################################################


def test_get_is_rs_name_all_correct(data_obj):
    result = common_operations.BaseCalculator(data_obj).get_is_rs_name()
    assert result["is_name"] == ["is_1"]
    assert result["rs_name"] == ["rs_1"]


################################################
# get_is_rs_amount
################################################


def test_get_is_rs_amount(data_obj):
    result = common_operations.BaseCalculator(data_obj).get_is_rs_amount()
    assert result["is_amount"].values == 10
    assert result["rs_amount"].values == 10


################################################
# get_sample_names_by_sample_type
################################################


def test_get_sample_names_by_sample_type_blank(data_obj):
    result = common_operations.BaseCalculator(data_obj).get_sample_names_by_sample_type(
        "blank"
    )
    assert result == ["sample_1"]


def tes_tget_sample_names_by_sample_type_qc(data_obj):
    result = common_operations.BaseCalculator(data_obj).get_sample_names_by_sample_type(
        "qc"
    )
    assert result == ["sample_2"]


def test_get_sample_names_by_sample_type_sample(data_obj):
    result = common_operations.BaseCalculator(data_obj).get_sample_names_by_sample_type(
        "sample"
    )
    assert result == ["sample_3"]


################################################
# get_sample_volume_by_sample_type
################################################


def test_get_sample_volume_by_sample_type_blank(data_obj):
    result = common_operations.BaseCalculator(
        data_obj
    ).get_sample_volume_by_sample_type("blank")
    assert result == 10


def test_get_sample_volume_by_sample_type_qc(data_obj):
    result = common_operations.BaseCalculator(
        data_obj
    ).get_sample_volume_by_sample_type("qc")
    assert result == 10


def test_get_sample_volume_by_sample_type_sample(data_obj):
    result = common_operations.BaseCalculator(
        data_obj
    ).get_sample_volume_by_sample_type("sample")
    assert result == 10


################################################
# get_sample_areas_by_sample_type
################################################


def test_get_sample_areas_by_sample_type(data_obj):
    result = common_operations.BaseCalculator(data_obj).get_sample_areas_by_sample_type(
        "blank"
    )
    assert result.values == 100


################################################
# get_sample_concentrations_by_sample_type
################################################


def test_get_sample_concentrations_by_sample_type(data_obj):
    result = common_operations.BaseCalculator(
        data_obj
    ).get_sample_concentrations_by_sample_type("blank")
    assert result.values == 100
