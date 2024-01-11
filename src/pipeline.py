"""A module for executing the dataprpocessing pipeline.

This module provides a simple interface for executing the dataprocessing pipeline.
It returns recovery, correction factors and concentrations.
"""
from functools import partial


class Pipeline:
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

    def execute(self):
        # Step 1: Validate the data
        self.data_validator.validate_data()

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

    def display_plot(self, plot_name, **kwargs):
        plot_function = self.plot_functions.get(plot_name)
        if plot_function:
            plot_function(**kwargs)
        else:
            print(f"No plot function found for {plot_name}.")
