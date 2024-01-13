"""A module for calculating analyte concentrations and generating plots.

It includes strategies for data validation, recovery, correction, and concentration calculations,
with support for customizable plotting functions.
The module employs the strategy pattern making it easy to incorporate new strategies into the pipeline when needed.
"""


from abc import ABC, abstractmethod
from functools import partial
from typing import Any, Tuple

import pandas as pd

import concentration_calculator
import data
import qc
import recovery
import utils


class CalculationStrategy(ABC):
    @abstractmethod
    def calculate_concentration(self):
        pass

    @abstractmethod
    def display_plot(self, plot_name, **kwargs):
        pass


class MassBasedCalculator(CalculationStrategy):
    """
    Initializes an instance of the class.

    Parameters:
        data (object): The data object.
        data_validator (object): The data validator object.
        recovery_calculator (object): The recovery calculator object.
        correction_factor_calculator (object): The correction factor calculator object.
        concentration_calculator (object): The concentration calculator object.

    Returns:
        None
    """

    def __init__(
        self,
        data,
        data_validator,
        recovery_calculator,
        correction_factor_calculator,
        concentration_calculator,
    ):
        self.data = data
        self.data_validator = data_validator
        self.recovery_calculator = recovery_calculator
        self.correction_factor_calculator = correction_factor_calculator
        self.concentration_calculator = concentration_calculator
        default_args = {
            "by_sample": True,
        }
        self.plot_functions = {
            "recovery": partial(self.recovery_calculator.plot_recovery, **default_args),
            "response_factor": partial(
                self.recovery_calculator.plot_response_factor, **default_args
            ),
            "correction_factor": self.correction_factor_calculator.plot_correction_factor,
            "concentration": partial(
                self.concentration_calculator.plot_concentration, **default_args
            ),
        }

    def calculate_concentration(
        self,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Calculate the concentration of analytes based on provided data.

        This function validates the data using the `data_validator.validate_data()` method.
        If the `is_concentration_file` flag is set, it also calculates the recovery using the
        `recovery_calculator.calculate_recovery()` method.

        After validation and recovery calculation (if applicable), this function calculates the
        correction factors using the `correction_factor_calculator.calculate_correction_factor()` method.
        Finally, it calculates the concentrations using the `concentration_calculator.calculate_concentration()` method.

        Returns a tuple of three Pandas DataFrames: `recovery`, `correction_factors`, and `concentrations`.
        """
        # Step 1: Validate the data
        self.data_validator.validate()

        # Initialize recovery as None and return if no is_concentration_file provided
        recovery = None
        if self.data.is_concentration_file is not None:
            # Step 2: Calculate recovery
            recovery = self.recovery_calculator.calculate_recovery()

        # Step 3: Calculate correction factors
        correction_factors = (
            self.correction_factor_calculator.calculate_correction_factor()
        )

        # Step 4: Calculate concentrations
        concentrations = self.concentration_calculator.calculate_concentration()

        return recovery, correction_factors, concentrations

    def display_plot(self, plot_name, **kwargs) -> Any:
        """
        Display a plot based on the given plot name and keyword arguments.

        Parameters:
            plot_name (str): The name of the plot to display.
            **kwargs: Valid arguments: recovery, response_factor, correction_factor, concentration.
            by_sample (bool, optional): If True, plot by sample. If False, plot by analyte.

        Returns:
            Any: The return value of the plot function.
        """
        plot_function = self.plot_functions.get(plot_name)
        if plot_function:
            plot_function(**kwargs)
        else:
            print(
                f"No plot function found for {plot_name}. Valid arguments: {', '.join(list(self.plot_functions.keys()))}."
            )


class Pipeline:
    def __init__(self, strategy: CalculationStrategy):
        self.strategy = strategy

    def execute(self):
        return self.strategy.calculate_concentration()

    def display_plot(self, plot_name, **kwargs):
        self.strategy.display_plot(plot_name, **kwargs)


# Usage example
parent_folder = utils.Configuration.RAW_DATA_PATH

file_paths = {
    "quant_file": parent_folder.joinpath("results.csv"),
    "is_correspondence_file": parent_folder.joinpath("is_std_table_correspondence.csv"),
    "sample_properties_file": parent_folder.joinpath("sample_properties.csv"),
    "qc_file": parent_folder.joinpath("qc.csv"),
    "is_concentration_file": parent_folder.joinpath("is_std_table_concentration.csv"),
}

dfs = data.Data(**file_paths)
data_validator = data.DataValidator(dfs)
recovery_calculator = recovery.Recovery(dfs)
correction_factor_calculator = qc.CorrectionFactor(dfs)
concentration_calc = concentration_calculator.ConcentrationCalculator(
    dfs, correction_factor_calculator.calculate_correction_factor()
)

mass_based_calculator = MassBasedCalculator(
    dfs,
    data_validator,
    recovery_calculator,
    correction_factor_calculator,
    concentration_calc,
)

pipeline = Pipeline(mass_based_calculator)

results = pipeline.execute()
results
