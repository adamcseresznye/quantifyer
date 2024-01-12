"""A module for reading, validating, and processing files.

This module provides functions and a data class for reading in and processing CSV files.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd


@dataclass
class Data:
    quant_file: str
    is_correspondence_file: str
    sample_properties_file: str
    qc_file: Optional[str] = None
    is_concentration_file: Optional[str] = None

    def __post_init__(self):
        self.file_reader = FileReader()
        self.data_processor = DataProcessor()
        self.quant_file = self.__process_file(self.quant_file)
        self.is_correspondence_file = self.__process_file(self.is_correspondence_file)
        self.sample_properties_file = self.__process_file(self.sample_properties_file)
        self.qc_file = self.__process_file(self.qc_file)
        self.is_concentration_file = self.__process_file(self.is_concentration_file)

    def __process_file(self, file):
        """
        Process a file.

        Args:
            file (str): The path to the file to be processed.

        Returns:
            None: If the file is None.
            Any: The result of preprocessing the file.

        """
        if file is not None:
            return self.data_processor.preprocess_file(self.file_reader.read_file(file))
        return None


class FileReader:
    def read_csv(self, file_path: str) -> pd.DataFrame:
        """
        Reads a CSV file and returns the data as a pandas DataFrame.

        Args:
            file_path (str): The path to the CSV file.

        Returns:
            pd.DataFrame: The data read from the CSV file.
        """
        data = pd.read_csv(file_path)
        return data

    def read_excel(self, file_path: str) -> pd.DataFrame:
        """
        Reads an Excel file and returns the data as a pandas DataFrame.

        Args:
            file_path (str): The path to the Excel file.

        Returns:
            pd.DataFrame: The data read from the Excel file.
        """
        data = pd.read_excel(file_path)
        return data

    def read_file(self, file_path: str) -> pd.DataFrame:
        """
        Reads a file and returns its contents as a Pandas DataFrame.

        Parameters:
            file_path (str): The path to the file to be read.

        Returns:
            pd.DataFrame: The contents of the file as a Pandas DataFrame.

        Raises:
            ValueError: If the file type is not supported.
        """
        file_path = Path(file_path)
        if file_path.suffix == ".csv":
            return self.read_csv(file_path)
        elif file_path.suffix == ".xlsx":
            return self.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path}")


class DataProcessor:
    def preprocess_file(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocesses a pandas DataFrame by renaming columns and applying string preprocessing to object columns.

        Parameters:
            df (pd.DataFrame): The input DataFrame to be preprocessed.

        Returns:
            pd.DataFrame: The preprocessed DataFrame.
        """
        if df is None:
            return None

        df = df.rename(columns=lambda x: re.sub(r"\W", "_", x.lower())).pipe(
            lambda df: df.assign(
                **{
                    col: self.preprocess_str_column(df[col])
                    for col in df.select_dtypes("object").columns
                }
            )
        )

        return df

    def preprocess_str_column(self, series: pd.Series) -> pd.Series:
        """
        Preprocesses a string column in a pandas Series by converting it to string type,
        replacing any non-alphanumeric characters with an underscore, and converting
        all characters to lowercase.

        Parameters:
            series (pd.Series): The pandas Series containing the string column.

        Returns:
            pd.Series: The preprocessed pandas Series with the string column.
        """
        return series.astype(str).str.replace(r"\W", "_", regex=True).str.lower()


class DataValidator:
    def __init__(self, data):
        self.data = data

    def validate_object_cols(self, df):
        """
        Validates the values of object columns in the given DataFrame.

        Parameters:
            df (DataFrame): The DataFrame to be validated.

        Raises:
            AssertionError: If any object column contains uppercase characters.

        Returns:
            None
        """
        for column in df.select_dtypes(include="object"):
            assert (
                not df[column].str.isupper().any()
            ), f"{column} column should not contain uppercase characters"

    def validate_col_names(self, df):
        """
        Validate column names in a DataFrame.

        Parameters:
            df (DataFrame): The DataFrame to validate.

        Raises:
            AssertionError: If any column name contains uppercase characters.
        """
        assert (
            not df.columns.str.isupper().any()
        ), f"Column names should not contain uppercase characters"

    def validate_data(self):
        """
        Validates the data stored in the attributes of the class.

        This function iterates over the `attributes` dictionary, which contains the attribute names as keys and the expected columns as values.
        For each attribute, it retrieves the corresponding dataframe from the `self.data` object using the attribute name. If the dataframe exists,
        it checks whether the expected columns are present in the dataframe. If any of the expected columns are missing, an AssertionError is raised.

        Parameters:
        - None

        Returns:
        - None

        Raises:
        - AssertionError: If any of the expected columns are missing in the dataframe.

        Example:
        ```
        validate_data()
        ```
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
        try:
            for attribute, expected_columns in attributes.items():
                df = getattr(self.data, attribute)
                if df is not None:
                    assert set(expected_columns).issubset(
                        df.columns
                    ), f"Missing columns in {attribute}. Expected: {expected_columns}, Actual: {df.columns}"
                    self.validate_col_names(df)
                    self.validate_object_cols(df)
        except AssertionError as e:
            print(e)
            raise e
