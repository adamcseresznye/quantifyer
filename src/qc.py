"""This module is designed for computing correction factors derived from quality control samples.

The module includes functions specifically crafted to determine correction factors
for individual analytes. These factors are calculated by comparing the
known amounts of analytes with their experimentally measured values.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import matplotlib.pylab as plt
import pandas as pd

import utils


class CorrectionFactor:
    def __init__(self, concentrations, sample_properties_file, qc_file):
        self.concentrations = concentrations.query("type == 'concentration'").set_index(
            "name"
        )
        self.sample_properties_file = sample_properties_file
        self.qc_file = qc_file.set_index("native").squeeze()

    @property
    def blank_sample_names(self):
        return self.sample_properties_file.loc[
            self.sample_properties_file.sample_type == "blank", "sample_name"
        ].values

    @property
    def qc_sample_names(self):
        return self.sample_properties_file.loc[
            self.sample_properties_file.sample_type == "qc", "sample_name"
        ].values

    @property
    def qc_volume(self):
        return (
            self.sample_properties_file.query("sample_name.isin(@self.qc_sample_names)")
            .drop(columns="sample_type")
            .set_index("sample_name")
            .squeeze()
        )

    def calculate_average_blanks(self):
        return self.concentrations.loc[:, self.blank_sample_names].mean(axis=1)

    def calculate_measured_qc_values(self):
        qc_concentrations = self.concentrations.loc[:, self.qc_sample_names]
        return (
            (qc_concentrations.sub(self.calculate_average_blanks(), axis=0))
            .div(self.qc_volume, axis=1)
            .div(1000)
        )

    def calculate_correction_factors(self):
        calculated_mean_qc = self.calculate_measured_qc_values().mean(axis=1)
        correction_factors = self.qc_file.div(calculated_mean_qc)

        return correction_factors.mask(correction_factors <= 0, 1)

    def plot_correction_factors(self, sort_values=False):
        fig, ax = plt.subplots()
        correction_factors = self.calculate_correction_factors()
        if sort_values:
            correction_factors = self.calculate_correction_factors().sort_values()
        plot = correction_factors.plot.bar(ax=ax, rot=90)
        ax.set_title("Boxplots for RF values")
        ax.set_ylabel("Response factors")

        return plot
