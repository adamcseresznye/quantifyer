"""A module for performing concentration calculations in samples.

If QC file is not supplied, concentrations of analyes are divided by the
correction factor, which in this case set to 1 (ie no correction is performed).
"""

from typing import Any

import matplotlib.pylab as plt
import pandas as pd

import common_operations


class MassBasedConcentrationCalculator(common_operations.BaseCalculator):
    """A class for performing mass-based concentration calculations in samples.
    It takes in a data (data.Data()) and a correction factor qc.CorrectionFactor() object as input.
    """

    def __init__(self, data, correction_factor):
        """
        Initializes an instance of the class.

        Args:
            data (type): The data to be used for initialization.
            correction_factor (type): The correction factor to be applied.

        Returns:
            None
        """
        super().__init__(data)
        self.correction_factor = correction_factor

    def calculate_concentration(self) -> pd.DataFrame:
        """
        Calculate the concentration of samples based on native concentration values.

        Returns:
            pd.DataFrame: The calculated concentrations of samples.
        """
        AVG_native_concentration_in_blank = (
            self.get_sample_concentrations_by_sample_type("blank").mean(axis=1)
        )
        native_concentration_in_samples_other_than_blank = (
            self.get_sample_concentrations_by_sample_type("sample")
        )

        concentrations = (
            (
                native_concentration_in_samples_other_than_blank.sub(
                    AVG_native_concentration_in_blank, axis=0
                )
            )
            .mul(self.correction_factor, axis=0)
            .div(self.get_sample_volume_by_sample_type("sample"))
        )

        return concentrations.mask(concentrations <= 0, 0)

    def plot_concentration(self, by_sample=False, figsize=(5, 5)) -> Any:
        """
        Plot the concentration of the samples.

        Args:
            by_sample (bool, optional): If True, plot concentration by sample.
                                        If False, plot concentration by analyte. Defaults to False.

        Returns:
            Any: The matplotlib plot object.
        """
        fig, ax = plt.subplots(figsize=figsize)
        if by_sample:
            plot = self.calculate_concentration().boxplot(ax=ax, rot=90)
        else:
            plot = self.calculate_concentration().transpose().boxplot(ax=ax, rot=90)
        ax.set_title("Concentration")
        ax.set_ylabel("Concentration (pg/ml)")
        ax.grid(False)
        fig.tight_layout()
        return plot
