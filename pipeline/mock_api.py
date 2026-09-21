from fastapi import FastAPI

mock_app = FastAPI()

customers = [
    {"customer_id": 1, "name": "Anita Rao", "department": "Finance"},
    {"customer_id": 2, "name": "Rohan Mehta", "department": "IT"},
    {"customer_id": 3, "name": "Priya Nair", "department": "HR"},
]

@mock_app.get("/customers")
def get_customers():
    return customers