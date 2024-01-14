"""A module for testing the data.py module.

This module ensures that data integrity is thoroughly assessed when reading files before any processing occurs.
"""

from io import StringIO

import pandas as pd
import pytest

import data


@pytest.fixture
def data_processor():
    return data.DataProcessor()


# Fixture to initialize Data object
@pytest.fixture
def data_obj():
    example_data = {
        "quant_file": StringIO("Name,type"),
        "is_correspondence_file": StringIO(
            "native,internal_standard,external_standard"
        ),
        "sample_properties_file": StringIO("sample_name,sample_type,volume"),
        "qc_file": StringIO("native,concentration"),
        "is_concentration_file": StringIO("name,amount"),
    }
    return data.Data(**example_data)


################################################
# Test the preprocess_file method
################################################


def test_preprocess_file_valid_input(data_processor):
    # Create a DataFrame with object columns for testing
    df = pd.DataFrame(
        {
            "Name": ["Alice", "Bob"],
            "Age": [25, 30],
            "Email": ["alice@example.com", "bob@example.com"],
        }
    )
    result = data_processor.preprocess_file(df)

    # Check if the columns are renamed correctly and string preprocessing is applied
    assert (
        "name" in result.columns
        and "age" in result.columns
        and "email" in result.columns
    )


def test_preprocess_file_empty_input(data_processor):
    # Create an empty DataFrame
    df = pd.DataFrame()
    result = data_processor.preprocess_file(df)
    # Check if the result is an empty DataFrame
    assert result.empty


def test_preprocess_file_no_object_columns(data_processor):
    # Create a DataFrame with no object columns
    df = pd.DataFrame({"age": [25, 30], "height": [165, 180]})
    result = data_processor.preprocess_file(df)
    # Check if the DataFrame remains unchanged as there are no object columns
    assert df.equals(result)


################################################
# test the preprocess_str_column method
################################################


def test_preprocess_str_column_to_string(data_processor):
    series = pd.Series([123, 456])
    result = data_processor.preprocess_str_column(series)
    assert result.dtype == "object"  # 'object' dtype in pandas is used for strings


def test_preprocess_str_column_replace_non_alphanumeric(data_processor):
    series = pd.Series(["hello@world!", "python#rocks"])
    result = data_processor.preprocess_str_column(series)
    assert not result.str.contains(r"\W").any()  # Check for non-alphanumeric characters


def test_preprocess_str_column_to_lowercase(data_processor):
    series = pd.Series(["HELLO", "WORLD"])
    result = data_processor.preprocess_str_column(series)
    assert result.str.islower().all()  # Check if all characters are lowercase


def test_preprocess_str_column_empty_series(data_processor):
    series = pd.Series([])
    result = data_processor.preprocess_str_column(series)
    assert result.empty  # Check if the resulting series is empty


################################################
# test validate_column_names_in_dataframe method
################################################


def test_validate_data_structure_all_correct(data_obj):
    data.DataValidator(
        data_obj
    ).validate_column_names_in_dataframe()  # Check if all attributes have correct columns


def test_missing_columns_in_quant_file(data_obj):
    data_obj.quant_file = pd.DataFrame({"name": []})
    with pytest.raises(data.DataValidationError):
        data.DataValidator(
            data_obj
        ).validate_column_names_in_dataframe()  # Testing for missing columns in quant_file


def test_missing_columns_in_is_correspondence_file(data_obj):
    data_obj.is_correspondence_file = pd.DataFrame(
        {"native": [], "internal_standard": []}
    )
    with pytest.raises(data.DataValidationError):
        data.DataValidator(
            data_obj
        ).validate_column_names_in_dataframe()  # Testing for missing columns in is_correspondence_file


def test_missing_columns_in_sample_properties_file(data_obj):
    data_obj.sample_properties_file = pd.DataFrame(
        {"sample_name": [], "sample_type": []}
    )
    with pytest.raises(data.DataValidationError):
        data.DataValidator(
            data_obj
        ).validate_column_names_in_dataframe()  # Testing for missing columns in sample_properties_file


def test_missing_columns_in_qc_file(data_obj):
    data_obj.qc_file = pd.DataFrame({"native": []})
    with pytest.raises(data.DataValidationError):
        data.DataValidator(
            data_obj
        ).validate_column_names_in_dataframe()  # Testing for missing columns in qc_file


def test_missing_columns_in_is_concentration_file(data_obj):
    data_obj.is_concentration_file = pd.DataFrame({"Name": []})
    data.DataValidator(
        data_obj
    ).validate_lower_case_in_object_col()  # Testing for missing columns in is_concentration_file


################################################
# validate_lower_case_in_object_col
################################################


def test_validate_col_names_not_all_lower(data_obj):
    data_obj.is_concentration_file = pd.DataFrame({"AMOUNT": [], "NaME": []})
    with pytest.raises(data.DataValidationError):
        data.DataValidator(
            data_obj
        ).validate()  # Testing for non-lowercase column names


################################################
# validate_is_concentration_file_has_is_rs
################################################


def test_validate_is_concentration_file_has_is_rs(data_obj):
    data_obj.is_concentration_file = pd.DataFrame({"is_name": ["is_1"]})
    with pytest.raises(data.DataValidationError):
        data.DataValidator(
            data_obj
        ).validate_is_concentration_file_has_is_rs()  # Testing is_concentration_file has IS and RS


################################################
# validate_quant_file_has_area_concentration
################################################


def test_validate_quant_file_has_no_area_concentration(data_obj):
    with pytest.raises(data.DataValidationError):
        data.DataValidator(
            data_obj
        ).validate_quant_file_has_area_concentration()  # Testing quant_file has no area or concentration


################################################
# validate_df_not_empty
################################################


def test_validate_df_not_empty(data_obj):
    with pytest.raises(data.DataValidationError):
        data.DataValidator(
            data_obj
        ).validate_df_not_empty()  # Testing if dfs are not empty


################################################
# test overall validate pipeline
################################################


def test_validate_pipeline(data_obj):
    with pytest.raises(data.DataValidationError):
        data.DataValidator(data_obj).validate()  # Testing overal validation pipeline
