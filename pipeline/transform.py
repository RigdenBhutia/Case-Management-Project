import pandas as pd
from pipeline.clean import clean_cases
from pipeline.ingest import ingest_cases_csv, ingest_reference_data

def join_cases_with_categories(cases_df: pd.DataFrame, reference_df: pd.DataFrame):
    merged_df = cases_df.merge(
        reference_df,
        on="category_id",
        how="left"
    )
    return merged_df

if __name__ == "__main__":
    raw_cases = ingest_cases_csv()
    valid_cases, rejected_cases = clean_cases(raw_cases)
    reference_df = ingest_reference_data()

    curated_df = join_cases_with_categories(valid_cases, reference_df)
    print(curated_df)

    curated_df.to_csv("pipeline/curated/cases_curated.csv", index=False)