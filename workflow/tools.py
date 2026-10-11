import os

import requests
from pydantic import ValidationError

from workflow.schemas import (
    CaseDetails,
    RetrieveCaseInput,
    RetrieveCaseResult,
    ToolError,
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


if __name__ == "__main__":
    for payload in [{"case_id": 1}, {"case_id": 9999}, {"case_id": 0}, {"case_id": "abc"}]:
        print(payload, "->", retrieve_case(payload).model_dump(mode="json"))