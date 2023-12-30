#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 19:32:26 2022

@author: adamcseresznye
"""

import glob
import os
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

###################################################################
############## PART I: Read in files and tidy up ##################
###################################################################

# Folder location:
all_files = glob.glob(
    "/Users/adamcseresznye/Desktop/ 211218_e-waste-FI-LV_B2/**/a-all.txt",
    recursive=True,
)
# Read in datafiles:
li = []

colspecs = [(0, 6), (7, 19), (20, 40), (41, 46), (47, 55), (56, 64)]

for filename in all_files:
    df = pd.read_fwf(
        filename,
        colspecs=colspecs,
        skiprows=19,
        skipfooter=5,
        names=["number", "compound", "Rt", "Qion", "Response", "Concentration"],
    )
    li.append(df)
    frame = pd.concat(li, axis=1, ignore_index=True)

# Drop the 7th row:
frame.drop(index=4, inplace=True)

# Separate concentration and response values to two dfs, plus compound names:
concentration = frame.iloc[:, 5::6]
response = frame.iloc[:, 4::6]
compound = frame.iloc[:, 1]

# Generate a list of sample names
# read in file names:
names = [
    os.path.dirname(x)
    for x in glob.glob(
        "/Users/adamcseresznye/Desktop/ 211218_e-waste-FI-LV_B2/**/a-all.txt",
        recursive=True,
    )
]

# extract sample names:
names = [re.findall(".+(/.+)$", x) for x in names]

# collapse lists
names = [item for sublist in names for item in sublist]

# replace unwanted parts of the name:
names = [re.sub(r"/|.D", "", x) for x in names]

# Convert concentration df to numeric
li = [pd.to_numeric(concentration[column], errors="coerce") for column in concentration]

# concatanate the list to a df
concentration = pd.concat(li, axis=1, ignore_index=True)

# rename column names and indexes of concentration and response dfs
response.columns = names
concentration.columns = names
concentration.index = compound
response.index = compound
concentration.index.name = "Response_ID"
response.index.name = "Response_ID"

###################################################################
###Alternatively, read in already processed csv files:
# concentration = pd.read_csv('/Users/adamcseresznye/Desktop/Work/eWaste/211215_e_waste_2nd_batch/ 211218_e-waste-FI-LV_B2/Concentration.csv')
# response = pd.read_csv('/Users/adamcseresznye/Desktop/Work/eWaste/211215_e_waste_2nd_batch/ 211218_e-waste-FI-LV_B2/Response.csv')


###################################################################
############## PART II: Calculating Recoveries ####################
###################################################################
# Response factor
concentration_filter = response.filter(regex="IS-RS").iloc[:3, :]
concentration_filter.index.name = "Response_ID"

# Set concentration values for internal standards:
df = pd.DataFrame(
    {
        "Reponse_ID": {0: "mass_CB 143 (IS)", 1: "mass_13C HCB", 2: "mass_CB 207 (RS)"},
        "mass": {0: "12500", 1: "2500", 2: "2500"},
    }
).set_index("Reponse_ID")
# Fill up the dataframe with values so that it has same dimension as the concentration_filter dataframe
for i in list(range(concentration_filter.shape[1] - 1)):
    df[i] = df.mass
    i += 1
# change column names:
df.set_axis(concentration_filter.columns, axis=1, inplace=True)
# put dataframes in a list so that we can concatanate them:
frames = [concentration_filter, df]
RF_df = pd.concat(frames, axis=0, copy=False).apply(pd.to_numeric)

# Calculate the RRF for the ISs:
d = pd.DataFrame()
for i in RF_df:
    temp = pd.DataFrame(
        {
            "CB143(IS)_RRF": [
                (RF_df[i][0] * RF_df[i][5]) / (RF_df[i][3] * RF_df[i][2])
            ],
            "13CHCB_RRF": [(RF_df[i][1] * RF_df[i][5]) / (RF_df[i][4] * RF_df[i][2])],
        }
    )
    d = pd.concat([d, temp], ignore_index=True)
# Calculate the average RRF for the ISs:
average_RRF = []
for i in d:
    df = d[i].mean()
    average_RRF.append(df)
# Extract the average RRFs to a dataframe:
AVG_RRF = d.describe().loc["mean"]

# Calculating expected recoveries:
no_IS = response.loc[:, ~response.columns.str.contains("IS-RS")].iloc[:3, :]

# Calculating the actual amounts of ISs extracted from each samples:
expected_pg = pd.DataFrame()
for i in no_IS:
    temp = pd.DataFrame(
        {
            "CB143(IS)_extracted_pg": [
                (no_IS.loc["CB 143 (IS)"][i] * 2500)
                / (no_IS.loc["CB 207 (RS)"][i] * AVG_RRF.loc["CB143(IS)_RRF"])
            ],
            "13CHCB_extracted_pg": [
                (no_IS.loc["13C HCB"][i] * 2500)
                / (no_IS.loc["CB 207 (RS)"][i] * AVG_RRF.loc["13CHCB_RRF"])
            ],
        }
    )
    expected_pg = pd.concat([expected_pg, temp], ignore_index=True)

# Create two series that contain the IS recoveries from all samples
CB143_recovery = pd.Series((expected_pg.loc[:, "CB143(IS)_extracted_pg"] / 12500) * 100)
HCB_recovery = pd.Series((expected_pg.loc[:, "13CHCB_extracted_pg"] / 2500) * 100)

# zipping these two series together
Recovery = pd.DataFrame(
    list(zip(CB143_recovery, HCB_recovery)),
    columns=["CB143(IS)_Recovery", "13CHCB_Recovery"],
)

# Assign sample names as indexes:
Recovery = Recovery.set_index(no_IS.columns)

# Summary of the Extraction efficiencies:
Recovery.describe()

fig = plt.figure()
ax = plt.subplot(111)
ax.boxplot(Recovery)
xticks = list(Recovery.columns)
ax.set_xticklabels(xticks, fontsize=10)
ax.set_title("Recovery of internal standards in all samples measured")
ax.set_ylabel("% Recovery")

###################################################################
############## PART III: Calculating Correction factors ###########
###################################################################
# Get the pg values measured in the samples:
QC_pg = concentration.filter(regex="AMAP").iloc[4:, :]
QC_pg.index.name = "Response_ID"

# First, let's calculate the analyte concentrations measured in the blanks:
blank_filtered = concentration.filter(regex="blank").iloc[4:, :]
blank_filtered.index.name = "Response_ID"

# Calculate how many pg of analytes are there present in the samples (on average)
blank_values = []
for i in range(len(blank_filtered)):
    temp = blank_filtered.iloc[i, :].mean()
    blank_values.append(temp)

# Let's convert it to a pandas series
blank_values = pd.Series(blank_values, index=QC_pg.index).rename({"0": "blank_pg"})

# Get the blank corrected QC values in ng/ml:
QC_corrected_conc = (QC_pg.sub(blank_values, axis=0)) / (0.5 * 1000)
# could be calculated like this too: ((QC_pg.T - blank_values).T)/ (0.5 * 1000)
# check out https://bit.ly/3utACIR

# Let's make a series that contains the theretical assigned values of analytes
# in the QC
theoretical_assigned = {
    "CB 101": 1.44,
    "CB 99": 0.508,
    "CB 118": 0.331,
    "CB 153": 0.759,
    "CB 138": 0.865,
    "CB 187": 0.506,
    "CB 183": 0.463,
    "CB 180": 1.27,
    "CB 170": 0.33,
    "CB 194": 1,
    "HCB": 1,
    "alpha-HCH": 1,
    "beta-HCH": 1,
    "gamma-HCH": 1,
    "OxC": 0.637,
    "TN": 1.95,
    "CN": 2.67,
    "ppDDT": 0.535,
}
theoretical_assigned = pd.Series(data=theoretical_assigned)

# Calculate the mean of blank corrected concentrations (ng/ml)
QC_corrected_conc_mean = []
for i in range(len(QC_pg)):
    temp = QC_corrected_conc.iloc[i, :].mean()
    QC_corrected_conc_mean.append(temp)

# Transform the list created in the previous step to a series:
QC_corrected_conc_mean = pd.Series(QC_corrected_conc_mean, index=QC_pg.index)

# Calculate the correction factors and set values from CB 194 to gamma-HCH to 1
# these compounds are not present in the AMAP samples
correction_factor = theoretical_assigned / QC_corrected_conc_mean
correction_factor[range(9, 14)] = 1

# Let's plot the calculated correction factors:
fig = plt.figure()
ax1 = plt.subplot(2, 3, 2)
ax2 = plt.subplot(2, 1, 2)
fig.suptitle("Calculated correction factors", fontweight="bold")
ax1.boxplot(correction_factor)
ax2.bar(range(len(correction_factor)), correction_factor)
xticks = list(correction_factor.index)
ax1.set_xticklabels([])
ax2.set_xticklabels(xticks, fontsize=7, rotation=-90)
ax2.set_xticks(
    np.arange(min(list(range(len(xticks)))), max(list(range(len(xticks)))) + 1, 1)
)
ax1.set_title("Boxplot of calculated correction factors", size=10)
ax2.set_title("Calculated correction factors for individual natives", size=10)
ax1.title.set_text("Boxplot of calculated correction factors:")
ax2.title.set_text("Calculated correction factors for individual natives:")
ax1.set_ylabel("Correction factor", fontsize=8)
ax2.set_ylabel("Correction factor", fontsize=8)
ax1.tick_params(axis="both", which="major", labelsize=8)
ax2.tick_params(axis="both", which="major", labelsize=8)

###################################################################
########## PART IV: Calculating Sample Concentrations #############
###################################################################

# create dataframe that only contains the samples:
sample_concentration_pg = concentration.drop(
    list(concentration.filter(regex="(IS-RS|blank|AMAP)")), axis=1
).tail(concentration.shape[0] - 4)
sample_concentration_pg.index.name = "Concentration_ID"

# Let's calculate the corrected sample concentrations[pg].
corrected_sample_concentration_pg = sample_concentration_pg.sub(
    blank_values, axis=0
).mul(correction_factor, axis=0)

# As one of the last steps, we have to imput the amount of sample extracted.
# Let's do this through a csv file.

sample_list = corrected_sample_concentration_pg.columns.tolist()

# We can convert the list object to series and save it as csv:
sample_list_empty = pd.Series(sample_list).to_csv("sample_list_empty.csv", index=False)

# Read in the file and convert it to series:
sample_list_filled_in = pd.read_csv(
    "/Users/adamcseresznye/Desktop/Python/Pandas_for_everyone/sample_list_empty.csv",
    index_col=0,
).squeeze()

# Divide the calculated sample concentrations [pg] with the amount of sample extracted.
# Now we get ng/ml
corrected_sample_concentration_ngml = corrected_sample_concentration_pg.div(
    sample_list_filled_in, axis=1
)

# Final step: replace negative ng/ml values with zeros:
corrected_sample_concentration_ngml[corrected_sample_concentration_ngml < 0] = 0

# Boxplot of the analyte concentrations per sample:
corrected_sample_concentration_ngml.plot.box(
    rot=90, fontsize=5, ylabel="c [pg/ml]", title="Concentrations according to samples"
)

# Sumarize the targets:
target_summary = corrected_sample_concentration_ngml.T.describe()

# Boxplot of the sample concentration per analyte:
corrected_sample_concentration_ngml.T.plot.box(
    rot=90, ylabel="c [pg/ml]", title="Concentrations according to natives"
)
