import logging

from sqlalchemy.orm import Session

from src.models import AuditLog

logger = logging.getLogger("workflow")


def record(db: Session, correlation_id: str, user: dict, action: str,
           approval_id=None, case_id=None, detail=None):
    db.add(AuditLog(
        correlation_id=correlation_id,
        actor=user["user"],
        role=user["role"],
        action=action,
        approval_id=approval_id,
        case_id=case_id,
        detail=detail,
    ))
    db.commit()
    logger.info("cid=%s actor=%s role=%s action=%s approval_id=%s case_id=%s detail=%s",
                correlation_id, user["user"], user["role"], action, approval_id, case_id, detail)