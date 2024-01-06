from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import matplotlib.pylab as plt
import pandas as pd

import utils


class ConcentrationCalculator:
    def __init__(
        self,
        concentrations,
        sample_properties_file,
        correction_factors,
    ):
        self.concentrations = concentrations.query("type == 'concentration'").set_index(
            "name"
        )
        self.sample_properties_file = sample_properties_file
        self.correction_factors = correction_factors

    @property
    def blank_sample_names(self):
        return self.sample_properties_file.loc[
            self.sample_properties_file.sample_type == "blank", "sample_name"
        ].values

    @property
    def other_sample_names(self):
        return self.sample_properties_file.loc[
            self.sample_properties_file.sample_type.isin(["sample", "qc"]),
            "sample_name",
        ].values

    @property
    def sample_volumes(self):
        return (
            self.sample_properties_file.query(
                "sample_name.isin(@self.other_sample_names)"
            )
            .drop(columns="sample_type")
            .set_index("sample_name")
            .squeeze()
        )

    def calculate_average_blanks(self):
        return self.concentrations.loc[:, self.blank_sample_names].mean(axis=1)

    def calculate_concentrations(self):
        concentrations = (
            (
                self.concentrations.filter(items=self.other_sample_names, axis=1).sub(
                    self.calculate_average_blanks(), axis=0
                )
            )
            .mul(self.correction_factors, axis=0)
            .div(self.sample_volumes)
        )
        return concentrations.mask(concentrations <= 0, 1)
