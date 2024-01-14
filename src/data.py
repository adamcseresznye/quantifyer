"""A module for reading, validating, and processing files.

This module provides functions and a data class for reading in and processing CSV files.
"""

import re
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Optional

import pandas as pd

import common_operations


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
        if file is not None:
            return self.data_processor.preprocess_file(self.file_reader.read_file(file))
        return None


class FileReader:
    def read_csv(self, file_path: str) -> pd.DataFrame:
        data = pd.read_csv(file_path)
        return data

    def read_excel(self, file_path: str) -> pd.DataFrame:
        data = pd.read_excel(file_path)
        return data

    def read_file(self, file) -> pd.DataFrame:
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
        return series.astype(str).str.replace(r"\W", "_", regex=True).str.lower()


class DataValidationError(Exception):
    pass


class DataValidator:
    def __init__(self, data):
        self.data = data

    def validate(self):
        self.validate_column_names_in_dataframe()
        self.validate_lower_case_in_object_col()
        self.validate_is_concentration_file_has_is_rs()
        self.validate_quant_file_has_area_concentration()
        self.validate_df_not_empty()

    def validate_column_names_in_dataframe(self):
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
        for df in self.data.__dict__.values():
            if isinstance(df, pd.DataFrame):
                for column in df.select_dtypes(include="object"):
                    if df[column].str.isupper().any():
                        raise DataValidationError(
                            f"{column} column should not contain uppercase characters"
                        )

    def validate_is_concentration_file_has_is_rs(self):
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
        # Check if all rows contain 'area' or 'concentration' in the 'type' column
        if (
            self.data.quant_file.type.empty
            or not self.data.quant_file.type.str.contains("area|concentration").all()
        ):
            raise DataValidationError(
                "All rows should contain 'area' or 'concentration' in the 'type' column"
            )

    def validate_df_not_empty(self):
        for df in self.data.__dict__.values():
            if isinstance(df, pd.DataFrame):
                if df.empty:
                    raise DataValidationError(f"{df.name} is empty")
