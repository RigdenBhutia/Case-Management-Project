import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

@pytest.fixture
def sample_case():
    response = client.post("/cases", json={
        "title": "Fixture case",
        "description": "Created by a fixture"
    })
    return response.json()

def test_create_case():
    response = client.post("/cases", json={
        "title": "Test case",
        "description": "This is a test"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test case"
    assert data["status"] == "open"

def test_get_case_not_found():
    response = client.get("/cases/9999")
    assert response.status_code == 404

def test_update_case(sample_case):
    case_id = sample_case["id"]
    update_response = client.put(f"/cases/{case_id}", json={
        "status": "in_progress"
    })
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "in_progress"