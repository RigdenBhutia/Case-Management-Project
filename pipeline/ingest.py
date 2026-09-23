import pandas as pd
import json
import requests

def ingest_cases_csv():
    df = pd.read_csv("pipeline/raw/cases_source.csv")
    return df

def ingest_reference_data():
    with open("pipeline/raw/reference_data.json") as f:
        data = json.load(f)
    return pd.DataFrame(data)

def ingest_policy_metadata():
    with open("pipeline/raw/policy_metadata.json") as f:
        data = json.load(f)
    return pd.DataFrame(data)

def ingest_customers_api():
    response = requests.get("http://host.docker.internal:8001/customers")
    data = response.json()
    return pd.DataFrame(data)

if __name__ == "__main__":
    cases_df = ingest_cases_csv()
    reference_df = ingest_reference_data()
    policy_df = ingest_policy_metadata()
    customers_df = ingest_customers_api()

    print("Cases:\n", cases_df)
    print("\nReference Data:\n", reference_df)
    print("\nPolicy Metadata:\n", policy_df)
    print("\nCustomers:\n", customers_df)