"""
"""

import matplotlib.pylab as plt
import pandas as pd

import common_operations


class ConcentrationCalculator(common_operations.BaseCalculator):
    def __init__(self, data, correction_factor=None):
        super().__init__(data)
        self.correction_factor = correction_factor

    def calculate_concentration(self):
        AVG_native_concentration_in_blank = (
            self.get_sample_concentrations_by_sample_type("blank").mean(axis=1)
        )
        native_concentration_in_samples_other_than_blank = (
            self.get_sample_concentrations_by_sample_type("sample")
        )
        if self.correction_factor is not None:
            concentrations = (
                (
                    native_concentration_in_samples_other_than_blank.sub(
                        AVG_native_concentration_in_blank, axis=0
                    )
                )
                .mul(self.correction_factor, axis=0)
                .div(self.get_sample_volume_by_sample_type("sample"))
            )
        else:
            concentrations = (
                native_concentration_in_samples_other_than_blank.sub(
                    AVG_native_concentration_in_blank, axis=0
                )
            ).div(self.get_sample_volume_by_sample_type("sample"))
        return concentrations.mask(concentrations <= 0, 1)

    def plot_concentration(self, by_sample=False):
        fig, ax = plt.subplots()
        if by_sample:
            plot = self.calculate_concentration().boxplot(ax=ax, rot=90)
        else:
            plot = self.calculate_concentration().transpose().boxplot(ax=ax, rot=90)
        ax.set_title("Concentration")
        ax.set_ylabel("Concentration (pg/ml)")
        ax.grid(False)
        return plot
