# Reconciliation App
Centralize and automate your organizations's data reconciliation. Save your organization hundreds of hours of manual work each quarter. 

[See the app in action](https://www.loom.com/share/ed87167b23ce4529ad7b369b53264709?sid=bfa672ed-d9c8-4dc6-9566-ecbb2f3ba2cc)

Users of the reconciliation app interact with three main componets:
1. Reconciliation Dashboard: shows the current status of all the reconciliations your organization has created. Including:
- Number of rules checked
- Number of data points reconciled
- Total hours saved due to automation
- The total number of passing and failing checks
2. Reconciliation Creation Wizard: walks users through the process of building a new reconciliation. Using the Mito spreadsheet, non-technical users are able to create full reconciliation automations without writing any code. Analysts use: 
- [Custom importers](https://docs.trymito.io/how-to/importing-data-to-mito/import-generated-ui-from-any-python-function) to access internal data sources.
- [Excel and CSV import taskpane](https://docs.trymito.io/how-to/importing-data-to-mito/importing-from-excel-files) to configure data imports from their local computer or shared drives.
- [Merge Taskpane](https://docs.trymito.io/how-to/combining-dataframes/merging-datasets-together) - to join data from multiple sources.
- [Excel-like spreadsheet formulas](https://docs.trymito.io/how-to/interacting-with-your-data/mito-spreadsheet-formulas) and [Custom spreadsheet formulas](https://docs.trymito.io/how-to/interacting-with-your-data/bring-your-own-spreadsheet-functions) to build reconciliation logic.
3. Reconciliation Updating Wizard: walks users through the process of rerunning an existing reconciliation with new data.   

### App architecture
The 🆕Recon.py file is the entry point for creating a new reconciliation. After the user defines some basic information about the recon, the app sets up a new reconciliation. It does the following: 
1. It duplicates the `recon_wizard_template.py` into the Pages folder and names it according to the user's input.
2. It creates a new entry in the `recon_metadata.csv` file which stores information about the reconciliation that is used by the reconciliation dashboard.

After the user follows the prompts of the recon wizard to set up a new recon, the result of the recon is saved in the `outputs` folder. These outputs are used by the reconciliation dashboard. 

The app relies on the [Streamlit framework](https://streamlit.io) and the [Mito Streamlit Spreadsheet](https://docs.trymito.io/mito-for-streamlit/getting-started).

### Run Locally 
1. Create a virtual environment:
```
python3 -m venv venv
```

2. Start the virtual environment:
```
source venv/bin/activate
```

3. Install the required python packages:
```
pip install -r requirements.txt
```

4. Start the streamlit app
```
streamlit run Dashboard.py
```

### Developer Utilities
If you make changes to the app's architecture and/or want to clear all previous recons, use the `reset_app.sh` bash script to reset the app. Use it by running:
```
bash dev/reset_app.sh
```
 
### Demoing this app
Step 1: Import database data
- Custom Import the get_european_real_estate_data

Step 2: Import vendor-provided data
- Import the Warehouse v1 and Prologis v1
- In Warehouse v1, Tenant Name column, =SUBSTITUTE('Tenant Name0, 'Grp.', 'Group')
- In Warehouse v1, rename SQM to Square Meters
- In Prologis v1, filter the Strategy column to just warehouse
- Concat the tables on top of eachother. Its better to do Warehouse on top then Prologis

Step 3: Create dataset for recon 
- Merge that datasets together on the Lease ID column. You can use Asset ID also if you want to show off composite key

Step 4: Build the recon
- Use the =CHECK_STRING_DIFFERENCE formula with a similarity threshold of 90
- Use the =CHECK_NUMBER_DIFFERENCE formula with a threshold of 10

Step 5: Show recon report in app
- Generate the recon
- Scroll down to show the results
- Click the Save Button

Step 6: Show updated dashboard
- Show the updated dashboard

Step 7: Rerun the recon
- Click on the recon you just built and update it by importing the new files
- Show that in the new dataset, there are no failing tests
