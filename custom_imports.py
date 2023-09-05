import pandas as pd

def get_sales_data(cutoff_year: str):
    import pandas as pd
    df = pd.read_csv("./data/car_sales_db.csv")
    return df