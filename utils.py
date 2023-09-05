from typing import List, Optional
import pandas as pd
from datetime import datetime
import os
from custom_spreadsheet_functions import IMMATERIAL, MATCH
import plotly.express as px

METADATE_FILE_PATH = 'recon_metadata.csv'

# Path to the "outputs" folder
OUTPUTS_FOLDER = 'outputs/'


def clean_merged_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    # Sort the dataframe by column names so that matching attributes are next to eachother
    df.sort_index(axis=1, inplace=True)

    return df


def get_value_count(value_counts: pd.Series, value: str) -> int:
    if value in value_counts:
        return value_counts[value]
    return 0

def get_recon_report(df: pd.DataFrame) -> List[pd.DataFrame]:
    check_summary_df = pd.DataFrame(columns=['Date', 'Check', 'Outcome', 'Count'])

    # Label the report with the current datetime
    now = datetime.now()

    outcome_dfs = [check_summary_df, df]

    # For each series in the dataframe, if the column contains the word check, build the summary
    for column_header in df.columns:
        if 'check' in column_header.lower():
            value_counts = df[column_header].value_counts()

            matching_value_counts = get_value_count(value_counts, MATCH)
            immaterial_value_counts = get_value_count(value_counts, IMMATERIAL)
            failing_value_counts = value_counts.sum() - matching_value_counts - immaterial_value_counts

            matching_checks_summary = [now, column_header, MATCH, matching_value_counts]
            immaterial_checks_summary  = [now, column_header, IMMATERIAL, immaterial_value_counts]
            failing_checks_summary = [now, column_header, 'Failing', failing_value_counts]

            check_summary_df.loc[len(check_summary_df)] = matching_checks_summary
            check_summary_df.loc[len(check_summary_df)] = immaterial_checks_summary
            check_summary_df.loc[len(check_summary_df)] = failing_checks_summary

            matching_checks_df = df[df[column_header] == MATCH]
            immaterial_checks_df = df[df[column_header] == IMMATERIAL]
            failing_checks_df = df[(df[column_header] != MATCH ) & (df[column_header] != IMMATERIAL)]

            outcome_dfs.extend([matching_checks_df, immaterial_checks_df, failing_checks_df])

    return outcome_dfs

def get_recon_names() -> List[str]:
    # Get a list of subdirectories in the "outputs" folder
    return [subdir for subdir in os.listdir(OUTPUTS_FOLDER) if os.path.isdir(os.path.join(OUTPUTS_FOLDER, subdir))]

def get_most_recent_outputs_paths(): 
    most_recent_output_paths_dict = {}

    # Get a list of subdirectories in the "outputs" folder
    recon_names = get_recon_names()

    # Iterate through subdirectories and find the most recent CSV file
    for recon_name in recon_names:
        most_recent_output_paths_dict[recon_name] = get_most_recent_output_path_by_name(recon_name)

    return most_recent_output_paths_dict

def get_most_recent_output_path_by_name(recon_name: str) -> Optional[str]:
    subfolder_path = os.path.join(OUTPUTS_FOLDER, recon_name)
    csv_files = [file for file in os.listdir(subfolder_path) if file.endswith('.csv')]
    return get_most_recent_csv_file_path(subfolder_path, csv_files)
    
def get_most_recent_csv_file_path(subfolder_path: str, csv_files: List[str]) -> Optional[str]:
    if csv_files:
        # Find the most recent CSV file
        most_recent_csv = max(csv_files, key=lambda x: os.path.getctime(os.path.join(subfolder_path, x)))            
        most_recent_csv_path = os.path.join(subfolder_path, most_recent_csv)

        return most_recent_csv_path
    return None

def get_recon_summary_graph(check_summary_df: pd.DataFrame):
    # Visualize the summary report using Plotly code generated by Mito
    fig = px.bar(check_summary_df, x='Check', y='Count', color='Outcome', barmode='group')
    
    fig.update_layout(
        title='Recon Report Summary', 
        xaxis={
            "showgrid": True, 
        }, 
        yaxis={
            "showgrid": True
        }, 
        legend={
            "orientation": 'v'
        }, 
        barmode='group', 
        paper_bgcolor='#FFFFFF'
    )

    return fig
            
def add_recon_to_metadata(recon_name, recon_description, recon_value):
    # Check if the metadata file, recon_metadata.csv exists
    if not os.path.exists(METADATE_FILE_PATH):

        df = pd.DataFrame(columns = ['recon_name', 'recon_description', 'recon_value', 'date_created'])
        df.to_csv(METADATE_FILE_PATH, index=False)

    # Add the new recon to the metadata file
    df = pd.read_csv(METADATE_FILE_PATH)

    # Make sure the recon was not already logged
    if recon_name in df['recon_name'].values:
        return 

    new_row = [recon_name, recon_description, recon_value, datetime.now()]
    df.loc[len(df)] = new_row
    df.to_csv(METADATE_FILE_PATH, index=False)

    



