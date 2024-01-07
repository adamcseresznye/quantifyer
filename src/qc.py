"""This module is designed for computing correction factors derived from quality control samples.

The module includes functions specifically crafted to determine correction factors
for individual analytes. These factors are calculated by comparing the
known amounts of analytes with their experimentally measured values.
"""

import matplotlib.pylab as plt
import pandas as pd

import common_operations


class CorrectionFactor(common_operations.BaseCalculator):
    def __init__(self, data):
        super().__init__(data)

    def calculate_measured_qc_concentration(self):
        CONVERT_TO_NGML = 1000
        native_concentration_in_qc = self.get_sample_concentrations_by_sample_type("qc")
        AVG_native_concentration_in_blank = (
            self.get_sample_concentrations_by_sample_type("blank")
        ).mean(axis="columns")

        blank_substracted_native_concentration_in_qc = (
            native_concentration_in_qc.sub(
                AVG_native_concentration_in_blank, axis="index"
            )
            .div(self.get_sample_volume_by_sample_type("qc"), axis=1)
            .div(CONVERT_TO_NGML)
        )
        return blank_substracted_native_concentration_in_qc

    def calculate_correction_factor(self):
        AVG_native_concentration_in_qc = (
            self.calculate_measured_qc_concentration().mean(axis="columns")
        )
        theoretical_native_concentration_in_qc = self.data.qc_file.set_index(
            "native"
        ).squeeze()
        correction_factor = theoretical_native_concentration_in_qc.div(
            AVG_native_concentration_in_qc
        )

        return correction_factor.mask(correction_factor <= 0, 1)

    def plot_correction_factor(self, sort_values=False):
        fig, ax = plt.subplots()
        correction_factors = self.calculate_correction_factor()
        if sort_values:
            correction_factors = self.calculate_correction_factor().sort_values()
        plot = correction_factors.plot.bar(ax=ax, rot=90)
        ax.set_title("Correction factor")
        ax.set_ylabel(
            "Theoretical concentration (ng/ml)/\nAverage measured concentrations in QC samples (ng/ml)"
        )

        plt.axhline(
            y=1,
            xmin=0,
            xmax=self.calculate_correction_factor().size,
            color="r",
            ls="--",
        )
        return plot
