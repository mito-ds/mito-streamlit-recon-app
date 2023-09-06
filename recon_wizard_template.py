import streamlit as st
import pandas as pd
from mitosheet.streamlit.v1 import spreadsheet
import plotly.express as px
from datetime import datetime
from custom_imports import get_sales_data
from custom_spreadsheet_functions import CHECK_NUMBER_DIFFERENCE, CHECK_STRING_DIFFERENCE
from utils import * 

RECON_NAME = "MITO_PLACEHOLDER__REPLACE_WITH_RECON_NAME"
RECON_DESCRIPTION = "MITO_PLACEHOLDER__REPLACE_WITH_RECON_DESCRIPTION"
RECON_VALUE = "MITO_PLACEHOLDER__REPLACE_WITH_RECON_VALUE"
UPDATE_RECON_KEY = f"update_{RECON_NAME}"

st.set_page_config(layout="wide")
st.title(RECON_NAME)

if UPDATE_RECON_KEY not in st.session_state:
    st.session_state[UPDATE_RECON_KEY] = False

# Get the previous run of the report if it exists
previous_recon_report_path = get_most_recent_output_path_by_name(RECON_NAME)

if RECON_NAME not in st.session_state:
    st.session_state[RECON_NAME] = False

if previous_recon_report_path or st.session_state[UPDATE_RECON_KEY]:
    # If we've already ran this report, display the summary of the most recent run.
    recon_report_summary_df = pd.read_csv(previous_recon_report_path)

    # Get the csv name from the report path
    previous_recon_report_name = previous_recon_report_path.split('/')[-1]

    # Format the name as a date
    previous_recon_report_date = datetime.strptime(previous_recon_report_name, "%Y-%m-%d-%H-%M-%S.csv")

    st.info(f'''
        Recon Description: {RECON_DESCRIPTION} 

        Hours per quarter saved with automation: {RECON_VALUE}'''
    )

    if st.button("Rerun recon with new datsets"):
        st.session_state[UPDATE_RECON_KEY] = True

    if st.session_state[UPDATE_RECON_KEY]:
        recon_function_string = get_recon_script(RECON_NAME)

        recon_function_string, original_imported_df_names = remove_import_code_and_get_df_names(recon_function_string)

        new_df_names_and_dfs, new_imports_string = spreadsheet(import_folder='./data', key='update_recon')
        new_df_names = list(new_df_names_and_dfs.keys())

        if st.button("Rerun Recon"):     

            # Remove the package imports since we've already imported them in the recon_function
            new_imports_string = remove_package_imports(new_imports_string)

            # Rename the imports to the original names
            rename_imports_strings = []
            original_and_new_df_names = {df_name: df for df_name, df in zip(original_imported_df_names, new_df_names)}
            for original_imported_df_names, new_df in original_and_new_df_names.items():
                rename_imports_strings.append(f'{original_imported_df_names} = {new_df}')

            rename_imports_string = '\n'.join(rename_imports_strings)

            recon_function_string = finalize_code_string(recon_function_string, new_imports_string, rename_imports_string)


            recon_function = get_new_function(recon_function_string)
            recon_function_dfs = recon_function()

            # Get the last dataframe from the recon_function_dfs
            recon_result_df = recon_function_dfs[-1]

            check_summary_df = get_recon_report(recon_result_df)[0]

    st.markdown(f"""This recon was last run on {previous_recon_report_date}""")

    dfs, _ = spreadsheet(recon_report_summary_df)
    dfs_list = list(dfs.values())
    check_summary_df = dfs_list[0]

    # Create graph and display it
    fig = get_recon_summary_graph(check_summary_df)
    st.plotly_chart(fig, use_container_width=True)

