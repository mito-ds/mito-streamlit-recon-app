import streamlit as st
from metaprogramming_utils import create_new_recon

st.set_page_config(layout="wide")
st.title("Setup a New Recon Dashboard")

with st.form(key='create_new_recon_form'):
    recon_report_name = st.text_input('Recon Name')
    recon_description = st.text_area('Recon Description')
    recon_value = st.number_input('How much time do you spend per quarter building this recon?')

    submitted = st.form_submit_button("Generate New Recon Wizard", on_click=create_new_recon(recon_report_name, recon_description, recon_value))

if submitted:
    st.success(f'Created a new recon wizard. Click on the new tab {recon_report_name} to configure it.')
