"""A module for reading, validating, and processing files.

This module provides functions and a data class for reading in and processing CSV files.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd


class FileReader:
    def read_csv(self, file_path: str) -> pd.DataFrame:
        data = pd.read_csv(file_path)
        return data

    def read_excel(self, file_path: str) -> pd.DataFrame:
        data = pd.read_excel(file_path)
        return data

    def read_file(self, file_path: str) -> pd.DataFrame:
        file_path = Path(file_path)
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
        self.quant_file = self.process_file(self.quant_file)
        self.is_correspondence_file = self.process_file(self.is_correspondence_file)
        self.sample_properties_file = self.process_file(self.sample_properties_file)
        self.qc_file = self.process_file(self.qc_file)
        self.is_concentration_file = self.process_file(self.is_concentration_file)

    def process_file(self, file):
        if file is not None:
            return self.data_processor.preprocess_file(self.file_reader.read_file(file))
        return None


class DataValidator:
    def __init__(self, data):
        self.data = data

    def validate_object_cols(self, df):
        for column in df.select_dtypes(include="object"):
            assert (
                not df[column].str.isupper().any()
            ), f"{column} column should not contain uppercase characters"

    def validate_col_names(self, df):
        assert (
            not df.columns.str.isupper().any()
        ), f"Column names should not contain uppercase characters"

    def validate_data(self):
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
                assert set(expected_columns).issubset(
                    df.columns
                ), f"Missing columns in {attribute}. Expected: {expected_columns}, Actual: {df.columns}"
                self.validate_col_names(df)
                self.validate_object_cols(df)
        print("All validation was successful.")
