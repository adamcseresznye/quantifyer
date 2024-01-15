"""A module for testing the pipeline.py module."""

from io import StringIO

import numpy as np
import pandas as pd
import pytest

import concentration_calculator
import data
import pipeline
import qc
import recovery


# Fixture to initialize Data object with test data
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


# Fixture to initialize MassBasedCalculator object
@pytest.fixture
def calculator(data_obj):
    data_validator = data.DataValidator(data_obj)
    recovery_calculator = recovery.Recovery(data_obj)
    correction_factor_calculator = qc.CorrectionFactor(data_obj)
    concentration_calc = concentration_calculator.MassBasedConcentrationCalculator(
        data_obj, correction_factor_calculator.calculate_correction_factor()
    )
    return pipeline.MassBasedCalculatorPipeline(
        data_obj,
        data_validator,
        recovery_calculator,
        correction_factor_calculator,
        concentration_calc,
    )


# Test function to check return types from calculate_concentration method
def test_calculate_concentration_return_types(calculator):
    recovery, correction_factors, concentrations = calculator.calculate_concentration()
    assert recovery is not None
    assert isinstance(correction_factors, pd.Series)
    assert isinstance(concentrations, pd.DataFrame)


# Test function to check results from calculate_concentration method
def test_calculate_concentration_check_results(calculator):
    (
        calculated_recovery,
        calculated_correction_factors,
        calculated_concentrations,
    ) = calculator.calculate_concentration()
    expected_recovery = np.array([50.0, 100, 150, 50, 100, 150, 50, 100, 150])
    expected_qc_correction_factor = np.array([1.002])
    expected_concentration = np.array([89.98, 89.98, 89.98])
    assert np.isclose(calculated_recovery, expected_recovery).all()
    assert np.isclose(
        calculated_correction_factors, expected_qc_correction_factor
    ).all()
    assert np.isclose(calculated_concentrations, expected_concentration).all()


# Test function to check results without qc file
def test_calculate_concentration_check_results_without_qc(calculator):
    # Modify the calculator object to simulate absence of qc file
    calculator.data.qc_file = None
    (
        calculated_recovery,
        calculated_correction_factors,
        calculated_concentrations,
    ) = calculator.calculate_concentration()
    # Define expected results when qc file is absent
    expected_correction_factor = np.array(
        [1.0]
    )  # Assuming correction factor defaults to 1 without qc file
    assert np.isclose(calculated_correction_factors, expected_correction_factor).all()
