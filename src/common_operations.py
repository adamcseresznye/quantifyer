"""A module that contains common functions used by other modules.
"""

import pandas as pd


class BaseCalculator:
    def __init__(self, data):
        self.data = data

    def get_is_rs_name(self):
        is_name = self.data.is_correspondence_file.internal_standard.unique().tolist()
        rs_name = self.data.is_correspondence_file.external_standard.unique().tolist()
        return {"is_name": is_name, "rs_name": rs_name}

    def get_is_rs_amount(self):
        if self.data.is_concentration_file is not None:
            is_rs_name = self.get_is_rs_name()
            is_rs_concentration = self.data.is_concentration_file.set_index(
                "name"
            ).squeeze()
            is_amount = is_rs_concentration.filter(is_rs_name["is_name"], axis="index")
            rs_amount = is_rs_concentration.filter(is_rs_name["rs_name"], axis="index")
            return {"is_amount": is_amount, "rs_amount": rs_amount}

    def get_sample_names_by_sample_type(self, sample_type):
        if isinstance(sample_type, str):
            sample_type = [sample_type]

        if self.data.sample_properties_file is not None:
            return self.data.sample_properties_file.loc[
                self.data.sample_properties_file.sample_type.isin(sample_type),
                "sample_name",
            ].values.tolist()

    def get_sample_volume_by_sample_type(self, sample_type):
        return (
            self.data.sample_properties_file.query("sample_type == @sample_type")
            .drop(columns="sample_type")
            .set_index("sample_name")
            .squeeze()
        )

    def get_sample_areas_by_sample_type(self, sample_type):
        filtered_sample_names = self.get_sample_names_by_sample_type(sample_type)
        return (
            self.data.quant_file.query("type == 'area'")
            .set_index("name")
            .filter(items=filtered_sample_names, axis="columns")
        )

    def get_sample_concentrations_by_sample_type(self, sample_type):
        filtered_sample_names = self.get_sample_names_by_sample_type(sample_type)
        return (
            self.data.quant_file.query("type == 'concentration'")
            .set_index("name")
            .filter(items=filtered_sample_names, axis="columns")
        )
