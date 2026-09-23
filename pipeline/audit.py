import pandas as pd
from datetime import datetime
import uuid

def log_pipeline_run(source_count, valid_count, rejected_count, status="SUCCESS"):
    run_record = {
        "run_id": str(uuid.uuid4()),
        "run_timestamp": datetime.now().isoformat(),
        "source_record_count": source_count,
        "valid_record_count": valid_count,
        "rejected_record_count": rejected_count,
        "status": status
    }

    log_df = pd.DataFrame([run_record])

    try:
        existing_log = pd.read_csv("pipeline/curated/audit_log.csv")
        log_df = pd.concat([existing_log, log_df], ignore_index=True)
    except FileNotFoundError:
        pass

    log_df.to_csv("pipeline/curated/audit_log.csv", index=False)
    return run_record