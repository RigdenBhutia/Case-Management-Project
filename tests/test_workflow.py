from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import workflow.app as wf
from src.models import Base
from workflow.schemas import (
    CaseDetails, RetrieveCaseResult, TicketDetails, ToolError, UpdateTicketResult,
)

REQUESTER = {"X-API-Key": "requester-dev-key"}
APPROVER = {"X-API-Key": "approver-dev-key"}


@pytest.fixture
def client(monkeypatch):
    # throwaway in-memory database
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                           poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    wf.app.dependency_overrides[wf.get_db] = override_get_db

    calls = {"update": 0}

    def fake_retrieve(payload):
        if payload["case_id"] == 9999:
            return RetrieveCaseResult(ok=False, error=ToolError(code="NOT_FOUND", message="missing"))
        return RetrieveCaseResult(ok=True, case=CaseDetails(
            id=payload["case_id"], title="t", description="d",
            status="open", created_at=datetime.now()))

    def fake_update(payload):
        calls["update"] += 1
        return UpdateTicketResult(ok=True, ticket=TicketDetails(
            ticket_id="T-1", case_id=payload["case_id"], status=payload["status"]))

    monkeypatch.setattr(wf, "retrieve_case", fake_retrieve)
    monkeypatch.setattr(wf, "update_ticket", fake_update)

    test_client = TestClient(wf.app)
    test_client.update_calls = calls
    yield test_client
    wf.app.dependency_overrides.clear()


def create_request(client, headers=REQUESTER, **overrides):
    body = {"case_id": 1, "status": "resolved", "comment": "Fixed"}
    body.update(overrides)
    return client.post("/approvals", json=body, headers=headers)


def test_new_request_is_pending_and_does_not_update_ticket(client):
    r = create_request(client)
    assert r.status_code == 201
    assert r.json()["state"] == "pending"
    assert client.update_calls["update"] == 0          # cannot update without approval


def test_rejected_request_never_updates_ticket(client):
    rid = create_request(client).json()["id"]
    r = client.post(f"/approvals/{rid}/reject", headers=APPROVER)
    assert r.json()["state"] == "rejected"
    assert client.update_calls["update"] == 0


def test_approval_updates_ticket_exactly_once(client):
    rid = create_request(client).json()["id"]
    first = client.post(f"/approvals/{rid}/approve", headers=APPROVER)
    assert first.json()["state"] == "executed"
    second = client.post(f"/approvals/{rid}/approve", headers=APPROVER)
    assert second.status_code == 409
    assert client.update_calls["update"] == 1


def test_requester_cannot_approve(client):
    rid = create_request(client).json()["id"]
    r = client.post(f"/approvals/{rid}/approve", headers=REQUESTER)
    assert r.status_code == 403                        # unauthorized is blocked
    assert client.update_calls["update"] == 0


def test_missing_api_key_is_blocked(client):
    assert client.post("/approvals", json={"case_id": 1, "status": "resolved"}).status_code == 401
    rid = create_request(client).json()["id"]
    assert client.post(f"/approvals/{rid}/approve").status_code == 401
    assert client.update_calls["update"] == 0


def test_unknown_case_is_rejected(client):
    assert create_request(client, case_id=9999).status_code == 404


def test_invalid_status_is_rejected(client):
    assert create_request(client, status="banana").status_code == 422


def test_audit_trail_records_who_did_what(client):
    rid = create_request(client).json()["id"]
    client.post(f"/approvals/{rid}/approve", headers=APPROVER)
    rows = client.get(f"/audit?approval_id={rid}", headers=APPROVER).json()
    assert [r["action"] for r in rows] == ["request_created", "approved", "executed"]
    assert rows[0]["actor"] == "alice"
    assert rows[1]["actor"] == "bob"


def test_requester_cannot_read_audit(client):
    assert client.get("/audit", headers=REQUESTER).status_code == 403