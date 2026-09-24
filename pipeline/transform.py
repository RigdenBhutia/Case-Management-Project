import pandas as pd
from src.database import engine
pd.set_option("display.max_columns", None)
from pipeline.audit import log_pipeline_run
from pipeline.clean import clean_cases
from pipeline.ingest import ingest_cases_csv, ingest_reference_data, ingest_customers_api

def check_referential_integrity(cases_df, reference_df, customers_df):
    valid_category_ids = set(reference_df["category_id"])
    valid_customer_ids = set(customers_df["customer_id"])

    orphaned_category = cases_df[~cases_df["category_id"].isin(valid_category_ids)]
    orphaned_customer = cases_df[~cases_df["customer_id"].isin(valid_customer_ids)]

    return orphaned_category, orphaned_customer
def join_cases_with_categories(cases_df: pd.DataFrame, reference_df: pd.DataFrame):
    return cases_df.merge(reference_df, on="category_id", how="left")

def join_with_customers(df: pd.DataFrame, customers_df: pd.DataFrame):
    return df.merge(customers_df, on="customer_id", how="left")

def check_referential_integrity(cases_df, reference_df, customers_df):
    valid_category_ids = set(reference_df["category_id"])
    valid_customer_ids = set(customers_df["customer_id"])

    orphaned_category = cases_df[~cases_df["category_id"].isin(valid_category_ids)]
    orphaned_customer = cases_df[~cases_df["customer_id"].isin(valid_customer_ids)]

    return orphaned_category, orphaned_customer

if __name__ == "__main__":
    raw_cases = ingest_cases_csv()
    valid_cases, rejected_cases = clean_cases(raw_cases)
    reference_df = ingest_reference_data()
    customers_df = ingest_customers_api()
    orphaned_category, orphaned_customer = check_referential_integrity(valid_cases, reference_df, customers_df)
    print("Cases with invalid category_id:\n", orphaned_category)
    print("Cases with invalid customer_id:\n", orphaned_customer)

    curated_df = join_cases_with_categories(valid_cases, reference_df)
    curated_df = join_with_customers(curated_df, customers_df)

    print(curated_df)

    curated_df.to_csv("pipeline/curated/cases_curated.csv", index=False)
    curated_df.to_sql("curated_cases", con=engine, if_exists="replace", index=False)

    log_pipeline_run(
        source_count=len(raw_cases),
        valid_count=len(valid_cases),
        rejected_count=len(rejected_cases)
    )