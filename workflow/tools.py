import os
import time
import uuid

import requests
from pydantic import ValidationError

from workflow.schemas import (
    CaseDetails,
    RetrieveCaseInput,
    RetrieveCaseResult,
    ToolError,
    UpdateTicketInput,
    UpdateTicketResult,
    TicketDetails,
)

CASE_API_URL = os.getenv("CASE_API_URL", "http://127.0.0.1:8000")
TIMEOUT_SECONDS = 5


def _fail(code: str, message: str) -> RetrieveCaseResult:
    return RetrieveCaseResult(ok=False, error=ToolError(code=code, message=message))


def retrieve_case(raw_input: dict) -> RetrieveCaseResult:
    # 1. Validate input before doing anything
    try:
        args = RetrieveCaseInput(**raw_input)
    except (ValidationError, TypeError):
        return _fail("INVALID_INPUT", "case_id must be a positive integer")

    # 2. Call the Week 1 API, with a timeout so we never hang
    try:
        resp = requests.get(
            f"{CASE_API_URL}/cases/{args.case_id}", timeout=TIMEOUT_SECONDS
        )
    except requests.Timeout:
        return _fail("UPSTREAM_TIMEOUT", "Case service did not respond in time")
    except requests.ConnectionError:
        return _fail("UPSTREAM_UNAVAILABLE", "Case service is unreachable")

    # 3. Map HTTP outcomes to fixed error codes
    if resp.status_code == 404:
        return _fail("NOT_FOUND", f"Case {args.case_id} does not exist")
    if resp.status_code != 200:
        return _fail("UPSTREAM_ERROR", f"Case service returned {resp.status_code}")

    # 4. Validate the response too, don't trust it blindly
    try:
        case = CaseDetails(**resp.json())
    except (ValueError, ValidationError):
        return _fail("UPSTREAM_BAD_RESPONSE", "Case service returned unexpected data")

    return RetrieveCaseResult(ok=True, case=case)




TICKET_API_URL = os.getenv("TICKET_API_URL", "http://127.0.0.1:8002")
MAX_ATTEMPTS = 3

def _fail_update(code: str, message: str) -> UpdateTicketResult:
    return UpdateTicketResult(ok=False, error=ToolError(code=code, message=message))

def _call(method: str, url: str, **kwargs):
    """HTTP call with timeout and retries (timeouts, connection errors, 5xx)."""
    last_exc, last_resp = None, None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            resp = requests.request(method, url, timeout=TIMEOUT_SECONDS, **kwargs)
            if resp.status_code < 500:
                return resp
            last_resp, last_exc = resp, None
        except (requests.Timeout, requests.ConnectionError) as exc:
            last_exc = exc
        if attempt < MAX_ATTEMPTS:
            time.sleep(0.5 * 2 ** (attempt - 1))   # 0.5s, 1s backoff
    if last_exc:
        raise last_exc
    return last_resp

def update_ticket(raw_input: dict) -> UpdateTicketResult:
    # 1. validate input
    try:
        data = UpdateTicketInput(**raw_input)
    except (ValidationError, TypeError):
        return _fail_update("INVALID_INPUT", "Invalid case_id, status, comment or idempotency_key")

    try:
        # 2. find the ticket for this case
        find = _call("GET", f"{TICKET_API_URL}/tickets", params={"case_id": data.case_id})
        if find.status_code != 200:
            return _fail_update("UPSTREAM_ERROR", f"Ticket lookup returned {find.status_code}")
        matches = find.json()
        if not matches:
            return _fail_update("NOT_FOUND", f"No ticket for case {data.case_id}")
        ticket_id = matches[0]["ticket_id"]

        # 3. update it, with the idempotency key
        resp = _call(
            "PUT",
            f"{TICKET_API_URL}/tickets/{ticket_id}",
            json={"status": data.status, "comment": data.comment},
            headers={"Idempotency-Key": data.idempotency_key},
        )
    except requests.Timeout:
        return _fail_update("UPSTREAM_TIMEOUT", "Ticket service timed out")
    except requests.ConnectionError:
        return _fail_update("UPSTREAM_UNAVAILABLE", "Ticket service is unreachable")

    if resp.status_code == 404:
        return _fail_update("NOT_FOUND", f"Ticket {ticket_id} not found")
    if resp.status_code != 200:
        return _fail_update("UPSTREAM_ERROR", f"Ticket update returned {resp.status_code}")

    # 4. validate the response
    try:
        ticket = TicketDetails(**resp.json())
    except (ValidationError, ValueError):
        return _fail_update("UPSTREAM_BAD_RESPONSE", "Ticket service returned malformed data")

    return UpdateTicketResult(ok=True, ticket=ticket)  

if __name__ == "__main__":
    # --- Tool 1 tests (keep what you already have) ---
    for payload in [{"case_id": 1}, {"case_id": 9999}, {"case_id": 0}, {"case_id": "abc"}]:
        print(payload, "->", retrieve_case(payload).model_dump())

    # --- Tool 2 tests (new) ---
    key = str(uuid.uuid4())
    print(update_ticket({"case_id": 1, "status": "resolved", "comment": "Password reset", "idempotency_key": key}))
    print(update_ticket({"case_id": 1, "status": "resolved", "comment": "Password reset", "idempotency_key": key}))
    print(update_ticket({"case_id": 1, "status": "banana", "idempotency_key": key}))
    print(update_ticket({"case_id": 9999, "status": "resolved", "idempotency_key": str(uuid.uuid4())}))   