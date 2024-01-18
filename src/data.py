"""A module for reading, validating, and processing files.

This module provides functions and a data class for reading in and processing CSV files.
"""

import re
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Optional

import pandas as pd
from streamlit.runtime.uploaded_file_manager import UploadedFile

import common_operations


@dataclass
class Data:
    """
    A data class that holds various file paths and processes them.

    Attributes:
        quant_file (str): The path to the quant file containing the peak area and concentration data for each analyte in the samples.
        is_correspondence_file (str): The path to the correspondence file specifying which analyte is quantitated by which internal standard.
        sample_properties_file (str): The path to the sample properties file containing information about each sample such as sample type and extraction volume (mL)
        qc_file (Optional[str]): The path to the QC file. Default is None. contains the measured QC concentration for each analyte. If not provided, all analytes will
          have a correction factor of 1, indicating no correction is applied. This file is used exclusively for calculating correction factors.
        is_concentration_file (Optional[str]): The path to the concentration file. Default is None.This file contains the amount of internal standard and
        reconstitution standard spiked in each sample (in pg). It is used only for calculating recoveries.
    """

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
        if file is not None:
            return self.data_processor.preprocess_file(self.file_reader.read_csv(file))
        return None


class FileReader:
    def read_csv(self, file_path: str) -> pd.DataFrame:
        """
        Read a CSV file and return its contents as a pandas DataFrame.

        Parameters:
            file_path (str): The path to the CSV file.

        Returns:
            pd.DataFrame: The contents of the CSV file as a DataFrame.
        """
        data = pd.read_csv(file_path)
        return data

    def read_excel(self, file_path: str) -> pd.DataFrame:
        """
        Reads an Excel file and returns its contents as a pandas DataFrame.

        Parameters:
            file_path (str): The path to the Excel file.

        Returns:
            pd.DataFrame: The data from the Excel file as a pandas DataFrame.
        """
        data = pd.read_excel(file_path)
        return data

    def read_file(self, file) -> pd.DataFrame:
        """
        Read a file and return its contents as a pandas DataFrame.

        Parameters:
            file (str or StringIO): The file path or StringIO object to read.

        Returns:
            pd.DataFrame: The contents of the file as a pandas DataFrame.

        Raises:
            ValueError: If the file type is unsupported.
        """
        if isinstance(file, StringIO):
            # If the input is a StringIO object, we assume it's CSV format
            return self.read_csv(file)
        else:
            # If the input is a file path, determine the file type based on the suffix
            file_path = Path(file)
            if file_path.suffix == ".csv":
                return self.read_csv(file_path)
            elif file_path.suffix == ".xlsx":
                return self.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_path}")


class DataProcessor:
    def preprocess_file(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocesses a pandas DataFrame by renaming columns to replace non-alphanumeric characters
        with underscores and applying string preprocessing to object columns.

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
        Preprocesses a pandas Series containing string values.

        Args:
            series (pd.Series): The pandas Series to be preprocessed.

        Returns:
            pd.Series: The preprocessed pandas Series.
        """
        return series.astype(str).str.replace(r"\W", "_", regex=True).str.lower()


class DataValidationError(Exception):
    pass


class DataValidator:
    """A class to perform data validation prior to performing calculations."""

    def __init__(self, data):
        self.data = data

    def validate(self):
        """
        Validate the data in the dataframe.
        """
        self.validate_column_names_in_dataframe()
        self.validate_lower_case_in_object_col()
        self.validate_is_concentration_file_has_is_rs()
        self.validate_quant_file_has_area_concentration()
        self.validate_df_not_empty()

    def validate_column_names_in_dataframe(self):
        """
        Validates the column names in the dataframes stored in the attributes dictionary.

        This function iterates over the keys and values of the attributes dictionary,
        which contains the names of the dataframe attributes as keys and the expected column names as values.
        For each attribute, it retrieves the corresponding dataframe using the `getattr` function. If the dataframe exists,
        it checks if all the expected columns are present in the dataframe's columns. If any columns are missing, it raises a
        `DataValidationError` with a message indicating the missing columns.

        Parameters:
            self (object): The instance of the class that the function belongs to.

        Raises:
            DataValidationError: If any expected columns are missing in a dataframe.
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
            df = getattr(self.data, attribute)
            if df is not None:
                missing_columns = set(expected_columns) - set(df.columns)
                if missing_columns:
                    raise DataValidationError(
                        f"Missing columns in {attribute}: {missing_columns}"
                    )

    def validate_lower_case_in_object_col(self):
        """
        Validates if there are any uppercase characters in object columns of the data.
        If any uppercase characters are found, raises a DataValidationError.

        Parameters:
            None

        Returns:
            None
        """
        for df in self.data.__dict__.values():
            if isinstance(df, pd.DataFrame):
                for column in df.select_dtypes(include="object"):
                    if df[column].str.isupper().any():
                        raise DataValidationError(
                            f"{column} column should not contain uppercase characters"
                        )

    def validate_is_concentration_file_has_is_rs(self):
        """
        Validates if the concentration file contains both IS and RS.

        Parameters:
            None

        Returns:
            None

        Raises:
            DataValidationError: if no IS and RS found in 'is_concentration_file'
        """
        if self.data.is_concentration_file is not None:
            # Check if 'is_concentration_file' contains both IS and RS
            isrs_name_dict = common_operations.BaseCalculator(
                self.data
            ).get_is_rs_name()
            isrs_flattened_list = [x for v in isrs_name_dict.values() for x in v]
            if len(isrs_flattened_list) == 0:
                raise DataValidationError(
                    "No IS and RS found in 'is_concentration_file'"
                )

    def validate_quant_file_has_area_concentration(self):
        """
        Check if all rows contain 'area' or 'concentration' in the 'type' column.

        :raises DataValidationError: If all rows do not contain 'area' or 'concentration' in the 'type' column.
        """
        # Check if all rows contain 'area' or 'concentration' in the 'type' column
        if (
            self.data.quant_file.type.empty
            or not self.data.quant_file.type.str.contains("area|concentration").all()
        ):
            raise DataValidationError(
                "All rows should contain 'area' or 'concentration' in the 'type' column"
            )

    def validate_df_not_empty(self):
        """
        Checks if any DataFrame in `self.data` is empty and raises a `DataValidationError` if it is.

        Parameters:
            None

        Returns:
            None

        Raises:
            DataValidationError: If any DataFrame in `self.data` is empty.
        """
        for df in self.data.__dict__.values():
            if isinstance(df, pd.DataFrame):
                if df.empty:
                    raise DataValidationError(f"{df.name} is empty")
