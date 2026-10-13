import uuid
from datetime import datetime
from typing import Literal, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models import ApprovalRequest
from workflow.tools import retrieve_case, update_ticket
from workflow.auth import get_user, require_role

app = FastAPI(title="Case Workflow")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ProposeUpdate(BaseModel):
    case_id: int = Field(gt=0)
    status: Literal["open", "in_progress", "resolved", "closed"]
    comment: Optional[str] = Field(default=None, max_length=500)


def to_dict(r: ApprovalRequest) -> dict:
    return {
        "id": r.id,
        "case_id": r.case_id,
        "requested_status": r.requested_status,
        "comment": r.comment,
        "state": r.state,
        "result_message": r.result_message,
        "created_at": r.created_at,
        "decided_at": r.decided_at,
    }


def get_or_404(db: Session, request_id: int) -> ApprovalRequest:
    row = db.get(ApprovalRequest, request_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return row


@app.post("/approvals", status_code=201)
def propose(payload: ProposeUpdate, db: Session = Depends(get_db),
            user: dict = Depends(require_role("requester", "approver"))):
    check = retrieve_case({"case_id": payload.case_id})
    if not check.ok:
        status = 404 if check.error.code == "NOT_FOUND" else 502
        raise HTTPException(status_code=status, detail=check.error.code)

    row = ApprovalRequest(
        case_id=payload.case_id,
        requested_status=payload.status,
        comment=payload.comment,
        idempotency_key=str(uuid.uuid4()),
        state="pending",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return to_dict(row)


@app.get("/approvals/{request_id}")
def read_request(request_id: int, db: Session = Depends(get_db), 
                user: dict = Depends(get_user)):
    return to_dict(get_or_404(db, request_id))


@app.post("/approvals/{request_id}/approve")
def approve(request_id: int, db: Session = Depends(get_db),
            user: dict = Depends(require_role("approver"))):
    row = get_or_404(db, request_id)
    if row.state != "pending":
        raise HTTPException(status_code=409, detail=f"Request is already {row.state}")

    result = update_ticket({
        "case_id": row.case_id,
        "status": row.requested_status,
        "comment": row.comment,
        "idempotency_key": row.idempotency_key,
    })
    row.decided_at = datetime.now()
    if result.ok:
        row.state = "executed"
        row.result_message = f"Ticket {result.ticket.ticket_id} set to {result.ticket.status}"
    else:
        row.state = "failed"
        row.result_message = result.error.code
    db.commit()
    db.refresh(row)
    return to_dict(row)


@app.post("/approvals/{request_id}/reject")
def reject(request_id: int, db: Session = Depends(get_db),
           user: dict = Depends(require_role("approver"))):
    row = get_or_404(db, request_id)
    if row.state != "pending":
        raise HTTPException(status_code=409, detail=f"Request is already {row.state}")
    row.state = "rejected"
    row.decided_at = datetime.now()
    db.commit()
    db.refresh(row)
    return to_dict(row)