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
        """
        Calculate Response Factors (RF).

        Response Factors quantify the instrumental response for each analyte in relation to the
        internal standard. The formula used for calculating RF is:

            RF = (IS Area * RS Amount) / RS Area / IS Amount

        Where:
            IS Area: Peak area of the internal standard.
            RS Area: Peak area of the external standard.
            IS Amount: Concentration of the internal standard.
            RS Amount: Concentration of the external standard.

        The result is a DataFrame of RF values indexed by the sample names.

        Returns:
            pandas.DataFrame: Response Factors calculated for each sample.
        """
        rs_area, is_area = self.get_is_rs_areas()

        rs_amount = self.is_concentration_file_amount(self.rs_identity).squeeze()
        is_amount = self.is_concentration_file_amount(self.is_identity)

        return ((is_area * rs_amount) / rs_area).div(is_amount, axis="index")

    def plot_RF(self):
        """
        Plot boxplots for Response Factors (RF) values.

        This method generates a boxplot visualizing the distribution of Response Factors
        calculated for each sample. The Response Factors are calculated using the
        `calculate_RF` method. The resulting boxplot provides insights into the variability
        and central tendency of the RF values across different samples.

        Returns:
            matplotlib.axes.AxesSubplot: The AxesSubplot containing the boxplot.
        """
        fig, ax = plt.subplots()
        plot = self.calculate_RF().boxplot(ax=ax, rot=90)
        ax.set_title("Boxplots for RF values")
        ax.set_ylabel("Response factors")

        return plot

    def calculate_recovery(self) -> pd.DataFrame:
        """
        Calculate Recovery values.

        Recovery represents the percentage of analyte recovered in the analysis process.
        The formula used for calculating recovery is:

            Recovery (%) = (IS Area * RS Amount) / RS Area / (Mean RF) / IS Amount * 100

        Where:
            IS Area: Peak area of the internal standard.
            RS Area: Peak area of the external standard.
            IS Amount: Concentration of the internal standard.
            RS Amount: Concentration of the external standard.
            Mean RF: Mean Response Factor calculated across samples.

        The result is a DataFrame of Recovery values indexed by the sample names.

        Returns:
            pandas.DataFrame: Recovery values calculated for each sample.
        """
        rs_area, is_area = self.get_is_rs_areas()

        rs_amount = self.is_concentration_file_amount(self.rs_identity).squeeze()
        is_amount = self.is_concentration_file_amount(self.is_identity)

        mean_RFF = self.calculate_RF().mean(axis="columns")

        is_masses = ((is_area * rs_amount) / rs_area).div(mean_RFF, axis="index")

        return is_masses.div(is_amount, axis="index").mul(100)

    def plot_recovery(self):
        """
        Plot boxplots for Recovery values.

        This method generates a boxplot visualizing the distribution of Recovery values
        calculated for each sample. The Recovery values are calculated using the
        `calculate_recovery` method. The resulting boxplot provides insights into the
        variability and central tendency of the Recovery percentages across different samples.

        Returns:
            matplotlib.axes.AxesSubplot: The AxesSubplot containing the boxplot.
        """
        fig, ax = plt.subplots()
        plot = self.calculate_recovery().boxplot(ax=ax, rot=90)
        ax.set_title("Boxplots for recovery values")
        ax.set_ylabel("Recovery (%)")

        return plot

    def is_concentration_file_amount(self, index=None) -> pd.DataFrame:
        """
        Retrieve concentration values from the concentration file.

        This method retrieves concentration values from the concentration file
        for the specified index (sample names). If no index is provided, it defaults
        to using the entire index of the concentration file.

        Parameters:
            index (array-like or None, optional): Index or list of indices to retrieve.
                If None, the entire index of the concentration file is used. Default is None.

        Returns:
            pandas.Series: Concentration values for the specified index.
        """
        if index is None:
            index = self.is_concentration_file.index
        return self.is_concentration_file.loc[index, "amount"]

    def get_is_rs_areas(self) -> Tuple[pd.Series, pd.DataFrame]:
        """
        Retrieve peak areas of internal and external standards for ISRS samples.

        This method extracts the peak areas of internal (IS) and external (RS) standards
        for samples identified as ISRS (Internal Standard Reference Standard). These peak
        areas are obtained from the `peak_areas` DataFrame.

        Returns:
            Tuple[pandas.Series, pandas.DataFrame]: A tuple containing:
                - rs_area (pandas.Series): Peak areas of external standards for ISRS samples.
                - is_area (pandas.DataFrame): Peak areas of internal standards for ISRS samples.
        """
        rs_area = self.peak_areas.loc[
            self.rs_identity, lambda df: df.columns.isin(self.isrs_sample_names)
        ].squeeze()
        is_area = self.peak_areas.loc[
            self.is_identity, lambda df: df.columns.isin(self.isrs_sample_names)
        ]
        return rs_area, is_area
