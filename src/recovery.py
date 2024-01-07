"""A module for calculating response factors and recoveries.

This module provides functions for calculating the response factors (RF) and
recoveries from ISRS, blanks, QCs and study samples.
"""

import matplotlib.pylab as plt
import pandas as pd

import common_operations


class Recovery(common_operations.BaseCalculator):
    """A class for calculating response factors and recoveries."""

    def __init__(self, data):
        super().__init__(data)

    def calculate_response_factor(self) -> pd.DataFrame:
        is_rs_amount = self.get_is_rs_amount()

        is_area = self.get_sample_areas_by_sample_type("isrs").loc[
            self.get_is_rs_name()["is_name"], :
        ]

        rs_area = (
            self.get_sample_areas_by_sample_type("isrs")
            .loc[self.get_is_rs_name()["rs_name"], :]
            .squeeze()
        )

        recovery = ((is_area * is_rs_amount["rs_amount"].squeeze()) / rs_area).div(
            is_rs_amount["is_amount"], axis="index"
        )

        return recovery

    def plot_response_factor(self, by_sample=False):
        fig, ax = plt.subplots()
        if by_sample:
            plot = self.calculate_response_factor().boxplot(ax=ax, rot=90)
        else:
            plot = self.calculate_response_factor().transpose().boxplot(ax=ax, rot=90)
        ax.set_title("Relative response factors")
        ax.set_ylabel("Response factors compared to reconstitution standard")

        return plot

    def calculate_recovery(self) -> pd.DataFrame:
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

    def plot_recovery(self, by_sample=True):
        fig, ax = plt.subplots()
        if by_sample:
            plot = self.calculate_recovery().boxplot(ax=ax, rot=90)
        else:
            plot = self.calculate_recovery().transpose().boxplot(ax=ax, rot=90)
        ax.set_title("Relative response factors")
        ax.set_ylabel("Response factors compared to reconstitution standard")

        return plot
