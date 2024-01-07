import concentration_calculator
import data
import qc
import recovery


class Pipeline:
    def __init__(
        self,
        quant_file,
        is_correspondence_file,
        sample_properties_file,
        qc_file=None,
        is_concentration_file=None,
    ):
        self.data = data.Data(
            quant_file,
            is_correspondence_file,
            sample_properties_file,
            qc_file,
            is_concentration_file,
        )
        self._data_validator = None
        self._recovery_calculator = None
        self._correction_factor_calculator = None
        self._concentration_calculator = None

    @property
    def data_validator(self):
        if self._data_validator is None:
            self._data_validator = data.DataValidator(self.data)
        return self._data_validator

    @property
    def recovery_calculator(self):
        if self._recovery_calculator is None:
            self._recovery_calculator = recovery.Recovery(self.data)
        return self._recovery_calculator

    @property
    def correction_factor_calculator(self):
        if self._correction_factor_calculator is None:
            self._correction_factor_calculator = qc.CorrectionFactor(self.data)
        return self._correction_factor_calculator

    @property
    def concentration_calculator(self):
        if self._concentration_calculator is None:
            self._concentration_calculator = (
                concentration_calculator.ConcentrationCalculator(
                    self.data,
                    self.correction_factor_calculator.calculate_correction_factor(),
                )
            )
        return self._concentration_calculator

    def execute(self):
        #     # Step 1: Validate the data
        self.data_validator.validate_data()

        #     # Step 2: Calculate recovery
        recovery = self.recovery_calculator.calculate_recovery()

        # Step 3: Calculate correction factors
        correction_factors = (
            self.correction_factor_calculator.calculate_correction_factor()
        )

        # Step 4: Calculate concentrations
        concentrations = self.concentration_calculator.calculate_concentration()

        return concentrations
