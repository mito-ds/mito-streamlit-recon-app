import pandas as pd

def get_sales_data(cutoff_year: str):
    import pandas as pd
    df = pd.read_csv("./db_data/car_sales_db.csv")
    return df

def get_european_real_estate_data(sector: str):
    import pandas as pd
    df = pd.read_csv("./db_data/commercial_real_estate_snowflake.csv")
    return df