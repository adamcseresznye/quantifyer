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


class MassBasedCalculatorPipeline(CalculationStrategy):
    """
    Initiates the MassBasedCalculatorPipeline class to perform mass-based calculations,
    such as recovery, correction factors, and concentrations (if necessary). This is
    especially useful when accounting for analyte concentrations is based on internal standard
    mass spiked in the samples during sample preparation.

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
            "figsize": (5, 5),
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


class StrategySelector:
    """This initializes the StrategySelector class, which provides
    the ability to choose from a variety of quantitation methods.
    At present, only the MassBasedCalculatorPipeline is available, allowing
    for the calculation of analyte concentration (pg/ml) based on the mass of
    the internal standard (pg) spiked into samples during sample preparation."""

    def __init__(self, strategy: CalculationStrategy):
        """
        Initializes an instance of the class.

        Args:
            strategy (CalculationStrategy): The calculation strategy to be used.

        Returns:
            None
        """
        self.strategy = strategy

    def execute(self):
        """
        Executes the function and returns the concentration calculated by the strategy.

        Returns:
            The concentration calculated by the strategy.
        """
        return self.strategy.calculate_concentration()

    def display_plot(self, plot_name, **kwargs):
        """
        Display a plot with the given plot name.

        Parameters:
            plot_name (str): The name of the plot to be displayed.
            **kwargs: Additional keyword arguments to be passed to the display function.

        Returns:
            None
        """
        self.strategy.display_plot(plot_name, **kwargs)
