import concentration_calculator
import data
import qc
import recovery


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

    def execute(self):
        # Step 1: Validate the data
        self.data_validator.validate_data()

        # Initialize recovery as None
        recovery = None
        if self.data.is_concentration_file is not None:
            # Step 2: Calculate recovery
            recovery = self.recovery_calculator.calculate_recovery()

        correction_factors = None
        if self.data.qc_file is not None:
            # Step 3: Calculate correction factors
            correction_factors = (
                self.correction_factor_calculator.calculate_correction_factor()
            )

        # Step 4: Calculate concentrations
        concentrations = self.concentration_calculator.calculate_concentration()

        return recovery, correction_factors, concentrations
