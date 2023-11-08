from mitosheet.types import ParamMetadata
import streamlit as st
import pandas as pd
from mitosheet.streamlit.v1 import spreadsheet, RunnableAnalysis
from mitosheet.public.v3 import *
import plotly.express as px
from datetime import datetime
from custom_imports import get_sales_data, get_european_real_estate_data
from custom_spreadsheet_functions import CHECK_NUMBER_DIFFERENCE, CHECK_STRING_DIFFERENCE
from utils import * 

RECON_NAME = "Residential"
RECON_DESCRIPTION = "Compare residential real estate data from Snowflake to manually tracked Excel files"
RECON_VALUE = "12.0"

RECON_SETUP_MODE_KEY = f"recon_setup_mode_{RECON_NAME}"
UPDATE_RECON_KEY = f"update_{RECON_NAME}"
RECON_CONFIGURATION_STEP_KEY = f"recon_configuration_step_{RECON_NAME}"

st.set_page_config(layout="wide")
st.title(RECON_NAME)

if UPDATE_RECON_KEY not in st.session_state:
    st.session_state[UPDATE_RECON_KEY] = False

if RECON_CONFIGURATION_STEP_KEY not in st.session_state:
    st.session_state[RECON_CONFIGURATION_STEP_KEY] = 1

def update_recon_configuration_step_state():
    st.session_state[RECON_CONFIGURATION_STEP_KEY] += 1

# Get the previous run of the report if it exists
previous_recon_report_path = get_most_recent_output_path_by_name(RECON_NAME)

if RECON_SETUP_MODE_KEY not in st.session_state:
    # If there is not a previous report, then we need to be in setup mode.
    # We save this in state so that once we finish building the report, the app
    # doesn't automatically switch into update mode on the next refresh.  
    st.session_state[RECON_SETUP_MODE_KEY] = previous_recon_report_path is None

if previous_recon_report_path and not st.session_state[RECON_SETUP_MODE_KEY]:
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
        original_analysis = RunnableAnalysis.from_json(get_recon_analysis(RECON_NAME))

        def map_param_to_value(param: ParamMetadata):
            return param['original_value'] if param['original_value'] != '' else param['name']

        recon_function_string = original_analysis.fully_parameterized_function
        original_imported_df_names = list(map(
            map_param_to_value,
            original_analysis.get_param_metadata('import')
        ))

        new_import_prompt = st.empty()

        new_analysis: RunnableAnalysis = spreadsheet(
            import_folder='./data', 
            key='update_recon', 
            importers=[get_sales_data, get_european_real_estate_data], 
            return_type='analysis'
        )
        new_df_names = new_analysis.get_param_metadata('import')

        def get_new_import_prompt(new_df_names: list, original_imported_df_names: list) -> str:
            if len(new_df_names) == len(original_imported_df_names):
                return "Click the **Rerun Recon** button below."
            else:
                return f"Import a file to replace **{original_imported_df_names[len(new_df_names)]}** dataframe."

        new_import_prompt.success(get_new_import_prompt(new_df_names, original_imported_df_names))

        if st.button("Rerun Recon", key='rerun_recon', disabled=len(new_df_names) != len(original_imported_df_names)):     
            recon_function_dfs = original_analysis.run()

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

    def get_instruction_prompt(recon_configuration_step: int) -> str:
        if recon_configuration_step == 1 or recon_configuration_step == 2:
            return f'''
                ### Step {recon_configuration_step}: Construct {'first' if recon_configuration_step == 1 else 'second'} dataset
                Construct the **{'first' if recon_configuration_step == 1 else 'second'}** data source to reconcile. 

                1. Import data by clicking **Import** in the Mito toolbar.
                2. Preprocess the data into the correct format using Mito's transformations. 
            '''

        if recon_configuration_step == 3:
            return """
            ### Step 3: Merge datasets together
            Merge the datasets together by clicking **Dataframes** > **Merge**. Then select the columns from each dataframe that you want to merge on."""
        
        if recon_configuration_step == 4:
            return """
            ### Step 4: Construct Recon
            Now that you've constructed the dataset, setup data checks by adding a new column and using the formulas =CHECK_NUMBER_DIFFERENCE() and =CHECK_STRING_DIFFERENCE().
            
            **Make sure to include the word "check" in the column name so that recon app registers it**.
            """
        
        if recon_configuration_step > 4:
            return "Scroll down to view the recon report."

    # Create a placeholder streamlit widget so we can later fill in the 
    # wizard instructions and display it to the user above the spreadsheet.
    instruction_prompt = st.success(get_instruction_prompt(st.session_state[RECON_CONFIGURATION_STEP_KEY]))
    st.button("Next Step" if st.session_state[RECON_CONFIGURATION_STEP_KEY] < 4 else "Generate Report", on_click=update_recon_configuration_step_state)

    safe_recon_name = RECON_NAME.replace(' ', '_')
    
    # Display the data inside of the spreadsheet so the user can easily fix data quality issues.
    analysis: RunnableAnalysis = spreadsheet(
        importers=[get_sales_data, get_european_real_estate_data], 
        import_folder='./data', 
        sheet_functions=[CHECK_NUMBER_DIFFERENCE, CHECK_STRING_DIFFERENCE],
        code_options={'as_function': True, 'call_function': False, 'function_name': f'MITO_GENERATED_RECON_FUNCTION_{safe_recon_name}', 'function_params': {}},
        key='setup_recon',
        return_type='analysis'
    )

    imports = analysis.get_param_metadata('import')
    output_dfs = analysis.run()
    recon_raw_data_df = None
    if isinstance(output_dfs, pd.DataFrame):
        recon_raw_data_df = output_dfs
    elif isinstance(output_dfs, tuple) and len(output_dfs) > 0:
        recon_raw_data_df = output_dfs[-1]
        
    if st.session_state[RECON_CONFIGURATION_STEP_KEY] > 4:
        # Save the recon metadata to the metadata file so we can display info about it in the app dashboard
        add_recon_to_metadata(RECON_NAME, RECON_DESCRIPTION, RECON_VALUE)
        save_recon_analysis(RECON_NAME, analysis.to_json())

        dfs = get_recon_report(recon_raw_data_df)

        st.markdown("# Recon Result")

        spreadsheet(*dfs)

        recon_summary_df = dfs[0]
        save_recon_report(recon_summary_df, RECON_NAME)

        # Create graph and display it
        fig = get_recon_summary_graph(recon_summary_df)
        st.plotly_chart(fig, use_container_width=True)

        if st.button('Save Recon'):
            st.success('Recon saved successfully.')
            # Update the session state and then rerun the app
            st.session_state[RECON_SETUP_MODE_KEY] = False
            st.experimental_rerun()

        



