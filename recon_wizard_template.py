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

if previous_recon_report_path:
    # If we've already ran this report, display the summary of the most recent run.
    recon_summary_df = pd.read_csv(previous_recon_report_path)

    # Get the csv name from the report path
    previous_recon_name = previous_recon_report_path.split('/')[-1]

    # Format the name as a date
    previous_recon_report_date = datetime.strptime(previous_recon_name, "%Y-%m-%d-%H-%M-%S.csv")

    st.info(f'''
        Recon Description: {RECON_DESCRIPTION} 

        Hours saved per quarter with automation: {RECON_VALUE}
        
        Last updated: {previous_recon_report_date}
        '''
    )

    if st.button("Rerun recon with new datsets"):
        st.session_state[UPDATE_RECON_KEY] = True

    if st.session_state[UPDATE_RECON_KEY]:
        recon_function_string = get_recon_script(RECON_NAME)

        recon_function_string, original_imported_df_names = remove_import_code_and_get_df_names(recon_function_string)

        new_import_prompt = st.empty()

        new_df_names_and_dfs, new_imports_string = spreadsheet(import_folder='./data', key='update_recon')
        new_df_names = list(new_df_names_and_dfs.keys())

        def get_new_import_prompt(new_df_names: list, original_imported_df_names: list) -> str:
            if len(new_df_names) == len(original_imported_df_names):
                return "Click the **Rerun Recon** button below."
            else:
                return f"Import a file to replace **{original_imported_df_names[len(new_df_names)-1]}** dataframe."

        new_import_prompt.success(get_new_import_prompt(new_df_names, original_imported_df_names))

        if st.button("Rerun Recon", key='rerun_recon', disabled=len(new_df_names) != len(original_imported_df_names)):     

            # Remove the package imports since we've already imported them in the recon_function
            new_imports_string = remove_package_imports(new_imports_string)

            # Rename the imports to the original names
            rename_imports_strings = []
            original_and_new_df_names = {df_name: df for df_name, df in zip(original_imported_df_names, new_df_names)}
            for original_imported_df_names, new_df in original_and_new_df_names.items():
                rename_imports_strings.append(f'{original_imported_df_names} = {new_df}')

            rename_imports_string = '\n'.join(rename_imports_strings)

            recon_function_string = finalize_code_string(recon_function_string, new_imports_string, rename_imports_string)

            st.code(recon_function_string)
            recon_function = get_new_function(recon_function_string)
            recon_function_dfs = recon_function()

            # Get the last dataframe from the recon_function_dfs
            recon_result_df = recon_function_dfs[-1]

            recon_summary_df = get_recon_report(recon_result_df)[0]
            save_recon_report(recon_summary_df, RECON_NAME)

            st.markdown('# Recon Result')
            # Display the new recon report
            spreadsheet(recon_summary_df)

            # Create graph and display it
            fig = get_recon_summary_graph(recon_summary_df)
            st.plotly_chart(fig, use_container_width=True)

        st.stop()

    st.markdown('# Previous Recon Result')
    dfs, _ = spreadsheet(recon_summary_df)
    dfs_list = list(dfs.values())
    recon_summary_df = dfs_list[0]

    # Create graph and display it
    fig = get_recon_summary_graph(recon_summary_df)
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

        st.markdown("# Recon Result")

        spreadsheet(*dfs)

        recon_summary_df = dfs[0]
        save_recon_report(recon_summary_df, RECON_NAME)

        # Create graph and display it
        fig = get_recon_summary_graph(recon_summary_df)
        st.plotly_chart(fig, use_container_width=True)



