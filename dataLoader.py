import pandas as pd
from sqlalchemy import create_engine

def load_data():
    engine = create_engine("sqlite:///ecommerce.db")

    # Use read_excel for .xlsx files
    ad_sales = pd.read_excel("datasets/Ad_sales.xlsx")
    total_sales = pd.read_excel("datasets/Total_Sales.xlsx")
    eligibility = pd.read_excel("datasets/Eligibility.xlsx")

    # Save to SQL
    ad_sales.to_sql("ad_sales", engine, if_exists="replace", index=False)
    total_sales.to_sql("total_sales", engine, if_exists="replace", index=False)
    eligibility.to_sql("eligibility", engine, if_exists="replace", index=False)

    print("Data loaded into ecommerce.db")

if __name__ == "__main__":
    load_data()
