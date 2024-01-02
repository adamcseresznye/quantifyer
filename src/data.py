# -*- coding: utf-8 -*-
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import matplotlib.pylab as plt
import matplotlib.pyplot as plt
import pandas as pd

import utils


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
        .rename(columns=lambda x: x.replace(r"[^a-zA-Z0-9]", "_").lower())
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
    return series.astype(str).str.replace(r"[^a-zA-Z0-9]", "_", regex=True).str.lower()


@dataclass
class Data:
    quant_file: str
    is_correspondence_file: str
    sample_properties_file: str
    qc_file: Optional[str] = None
    is_concentration_file: Optional[str] = None

    def __post_init__(self):
        self.quant_file = preprocess_file(self.quant_file)
        self.is_correspondence_file = preprocess_file(self.is_correspondence_file)
        self.sample_properties_file = preprocess_file(self.sample_properties_file)

        if self.qc_file is not None:
            self.qc_file = preprocess_file(self.qc_file)
        if self.is_concentration_file is not None:
            self.is_concentration_file = preprocess_file(self.is_concentration_file)
