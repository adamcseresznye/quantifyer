"""A module for calculating response factors and recoveries.

This module provides functions for calculating the response factors (RF) and
recoveries from ISRS, blanks, QCs and study samples.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import matplotlib.pylab as plt
import pandas as pd

import utils


class Recovery:
    """A class for calculating response factors and recoveries."""

    def __init__(
        self,
        peak_areas,
        is_concentration_file,
        sample_properties_file,
        is_correspondence_file,
    ):
        self.peak_areas = peak_areas.query("type == 'area'").set_index("name")
        self.is_concentration_file = is_concentration_file.set_index("name")
        self.sample_properties_file = sample_properties_file
        self.is_correspondence_file = is_correspondence_file

    @property
    def isrs_sample_names(self):
        return self.sample_properties_file.loc[
            self.sample_properties_file.sample_type == "isrs", "sample_name"
        ].values

    @property
    def sample_names_not_isrs(self):
        return self.sample_properties_file.loc[
            self.sample_properties_file.sample_type != "isrs", "sample_name"
        ].values

    @property
    def is_identity(self):
        return self.is_correspondence_file.internal_standard.unique()

    @property
    def rs_identity(self):
        return self.is_correspondence_file.external_standard.unique()

    def calculate_RF(self) -> pd.DataFrame:
        rs_area, is_area = self.get_is_rs_areas()

        rs_amount = self.is_concentration_file_amount(self.rs_identity).squeeze()
        is_amount = self.is_concentration_file_amount(self.is_identity)

        return ((is_area * rs_amount) / rs_area).div(is_amount, axis="index")

    def plot_RF(self):
        fig, ax = plt.subplots()
        plot = self.calculate_RF().boxplot(ax=ax, rot=90)
        ax.set_title("Boxplots for RF values")
        ax.set_ylabel("Response factors")

        return plot

    def calculate_recovery(self) -> pd.DataFrame:
        rs_area, is_area = self.get_is_rs_areas()

        rs_amount = self.is_concentration_file_amount(self.rs_identity).squeeze()
        is_amount = self.is_concentration_file_amount(self.is_identity)

        mean_RFF = self.calculate_RF().mean(axis="columns")

        is_masses = ((is_area * rs_amount) / rs_area).div(mean_RFF, axis="index")

        return is_masses.div(is_amount, axis="index").mul(100)

    def plot_recovery(self):
        fig, ax = plt.subplots()
        plot = self.calculate_recovery().boxplot(ax=ax, rot=90)
        ax.set_title("Boxplots for recovery values")
        ax.set_ylabel("Recovery (%)")

        return plot

    def is_concentration_file_amount(self, index=None) -> pd.DataFrame:
        if index is None:
            index = self.is_concentration_file.index
        return self.is_concentration_file.loc[index, "amount"]

    def get_is_rs_areas(self) -> Tuple[pd.Series, pd.DataFrame]:
        rs_area = self.peak_areas.loc[
            self.rs_identity, lambda df: df.columns.isin(self.isrs_sample_names)
        ].squeeze()
        is_area = self.peak_areas.loc[
            self.is_identity, lambda df: df.columns.isin(self.isrs_sample_names)
        ]
        return rs_area, is_area
