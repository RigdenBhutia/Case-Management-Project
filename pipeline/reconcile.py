import pandas as pd
from datetime import datetime
from pipeline.ingest import ingest_cases_csv
from pipeline.clean import clean_cases

def generate_reconciliation_report(raw_df: pd.DataFrame, valid_df: pd.DataFrame, rejected_df: pd.DataFrame):
    report = {
        "run_timestamp": datetime.now().isoformat(),
        "source_record_count": len(raw_df),
        "valid_record_count": len(valid_df),
        "rejected_record_count": len(rejected_df),
        "counts_reconciled": len(raw_df) == (len(valid_df) + len(rejected_df))
    }
    return report

if __name__ == "__main__":
    raw_cases = ingest_cases_csv()
    valid_cases, rejected_cases = clean_cases(raw_cases)

    report = generate_reconciliation_report(raw_cases, valid_cases, rejected_cases)
    print(report)

    report_df = pd.DataFrame([report])
    report_df.to_csv("pipeline/curated/reconciliation_report.csv", index=False)