"""A module for calculating response factors and recoveries.

This module provides functions for calculating the response factors (RF) and
recoveries from ISRS, blanks, QCs and study samples.
"""

from typing import Any

import matplotlib.pylab as plt
import pandas as pd

import common_operations


class Recovery(common_operations.BaseCalculator):
    """A class for calculating response factors and recoveries. It takes in a data object (data.Data())as input."""

    def __init__(self, data):
        super().__init__(data)

    def calculate_response_factor(self) -> pd.DataFrame:
        """
        Calculates the response factor based on ISRS concentration values.

        :return: A pandas DataFrame containing the calculated response factor.
        :rtype: pd.DataFrame
        :raises ValueError: If the file containing ISRS concentration values is missing.
        """
        if self.data.is_concentration_file is None:
            raise ValueError(
                "The file containing ISRS concentration values is missing. Please provide the file and try again."
            )
        is_rs_amount = self.get_is_rs_amount()

        is_area = self.get_sample_areas_by_sample_type("isrs").loc[
            self.get_is_rs_name()["is_name"], :
        ]

        rs_area = (
            self.get_sample_areas_by_sample_type("isrs")
            .loc[self.get_is_rs_name()["rs_name"], :]
            .squeeze()
        )

        response_factor = (
            (is_area * is_rs_amount["rs_amount"].squeeze()) / rs_area
        ).div(is_rs_amount["is_amount"], axis="index")

        return response_factor

    def plot_response_factor(self, by_sample=False, figsize=(5, 5)) -> Any:
        """
        Plots the response factor.

        Args:
            by_sample (bool): If True, the response factor is plotted by sample.
                              If False, it is plotted by column.

        Returns:
            Any: The plot object.
        """

        if self.data.is_concentration_file is None:
            raise ValueError(
                "The file containing ISRS concentration values is missing. Please provide the file and try again."
            )
        fig, ax = plt.subplots(figsize=figsize)
        if by_sample:
            plot = self.calculate_response_factor().boxplot(ax=ax, rot=90)
        else:
            plot = self.calculate_response_factor().transpose().boxplot(ax=ax, rot=90)
        ax.set_title("Relative response factor")
        ax.set_ylabel("(IS_AREA * RS_MASS(pg))/(RS_AREA * IS_MASS(pg))")
        ax.grid(False)
        fig.tight_layout()
        return plot

    def calculate_recovery(self) -> pd.DataFrame:
        """
        Calculate the recovery of the IS (Internal Standard) masses in the sample.

        Returns:
            pd.DataFrame: A DataFrame containing the calculated recovery of the IS masses.

        Raises:
            ValueError: If the file containing ISRS concentration values is missing.
        """
        if self.data.is_concentration_file is None:
            raise ValueError(
                "The file containing ISRS concentration values is missing. Please provide the file and try again."
            )
        mean_response_factor = self.calculate_response_factor().mean(axis="columns")
        is_rs_amount = self.get_is_rs_amount()

        is_area = self.get_sample_areas_by_sample_type(["sample", "blank", "qc"]).loc[
            self.get_is_rs_name()["is_name"], :
        ]

        rs_area = (
            self.get_sample_areas_by_sample_type(["sample", "blank", "qc"])
            .loc[self.get_is_rs_name()["rs_name"], :]
            .squeeze()
        )
        is_masses = ((is_area * is_rs_amount["rs_amount"].squeeze()) / rs_area).div(
            mean_response_factor, axis="index"
        )

        return is_masses.div(is_rs_amount["is_amount"], axis="index").mul(100)

    def plot_recovery(self, by_sample=True, figsize=(5, 5)) -> Any:
        """
        Generate a boxplot of the recovery percentages.

        Args:
            by_sample (bool, optional): If True, generate the boxplot by sample.
                                        If False, generate the boxplot by concentration. Defaults to True.

        Raises:
            ValueError: If the file containing ISRS concentration values is missing.

        Returns:
            Any: The boxplot object.
        """
        if self.data.is_concentration_file is None:
            raise ValueError(
                "The file containing ISRS concentration values is missing. Please provide the file and try again."
            )
        fig, ax = plt.subplots(figsize=figsize)
        if by_sample:
            plot = self.calculate_recovery().boxplot(ax=ax, rot=90)
        else:
            plot = self.calculate_recovery().transpose().boxplot(ax=ax, rot=90)
        ax.set_title("Recovery")
        ax.set_ylabel("Recovery (%)")
        ax.grid(False)
        fig.tight_layout()

        return plot
