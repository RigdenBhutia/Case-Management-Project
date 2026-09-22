import pandas as pd
from pipeline.ingest import ingest_cases_csv

def clean_cases(df: pd.DataFrame):
    # Track rejected rows separately
    rejected_rows = pd.DataFrame(columns=df.columns.tolist() + ["rejection_reason"])

    # Rule 1: title must not be missing
    missing_title = df[df["title"].isnull()]
    for _, row in missing_title.iterrows():
        reason_row = row.to_dict()
        reason_row["rejection_reason"] = "Missing title"
        rejected_rows = pd.concat([rejected_rows, pd.DataFrame([reason_row])], ignore_index=True)

    # Remove rows with missing title from the main dataset
    valid_df = df[df["title"].notnull()].copy()

    # Rule 2: remove exact content duplicates (keep first occurrence)
    duplicate_mask = valid_df.drop(columns=["id"]).duplicated(keep="first")
    duplicates = valid_df[duplicate_mask]
    for _, row in duplicates.iterrows():
        reason_row = row.to_dict()
        reason_row["rejection_reason"] = "Duplicate content"
        rejected_rows = pd.concat([rejected_rows, pd.DataFrame([reason_row])], ignore_index=True)

    valid_df = valid_df[~duplicate_mask]

    return valid_df, rejected_rows

if __name__ == "__main__":
    cases_df = ingest_cases_csv()
    valid_df, rejected_df = clean_cases(cases_df)

    print("Valid records:\n", valid_df)
    print("\nRejected records:\n", rejected_df)

    valid_df.to_csv("pipeline/standardized/cases_clean.csv", index=False)
    rejected_df.to_csv("pipeline/standardized/cases_rejected.csv", index=False)
    