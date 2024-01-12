"""This module is designed for computing correction factors derived from quality control samples.

The module includes functions specifically crafted to determine correction factors
for individual analytes. These factors are calculated by comparing the
known amounts of analytes with their experimentally measured values.
"""

from typing import Any

import matplotlib.pylab as plt
import pandas as pd

import common_operations


class CorrectionFactor(common_operations.BaseCalculator):
    def __init__(self, data):
        super().__init__(data)

    def calculate_measured_qc_concentration(self) -> pd.DataFrame:
        """
        Calculates the measured QC concentration.

        Returns:
            pd.DataFrame: The measured QC concentration as a pandas DataFrame.
        """
        # if there are no qc files in the sample_properties_file return None
        if len(self.get_sample_names_by_sample_type("qc")) != 0:
            CONVERT_TO_NGML = 1000
            native_concentration_in_qc = self.get_sample_concentrations_by_sample_type(
                "qc"
            )
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

    def calculate_correction_factor(self) -> pd.Series:
        """
        Calculate the correction factor for each analyte. If no QC file is provided
        all analytes will have a correction factor of 1.
        In case correction factor is less than 0, it will be set to 1.

        Returns:
            pd.Series: The correction factor for each native analyte.
        """
        if self.data.qc_file is None:
            # if the qc file is not present, return a correction factor set to 1 for all analytes
            unique_names = pd.Series(self.data.quant_file.name.unique())
            isrs_name = [x for name in self.get_is_rs_name().values() for x in name]
            correction_factor_set_to_one = pd.DataFrame(
                {
                    "native": unique_names[~unique_names.isin(isrs_name)].reset_index(
                        drop=True
                    ),
                    "concentration": 1,
                }
            )
            return correction_factor_set_to_one.set_index("native").squeeze()
        else:
            # else calculate the correction factors
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

    def plot_correction_factor(self, sort_values=False) -> Any:
        """
        Generates a bar plot of the correction factors calculated by the calculate_correction_factor() method.

        Parameters:
            sort_values (bool, optional): If True, the correction factors will be sorted in ascending order before plotting.
                                        Defaults to False.

        Returns:
            plot: The generated bar plot showing the correction factors.
        """
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
