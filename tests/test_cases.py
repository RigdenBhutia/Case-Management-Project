from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

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

def test_update_case():
    create_response = client.post("/cases", json={
        "title": "Original title",
        "description": "Original description"
    })
    case_id = create_response.json()["id"]

    update_response = client.put(f"/cases/{case_id}", json={
        "status": "in_progress"
    })
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "in_progress"