"""A module for reading, validating, and processing files.

This module provides functions and a data class for reading in and processing CSV files.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd


def preprocess_file(file: str) -> pd.DataFrame:
    """Preprocess a CSV file.

    Args:
        file (str or None): Path to the CSV file. If None, returns None.

    Returns:
        pd.DataFrame or None: Processed DataFrame or None if file is None.
    """
    if file is None:
        return None

    df = (
        pd.read_csv(file)
        .rename(columns=lambda x: re.sub(r"\W", "_", x.lower()))
        .pipe(
            lambda df: df.assign(
                **{
                    col: preprocess_str_column(df[col])
                    for col in df.select_dtypes("object").columns
                }
            )
        )
    )

    return df


def preprocess_str_column(series: pd.Series) -> pd.Series:
    """Preprocess a string column.

    Args:
        series (pd.Series): A Pandas Series representing a string column.

    Returns:
        pd.Series: Processed string column.
    """
    return series.astype(str).str.replace(r"\W", "_", regex=True).str.lower()


@dataclass
class Data:
    """A data class for handling and preprocessing multiple files related to quantitative analysis.

    This class is designed to store information about various data files used in a quantitative
    analysis pipeline. It includes methods to preprocess each file and ensures consistent data formatting.

    Attributes:
        quant_file (str): Path to the quantitative data file (CSV format).
        is_correspondence_file (str): Path to the data file that describes what IS is used for what native compound (CSV format).
        sample_properties_file (str): Path to the sample properties data file. It should contain columns names: sample_name,sample_type and volume (CSV format).
        qc_file (Optional[str]): Path to the data file containing concentrations of the quality control sample (CSV format), if applicable.
        is_concentration_file (Optional[str]): Path to the data file containing the amounts of IS and recovery standard (CSV format), if applicable.
    """

    quant_file: str
    is_correspondence_file: str
    sample_properties_file: str
    qc_file: Optional[str] = None
    is_concentration_file: Optional[str] = None

    def validate_object_cols(self, attribute):
        """Validate object-type columns in the specified attribute for uppercase characters.

        Args:
            attribute (str): The attribute name in the Data class containing the DataFrame to be validated.

        Raises:
            AssertionError: If any object-type column in the specified attribute contains uppercase characters.

        Example:
            To validate object-type columns in the 'quant_file' attribute:
            >>> self.validate_object_cols('quant_file')
        """
        if (
            hasattr(self, attribute) and getattr(self, attribute) is not None
        ):  # Check if the attribute is present and not None
            for column in getattr(self, attribute).select_dtypes(include="object"):
                assert (
                    not getattr(self, attribute)[column].str.isupper().any()
                ), f"{column} column should not contain uppercase characters"

    def validate_col_names(self, attribute):
        """Validate column names in the specified attribute for uppercase characters.

        Args:
            attribute (str): The attribute name in the Data class containing the DataFrame to be validated.

        Raises:
            AssertionError: If any column name in the specified attribute contains uppercase characters.

        Example:
            To validate column names in the 'quant_file' attribute:
            >>> self.validate_col_names('quant_file')
        """
        if (
            hasattr(self, attribute) and getattr(self, attribute) is not None
        ):  # Check if the attribute is present and not None
            assert (
                not getattr(self, attribute).columns.str.isupper().any()
            ), f"Column names in {attribute} should not contain uppercase characters"

    def validate_data(self):
        """Validate data attributes against expected columns and additional validations.

        This method performs a series of validations on specified attributes of the class instance.
        It checks if the expected columns are present in the corresponding data attributes,
        validates column names, and performs additional object column validations if applicable.

        Attributes:
            quant_file: A Pandas DataFrame containing quantitative data.
            is_correspondence_file: A Pandas DataFrame describing the correspondence between internal and external standards.
            sample_properties_file: A Pandas DataFrame containing sample properties such as names, types, and volumes.
            qc_file: An optional Pandas DataFrame containing quality control sample concentrations.
            is_concentration_file: An optional Pandas DataFrame containing internal standard concentrations.

        Raises:
            AssertionError: If any of the validations fail, an AssertionError is raised with a detailed message indicating the issue.

        Note:
            The method prints "All validation was successful!" to the screen if no AssertionError is raised.
        """
        attributes = {
            "quant_file": ["name", "type"],
            "is_correspondence_file": [
                "native",
                "internal_standard",
                "external_standard",
            ],
            "sample_properties_file": ["sample_name", "sample_type", "volume"],
            "qc_file": ["native", "concentration"],
            "is_concentration_file": ["name", "amount"],
        }

        for attribute, expected_columns in attributes.items():
            if (
                hasattr(self, attribute) and getattr(self, attribute) is not None
            ):  # Check if the attribute is present and not None
                assert set(expected_columns).issubset(
                    getattr(self, attribute).columns
                ), f"Missing columns in {attribute}. Expected: {expected_columns}, Actual: {getattr(self, attribute).columns}"

        for attribute in attributes:
            if (
                hasattr(self, attribute) and getattr(self, attribute) is not None
            ):  # Check if the attribute is present and not None
                self.validate_col_names(attribute)
                self.validate_object_cols(attribute)
        print("All validation was successful.")

    def __post_init__(self):
        """Initialize and preprocess data files upon class instantiation.

        This method automatically preprocesses the specified data files upon
        creating an instance of the Data class. It ensures that the data is
        formatted consistently for further analysis.
        """
        self.quant_file = preprocess_file(self.quant_file)
        self.is_correspondence_file = preprocess_file(self.is_correspondence_file)
        self.sample_properties_file = preprocess_file(self.sample_properties_file)

        if self.qc_file is not None:
            self.qc_file = preprocess_file(self.qc_file)
        if self.is_concentration_file is not None:
            self.is_concentration_file = preprocess_file(self.is_concentration_file)
