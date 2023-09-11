import streamlit as st
from metaprogramming_utils import create_new_recon
from Dashboard import ENTERPRISE_NAME

st.set_page_config(layout="wide")
st.title("Setup a New Recon")
st.markdown(f'To start a build a new recon, follow the steps below. If you have questions, If you have questions about creating a new reconciliation process, contact [{ENTERPRISE_NAME} Data Governance](mailto:aaron@sagacollab.com).')

with st.form(key='create_new_recon_form'):
    recon_report_name = st.text_input('Recon Name')
    recon_description = st.text_area('Recon Description')
    recon_value = st.number_input('How much time do you spend per quarter building this recon?')

    submitted = st.form_submit_button("Generate New Recon Wizard")

if submitted:
    success, message = create_new_recon(recon_report_name, recon_description, recon_value)
    if not success:
        st.error(message)
    else:
        st.success(f'Created a new recon wizard. Click on the new tab **Recon: {recon_report_name}** to configure it.')
