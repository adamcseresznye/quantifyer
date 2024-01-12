"""A module that contains common functions used by other modules.
"""
from typing import Dict, List

import pandas as pd


class BaseCalculator:
    def __init__(self, data):
        self.data = data

    def get_is_rs_name(self) -> Dict[str, List[str]]:
        """
        Returns a dictionary containing the unique values of the 'internal_standard' and 'external_standard'
        columns from the 'is_correspondence_file' table in the 'data' object.

        Parameters:
        - self: The instance of the class.

        Returns:
        - A dictionary with two keys:
            - 'is_name': A list of unique values from the 'internal_standard' column.
            - 'rs_name': A list of unique values from the 'external_standard' column.
        """
        is_name = self.data.is_correspondence_file.internal_standard.unique().tolist()
        rs_name = self.data.is_correspondence_file.external_standard.unique().tolist()
        return {"is_name": is_name, "rs_name": rs_name}

    def get_is_rs_amount(self) -> Dict[str, List[float]]:
        """
        Returns a dictionary containing the is_amount and rs_amount values.

        This function retrieves the is_rs_name by calling the get_is_rs_name() method.
        The is_concentration_file is then set as the index, and the is_rs_concentration is obtained by squeezing the resulting DataFrame.
        The is_amount and rs_amount values are filtered from the is_rs_concentration DataFrame based on the is_rs_name values.

        Returns:
            A dictionary with the following keys:
                - "is_amount": a list of is_amount values
                - "rs_amount": a list of rs_amount values
        """
        if self.data.is_concentration_file is not None:
            is_rs_name = self.get_is_rs_name()
            is_rs_concentration = self.data.is_concentration_file.set_index(
                "name"
            ).squeeze()
            is_amount = is_rs_concentration.filter(is_rs_name["is_name"], axis="index")
            rs_amount = is_rs_concentration.filter(is_rs_name["rs_name"], axis="index")
            return {"is_amount": is_amount, "rs_amount": rs_amount}

    def get_sample_names_by_sample_type(self, sample_type) -> List[str]:
        """
        Get a list of sample names based on the given sample type(s).

        Parameters:
            sample_type (str or List[str]): The type(s) of samples to filter by.

        Returns:
            List[str]: A list of sample names matching the given sample type(s).
        """
        if isinstance(sample_type, str):
            sample_type = [sample_type]

        if self.data.sample_properties_file is not None:
            return self.data.sample_properties_file.loc[
                self.data.sample_properties_file.sample_type.isin(sample_type),
                "sample_name",
            ].values.tolist()

    def get_sample_volume_by_sample_type(self, sample_type) -> pd.Series:
        """
        Retrieves the sample volume for a given sample type.

        Args:
            sample_type (str): The type of sample.

        Returns:
            pd.Series: A pandas Series object containing the sample volumes for the given sample type.
        """
        return (
            self.data.sample_properties_file.query("sample_type == @sample_type")
            .drop(columns="sample_type")
            .set_index("sample_name")
            .squeeze()
        )

    def get_sample_areas_by_sample_type(self, sample_type) -> pd.DataFrame:
        """
        Retrieves sample areas based on the given sample type.

        Args:
            sample_type (str): The type of sample.

        Returns:
            pd.DataFrame: A DataFrame containing the sample areas filtered by the sample type.
        """
        filtered_sample_names = self.get_sample_names_by_sample_type(sample_type)
        return (
            self.data.quant_file.query("type == 'area'")
            .set_index("name")
            .filter(items=filtered_sample_names, axis="columns")
        )

    def get_sample_concentrations_by_sample_type(self, sample_type) -> pd.DataFrame:
        """
        Retrieves sample concentrations by sample type.

        Parameters:
            sample_type (str): The type of sample to filter by.

        Returns:
            pd.DataFrame: A DataFrame containing the sample concentrations for the specified sample type.
        """
        filtered_sample_names = self.get_sample_names_by_sample_type(sample_type)
        return (
            self.data.quant_file.query("type == 'concentration'")
            .set_index("name")
            .filter(items=filtered_sample_names, axis="columns")
        )
