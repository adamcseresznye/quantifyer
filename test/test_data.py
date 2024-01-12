"""A module for testing the data.py module.

This module ensures that data integrity is thoroughly assessed when reading files before any processing occurs.
"""

import pandas as pd
import pytest

import data


@pytest.fixture
def data_processor():
    return data.DataProcessor()


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
    assert "name" in result.columns


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


def test_validate_object_cols_no_uppercase(data_processor):
    # Create a DataFrame with object columns containing only lowercase characters
    df1 = pd.DataFrame(
        {"object_col1": ["abc", "def", "ghi"], "object_col2": ["jkl", "mno", "pqr"]}
    )
    validator = data.DataValidator(data=data_processor)  # Use the fixture
    # Since there are no uppercase characters, the function should not raise an AssertionError
    validator.validate_object_cols(df1)


def test_validate_object_cols_with_uppercase(data_processor):
    # Create a DataFrame with one object column containing uppercase characters
    df2 = pd.DataFrame(
        {"object_col1": ["ABC", "Def", "ghi"], "object_col2": ["jkl", "mno", "pqr"]}
    )
    validator = data.DataValidator(data=data_processor)  # Use the fixture
    # Since there is an uppercase character, the function should raise an AssertionError
    with pytest.raises(AssertionError) as excinfo:
        validator.validate_object_cols(df2)
    assert "object_col1 column should not contain uppercase characters" in str(
        excinfo.value
    )