else:
    # If this report has never been generated, guide the user through the steps to create it.

    st.markdown("""This is the recon setup wizard. It will guide you through a series of steps to set up your recon report.""")

    def get_instruction_prompt(num_dfs: int) -> str:
        if num_dfs == 0:
            return "Import the **first** data source by clicking **Import** in the Mito toolbar and selecting an import method."

        if num_dfs == 1:
            return "Import the **second** data source by clicking **Import** in the Mito toolbar and selecting an import method."

        if num_dfs == 2:
            return """Merge the two datasets together by clicking **Dataframes** > **Merge**. Then select the columns from each dataframe that you want to merge on."""
        
        if num_dfs == 3:
            return """
            Now that you've constructed the dataset, setup data checks by adding a new column and using the formulas =CHECK_NUMBER_DIFFERENCE() and =CHECK_STRING_DIFFERENCE().
            
            **Make sure to include the word "check" in the column name so that recon app registers it as a report**.
            """

    # Create a placeholder streamlit widget so we can later fill in the 
    # wizard instructions and display it to the user above the spreadsheet.
    instruction_prompt = st.empty()
    formula_documation = st.empty()

    # Display the data inside of the spreadsheet so the user can easily fix data quality issues.
    dfs, code = spreadsheet(
        importers=[get_sales_data], 
        import_folder='./data', 
        sheet_functions=[CHECK_NUMBER_DIFFERENCE, CHECK_STRING_DIFFERENCE],
        code_options={'as_function': True, 'call_function': False, 'function_name': f'MITO_GENERATED_RECON_FUNCTION_{RECON_NAME}', 'function_params': {}},
        key='setup_recon'
    )

    num_dfs = len(dfs)
    instruction_prompt.success(get_instruction_prompt(num_dfs))

    if len(dfs) == 3:
        with formula_documation.expander("Formula Documentation"):
            st.markdown("""
                ### CHECK_NUMBER_DIFFERENCE 
                
                CHECK_NUMBER_DIFFERENCE(number_column_one, number_column_two, tolerance)
                Syntax:
                - number_column_one: The first column to compare
                - number_column_two: The second column to compare
                - tolerance: The amount of difference allowed between the two columns.

                Returns:
                - Match if the two columns are exactly equal
                - Immaterial if the two columns are within the tolerance
                - The difference if the two columns are not within the tolerance

                Ex: 
                - =CHECK_NUMBER_DIFFERENCE(price_excel, price_database, 0.5)
                
                ### CHECK_STRING_DIFFERENCE 
                
                CHECK_STRING_DIFFERENCE(string_column_one, string_column_two, similarity_threshold)
                Syntax:
                - string_column_one: The first column to compare
                - string_column_two: The second column to compare
                - similarity_threshold: The minimum required similarity between the two strings. Two identical strings have a similarity of 100.

                Returns:
                - Match if the two columns are exactly equal
                - Immaterial if the two columns are within the tolerance
                - The similarity ratio if the two columns are not above the similarity threshold

                Ex: 
                - =CHECK_STRING_DIFFERENCE(salesperson_excel, salesperson_database, 90)
            """
        )

    dfs = list(dfs.values())
    recon_raw_data_df = dfs[2] if len(dfs) >= 3 else None
        
    if st.button("Generate Recon Report", disabled=recon_raw_data_df is None):
        # Save the recon metadata to the metadata file so we can display info about it in the app dashboard
        add_recon_to_metadata(RECON_NAME, RECON_DESCRIPTION, RECON_VALUE)
        save_recon_script(RECON_NAME, code)

        dfs = get_recon_report(recon_raw_data_df)

        spreadsheet(*dfs)

        recon_summary_df = dfs[0]
        save_recon_report(recon_summary_df, RECON_NAME)

        # Create graph and display it
        fig = get_recon_summary_graph(recon_summary_df)
        st.plotly_chart(fig, use_container_width=True)

"""
TODO: When the user reopens an already created recon, we want to save the recon and let them add new data to it. But we don't want them to go through the 
entire setup process again. 

- [DONE] When the user reopens the recon, we want to show them the plotly chat and summary report from the last time they ran the recon.

- If they want to update the recon with new data, we should get the code from each mitosheet as a function. 
    1. Takes the input data sources and merges them together 
    2. Takes the mergeed data and runs the checks

- Take the result and generate the summary report and the plotly chart

"""


