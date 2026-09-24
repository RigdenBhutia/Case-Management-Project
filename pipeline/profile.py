import pandas as pd
from pipeline.ingest import ingest_cases_csv

def profile_cases(df: pd.DataFrame):
    print("Total rows:", len(df))
    print("\nMissing values per column:\n", df.isnull().sum())
    print("\nDuplicate rows (excluding id):", df.drop(columns=["id"]).duplicated().sum())
    print("\nDuplicate IDs:", df["id"].duplicated().sum())
    print("\nUnique statuses:", df["status"].unique())
    
if __name__ == "__main__":
    cases_df = ingest_cases_csv()
    profile_cases(cases_df)