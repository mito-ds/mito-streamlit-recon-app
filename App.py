from typing import List
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

from utils import get_most_recent_outputs_paths, METADATE_FILE_PATH
from custom_spreadsheet_functions import MATCH, IMMATERIAL, FAIL

st.set_page_config(layout="wide")
st.title("Recon Dashboard")

# For each folder in the outputs folder, get the csv file that has the latest date and time based on the filename
most_recent_ouput_paths_dict = get_most_recent_outputs_paths()
most_recent_output_dfs_dict = {key: pd.read_csv(path) if path else None for key, path in most_recent_ouput_paths_dict.items()}

# Create list of non-None dataframes
most_recent_output_dfs = [df for df in most_recent_output_dfs_dict.values() if df is not None]

def get_total_number_of_rules_applied(*argv: List[pd.DataFrame]):
    # Sum the unique values in the Check column for each dataframe
    total_number_of_rules_applied = 0
    for df in argv:
        # Get the unique values in the Check column
        total_number_of_rules_applied += df['Check'].nunique()

    return total_number_of_rules_applied

def get_total_number_of_records_checked(*argv: List[pd.DataFrame]):
    # Sum the Count column for each dataframe
    total_number_of_checks = 0
    for df in argv:
        total_number_of_checks += df['Count'].sum()

    return total_number_of_checks

def get_total_number_of_checks_for_outcome(*argv: List[pd.DataFrame], outcome):
    total_number_of_matching_checks = 0

    if outcome == MATCH or outcome == IMMATERIAL:
        
        for df in argv:
            df = df[df['Outcome'] == outcome]
            total_number_of_matching_checks += df['Count'].sum()

    return total_number_of_matching_checks

def get_total_number_of_failing_checks(*argv: List[pd.DataFrame]):
    total_number_of_failing_checks = 0

    for df in argv:
        df = df[(df['Outcome'] != MATCH) & (df['Outcome'] != IMMATERIAL)]
        total_number_of_failing_checks += df['Count'].sum()

    return total_number_of_failing_checks

def get_total_number_of_hours_saved():
    # If we haven't yet created the METADATE_FILE_PATH, then return 0
    if not os.path.exists(METADATE_FILE_PATH):
        return 0

    recon_metadata_df = pd.read_csv(METADATE_FILE_PATH)
    return recon_metadata_df['recon_value'].sum()

st.divider()

metric_one, metric_two, metric_three = st.columns((1,1,1))
metric_one.metric("Number of Rules Applied", get_total_number_of_rules_applied(*most_recent_output_dfs))
metric_two.metric("Number of Records Checked", get_total_number_of_records_checked(*most_recent_output_dfs))
metric_three.metric("Number of Hours Saved", get_total_number_of_hours_saved())

num_matching_checks =  get_total_number_of_checks_for_outcome(*most_recent_output_dfs, outcome=MATCH)
num_immaterial_checks = get_total_number_of_checks_for_outcome(*most_recent_output_dfs, outcome=IMMATERIAL)
num_failing_checks = get_total_number_of_failing_checks(*most_recent_output_dfs)

metric_one, metric_two, metric_three = st.columns((1,1,1))
metric_one.metric("Number of MATCHING checks", num_matching_checks)
metric_two.metric("Number of IMMATERIAL checks", num_immaterial_checks)
metric_three.metric("Number of FAILING checks", num_failing_checks)

st.divider()

total_summary_df = pd.DataFrame({'Outcome': [MATCH, IMMATERIAL, FAIL], 'Count': [num_matching_checks, num_immaterial_checks, num_failing_checks]})

fig = go.Figure()

fig.add_trace(go.Bar(
    x=total_summary_df['Outcome'],
    y=total_summary_df['Count'],
    xperiodalignment="middle", # Make sure that the x axis labels are centered with the bars, only availabe when using graph objects
))

fig.update_xaxes(title_text="Outcome")
fig.update_yaxes(title_text="Total number of records")
fig.update_layout(title_text="Outcome Distribution", title_font_size=20)

st.plotly_chart(fig, use_container_width=True)