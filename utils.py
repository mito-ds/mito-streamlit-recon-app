from typing import List, Optional
import pandas as pd
from datetime import datetime
import os
from custom_spreadsheet_functions import IMMATERIAL, MATCH
import plotly.express as px
import inspect

METADATE_FILE_PATH = 'recon_metadata.csv'

# Path to the "outputs" folder
OUTPUTS_FOLDER = 'outputs/'

def get_value_count(value_counts: pd.Series, value: str) -> int:
    if value in value_counts:
        return value_counts[value]
    return 0

def get_recon_report(recon_df: pd.DataFrame) -> List[pd.DataFrame]:
    """
    Given a recon dataframe, returns a list of dataframes with the following structure:
    1. A summary dataframe that shows the number of records that matched, were immaterial, or failed for each check
    2. For each (check, outcome) a separate dataframe that only shows records for that (check, outcome)
    """
    recon_summary_df = pd.DataFrame(columns=['Date', 'Check', 'Outcome', 'Count'])

    # Label the report with the current datetime
    now = datetime.now()

    outcome_dfs = [recon_summary_df, recon_df]

    # For each series in the dataframe, if the column contains the word check, build the summary
    for column_header in recon_df.columns:
        if 'check' in column_header.lower():
            value_counts = recon_df[column_header].value_counts()

            matching_value_counts = get_value_count(value_counts, MATCH)
            immaterial_value_counts = get_value_count(value_counts, IMMATERIAL)
            failing_value_counts = value_counts.sum() - matching_value_counts - immaterial_value_counts

            matching_checks_summary = [now, column_header, MATCH, matching_value_counts]
            immaterial_checks_summary  = [now, column_header, IMMATERIAL, immaterial_value_counts]
            failing_checks_summary = [now, column_header, 'Failing', failing_value_counts]

            recon_summary_df.loc[len(recon_summary_df)] = matching_checks_summary
            recon_summary_df.loc[len(recon_summary_df)] = immaterial_checks_summary
            recon_summary_df.loc[len(recon_summary_df)] = failing_checks_summary

            matching_checks_df = recon_df[recon_df[column_header] == MATCH]
            immaterial_checks_df = recon_df[recon_df[column_header] == IMMATERIAL]
            failing_checks_df = recon_df[(recon_df[column_header] != MATCH ) & (recon_df[column_header] != IMMATERIAL)]

            # Add an check column to each dataframe at the front of the dataframe
            matching_checks_df.insert(0, 'Check Outcome', f'{column_header} - {MATCH}')
            immaterial_checks_df.insert(0, 'Check Outcome', f'{column_header} - {IMMATERIAL}')
            failing_checks_df.insert(0, 'Check Outcome', f'{column_header} - Failing')

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

def save_recon_report(recon_summary_df: pd.DataFrame, recon_name: str):
    # Save the csv as the current date and time in the outputs/RECON_NAME folder
    now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    recon_summary_df.to_csv(f'./outputs/{recon_name}/{now}.csv', index=False)

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

def save_recon_script(recon_name, code):
    path = get_recon_path(recon_name)
    with open(path, 'w') as file:
        file.write(code)
   
def get_recon_script(recon_name):
    path = get_recon_path(recon_name)
    with open(path, 'r') as file:
        return file.read()

def get_recon_path(recon_name):
    return os.path.join('recon-scripts', recon_name + '.py')

def get_new_function(function_string: str):
    functions_before = [f for f in locals().values() if callable(f)]
    exec(function_string)
    functions = [f for f in locals().values() if callable(f) and f not in functions_before]

    for f in functions:
        # Return the Mito generated recon function so that we don't get tripped up 
        # by other functions that are imported, ie: custom sheet functions
        if "MITO_GENERATED_RECON_FUNCTION_" in f.__name__:
            return f

def remove_import_code_and_get_df_names(function_string: str) -> tuple[str, list[str]]:
    # Find the lines that start with "Imported" and then remove that line and the next one
    lines = function_string.split('\n')
    new_lines = []
    df_names = []
    skip_next_line = False
    for line in lines: 
        if skip_next_line or "pd.read_csv" in line:
            # Reset the skip_next_line flag 
            skip_next_line = False
            
            # Get the df name from the line 
            df_name = line.split('=')[0].strip()
            df_names.append(df_name)

            # Don't add this line
            continue 

        # Check if the word "Imported" is in the line
        if "Imported" in line:
            skip_next_line = True
        else:
            new_lines.append(line)

    return '\n'.join(new_lines), df_names


def finalize_code_string(function_string, new_imports_string, rename_imports_string) -> str: 
    """
    1. Adds an import statement for custom importers and sheet functions 
    2. Adds the new imported dataframes that we're going to replay the analysis on
    3. Rename the newly imported dataframes to the original names so we can rerun the code 
    """
    # After the def line, add the new_imports_string and rename_imports_string
    lines = function_string.split('\n')
    new_lines = []

    for line in lines:
        new_lines.append(line)
        if "def " in line:
            # Add a tab before each line in new_imports_string and rename_imports_string
            new_lines.append('    from mitosheet.public.v3 import SUBSTITUTE')
            new_lines.append('    import pandas as pd')
            new_lines.append('    from custom_imports import get_sales_data, get_european_real_estate_data')
            new_lines.append('    from custom_spreadsheet_functions import CHECK_NUMBER_DIFFERENCE, CHECK_STRING_DIFFERENCE')

            new_imports_string = '\n'.join(['    ' + l for l in new_imports_string.split('\n')])
            rename_imports_string = '\n'.join(['    ' + l for l in rename_imports_string.split('\n')])
            new_lines.append(new_imports_string)
            new_lines.append(rename_imports_string)
    return '\n'.join(new_lines)

def remove_package_imports(python_code) -> str:
    # Remove the package imports from the code
    lines = python_code.split('\n')
    new_lines = []
    for line in lines:
        if "import " in line:
            continue
        if "from " in line:
            continue
        new_lines.append(line)
    return '\n'.join(new_lines)
