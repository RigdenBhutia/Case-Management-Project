import logging
import uuid
from datetime import datetime
from typing import Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models import ApprovalRequest, AuditLog
from workflow.audit import record
from workflow.auth import get_user, require_role
from workflow.tools import retrieve_case, update_ticket

app = FastAPI(title="Case Workflow")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    cid = request.headers.get("x-correlation-id") or str(uuid.uuid4())
    request.state.correlation_id = cid
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = cid
    return response

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
def propose(payload: ProposeUpdate, request: Request, db: Session = Depends(get_db),
            user: dict = Depends(require_role("requester", "approver"))):
    cid = request.state.correlation_id
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
    record(db, cid, user, "request_created", row.id, row.case_id, f"status={row.requested_status}")
    return to_dict(row)


@app.post("/approvals/{request_id}/approve")
def approve(request_id: int, request: Request, db: Session = Depends(get_db),
            user: dict = Depends(require_role("approver"))):
    cid = request.state.correlation_id
    row = get_or_404(db, request_id)
    if row.state != "pending":
        raise HTTPException(status_code=409, detail=f"Request is already {row.state}")

    record(db, cid, user, "approved", row.id, row.case_id)
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
        db.commit()
        record(db, cid, user, "executed", row.id, row.case_id, row.result_message)
    else:
        row.state = "failed"
        row.result_message = result.error.code
        db.commit()
        record(db, cid, user, "failed", row.id, row.case_id, row.result_message)
    db.refresh(row)
    return to_dict(row)


@app.post("/approvals/{request_id}/reject")
def reject(request_id: int, request: Request, db: Session = Depends(get_db),
           user: dict = Depends(require_role("approver"))):
    cid = request.state.correlation_id
    row = get_or_404(db, request_id)
    if row.state != "pending":
        raise HTTPException(status_code=409, detail=f"Request is already {row.state}")
    row.state = "rejected"
    row.decided_at = datetime.now()
    db.commit()
    record(db, cid, user, "rejected", row.id, row.case_id)
    db.refresh(row)
    return to_dict(row)

@app.get("/audit")
def read_audit(approval_id: Optional[int] = None, db: Session = Depends(get_db),
               user: dict = Depends(require_role("approver"))):
    query = db.query(AuditLog).order_by(AuditLog.id)
    if approval_id is not None:
        query = query.filter(AuditLog.approval_id == approval_id)
    return [
        {"id": r.id, "correlation_id": r.correlation_id, "actor": r.actor, "role": r.role,
         "action": r.action, "approval_id": r.approval_id, "case_id": r.case_id,
         "detail": r.detail, "created_at": r.created_at}
        for r in query.all()
    ]