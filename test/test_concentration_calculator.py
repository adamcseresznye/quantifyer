"""A module for testing the concentration_calculator.py module."""

from io import StringIO

import numpy as np
import pandas as pd
import pytest

import concentration_calculator
import data


# Fixture to initialize Data object
@pytest.fixture
def data_obj():
    test_data = {
        "quant_file": StringIO(
            "name,type,QC_1,QC_2,QC_3,ISRS_1,ISRS_2,ISRS_3,blank_1,blank_2,blank_3,sample_1,sample_2,sample_3\ninternal_standard_name,Area,20,40,60,20,40,60,20,40,60,20,40,60\nreconstitution_standard_name,Area,100,100,100,100,100,100,100,100,100,100, 100, 100\nnative_name,area,50,50,50,50,50,50,50,50,50,50,50,50\nnative_name,concentration,50,50,50,0,0,0,0.1,0.1,0.1,45,45,45"
        ),
        "is_correspondence_file": StringIO(
            "native,internal_standard,external_standard\nnative_name,internal_standard_name,reconstitution_standard_name"
        ),
        "sample_properties_file": StringIO(
            "sample_name,sample_type,volume\nQC_1,qc,0.5\nQC_2,qc,0.5\nQC_3,qc,0.5\nISRS_1,isrs,0.5\nISRS_2,isrs,0.5\nISRS_3,isrs,0.5\nblank_1,blank,0.5\nblank_2,blank,0.5\nblank_3,blank,0.5\nsample_1,sample,0.5\nsample_2,sample,0.5\nsample_3,sample,0.5"
        ),
        "qc_file": StringIO("native,concentration\nnative_name,0.1"),
        "is_concentration_file": StringIO(
            "name,amount\ninternal_standard_name,1000\nreconstitution_standard_name,1000"
        ),
    }
    return data.Data(**test_data)
