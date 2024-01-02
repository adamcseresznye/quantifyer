# -*- coding: utf-8 -*-
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import matplotlib.pylab as plt
import matplotlib.pyplot as plt
import pandas as pd

import utils


class Recovery:
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

    def calculate_RRF(self, areas, amounts):
        rs_area = self.filter_peak_areas(self.rs_identity, areas).squeeze()
        is_area = self.filter_peak_areas(self.is_identity, areas)

        rs_amount = amounts.loc[self.rs_identity].squeeze()
        is_amount = amounts.loc[self.is_identity]

        return ((is_area * rs_amount) / rs_area).div(is_amount, axis="index")

    def calculate_mean_RRF(self):
        return self.calculate_RRF(
            self.isrs_sample_names, self.is_concentration_file_amount()
        ).mean(axis="columns")

    def get_RFF_stats(self):
        return self.calculate_RRF(
            self.isrs_sample_names, self.is_concentration_file_amount()
        ).describe()

    def plot_RFF(self):
        fig, ax = plt.subplots()
        plot = self.calculate_RRF(
            self.isrs_sample_names, self.is_concentration_file_amount()
        ).boxplot(ax=ax, rot=90)
        ax.set_title("Boxplots for RFF values")

        return plot

    def calculate_recovery(self):
        rs_area = self.filter_peak_areas(
            self.rs_identity, self.sample_names_not_isrs
        ).squeeze()
        is_area = self.filter_peak_areas(self.is_identity, self.sample_names_not_isrs)

        rs_amount = self.is_concentration_file_amount(self.rs_identity).squeeze()
        is_amount = self.is_concentration_file_amount(self.is_identity)

        mean_RFF = self.calculate_mean_RRF()

        is_masses = ((is_area * rs_amount) / rs_area).div(mean_RFF, axis="index")

        return is_masses.div(is_amount, axis="index").mul(100)

    def get_recovery_stats(self):
        return self.calculate_recovery().describe()

    def plot_recovery(self):
        fig, ax = plt.subplots()
        plot = self.calculate_recovery().boxplot(ax=ax, rot=90)
        ax.set_title("Boxplots for recovery values")

        return plot

    def filter_peak_areas(self, index, columns):
        return self.peak_areas.loc[
            self.peak_areas.index.isin(index), self.peak_areas.columns.isin(columns)
        ]

    def is_concentration_file_amount(self, index=None):
        if index is None:
            index = self.is_concentration_file.index
        return self.is_concentration_file.loc[index, "amount"]
