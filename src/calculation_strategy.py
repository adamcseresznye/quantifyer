from abc import ABC, abstractmethod
from functools import partial

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


class VolumeBasedCalculator(CalculationStrategy):
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

    def calculate_concentration(self):
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
            print(
                f"No plot function found for {plot_name}. Valid arguments: {', '.join(list(self.plot_functions.keys()))}."
            )


class Pipeline:
    def __init__(self, concentration_strategy: CalculationStrategy):
        self.concentration_strategy = concentration_strategy

    def execute(self):
        return self.concentration_strategy.calculate_concentration()

    def display_plot(self, plot_name, **kwargs):
        self.concentration_strategy.display_plot(plot_name, **kwargs)


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

volume_based_calculator = VolumeBasedCalculator(
    dfs,
    data_validator,
    recovery_calculator,
    correction_factor_calculator,
    concentration_calc,
)

pipeline = Pipeline(volume_based_calculator)

results = pipeline.execute()
results
