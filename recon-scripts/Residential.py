from mitosheet.public.v3 import *
import pandas as pd

def MITO_GENERATED_RECON_FUNCTION_Residential():
    # Imported df1 using get_european_estate_data
    df1 = get_european_estate_data(sector='Residential')
    
    # Imported Prologis v1.csv, Warehouse REIT v1.csv
    Prologis_v1 = pd.read_csv(r'/Users/aarondiamond-reivich/Mito/streamlit-recon-wizard/data/commercial leases/Prologis v1.csv')
    Warehouse_REIT_v1 = pd.read_csv(r'/Users/aarondiamond-reivich/Mito/streamlit-recon-wizard/data/commercial leases/Warehouse REIT v1.csv')
    
    # Filtered Stategy
    Prologis_v1 = Prologis_v1[Prologis_v1['Stategy'].apply(lambda val: all(val != s for s in ['Mixed Use', 'Office']))]
    
    # Renamed columns Square Meters
    Warehouse_REIT_v1.rename(columns={'SQM': 'Square Meters'}, inplace=True)
    
    # Set formula of Tenant Name
    Warehouse_REIT_v1['Tenant Name'] = SUBSTITUTE(Warehouse_REIT_v1['Tenant Name'], 'Grp.', 'Group')
    
    # Concatenated 2 into dataframes into df4
    df4 = pd.concat([Warehouse_REIT_v1, Prologis_v1], join='inner', ignore_index=True)
    
    # Merged df1 and df4 into df5
    temp_df = df4.drop_duplicates(subset=['Lease ID', 'Asset ID']) # Remove duplicates so lookup merge only returns first match
    df1_tmp = df1.drop(['Country', 'Square Meters', 'Space utilization', 'Portfolio', 'Peak space utilization'], axis=1)
    df4_tmp = temp_df.drop(['Country', 'Square Meters', 'Space utilization', 'Portfolio', 'Peak space utilization'], axis=1)
    df5 = df1_tmp.merge(df4_tmp, left_on=['Lease ID', 'Asset ID'], right_on=['Lease ID', 'Asset ID'], how='left', suffixes=['_df1', '_df4'])
    
    # Reordered column Tenant Name_df4
    df5_columns = [col for col in df5.columns if col != 'Tenant Name_df4']
    df5_columns.insert(2, 'Tenant Name_df4')
    df5 = df5[df5_columns]
    
    # Reordered column Estimated Rental Value_df4
    df5_columns = [col for col in df5.columns if col != 'Estimated Rental Value_df4']
    df5_columns.insert(4, 'Estimated Rental Value_df4')
    df5 = df5[df5_columns]
    
    # Added column 'Tenant Name Check'
    df5.insert(4, 'Tenant Name Check', CHECK_STRING_DIFFERENCE(df5['Tenant Name_df4'],df5['Tenant Name_df1'], 90))
    
    # Added column 'Estimated Rental Value Check'
    df5.insert(7, 'Estimated Rental Value Check', CHECK_NUMBER_DIFFERENCE(df5['Estimated Rental Value_df4'],df5['Estimated Rental Value_df1'], 10))
    
    # Added column 'Net Effective Rent Check'
    df5.insert(10, 'Net Effective Rent Check', CHECK_NUMBER_DIFFERENCE(df5['Net Effective Rent_df1'],df5['Net Effective Rent_df4'], 10))
    
    return df1, Prologis_v1, Warehouse_REIT_v1, df4, df5
