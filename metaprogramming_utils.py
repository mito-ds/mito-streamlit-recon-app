import os
from utils import get_recon_names
import streamlit as st
import pandas as pd

def create_new_recon(recon_name, recon_description, recon_value):
    # When this streamlit page is loaded, the form gets submitted with empty values, 
    # so we use this check to make sure that the form is submitted by the user before processing it.
    if recon_name == '' or recon_description == '':
        return

    # Get the existing recon names to make sure we don't duplicate
    existing_recon_names = get_recon_names()
    if recon_name in existing_recon_names:
        st.error(f"Recon name {recon_name} already exists. Please choose a different name.")
        return

    # Add subdirectory to outputs file
    os.mkdir(f"outputs/{recon_name}")

    new_recon_file_path = f"pages/{recon_name}.py"

    # Duplicate the recon_wizard_template.py file and rename it to the new recon name
    with open('./recon_wizard_template.py', 'r') as f:
        template_file_contents = f.read()

        # Replace the placeholder text with the new recon name
        template_file_contents = template_file_contents.replace("MITO_PLACEHOLDER__REPLACE_WITH_RECON_NAME", recon_name)
        template_file_contents = template_file_contents.replace("MITO_PLACEHOLDER__REPLACE_WITH_RECON_DESCRIPTION", recon_description)
        template_file_contents = template_file_contents.replace("MITO_PLACEHOLDER__REPLACE_WITH_RECON_VALUE", str(recon_value))

        # Write the new file to the pages folder
        with open(new_recon_file_path, 'w') as new_recon_file:
            new_recon_file.write(template_file_contents)



    