from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.now)

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, nullable=False)
    requested_status = Column(String, nullable=False)
    comment = Column(String, nullable=True)
    idempotency_key = Column(String, nullable=False, unique=True)
    state = Column(String, nullable=False, default="pending")   # pending, approved, rejected, executed, failed
    result_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    decided_at = Column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    correlation_id = Column(String, nullable=False)
    actor = Column(String, nullable=False)
    role = Column(String, nullable=False)
    action = Column(String, nullable=False)       # request_created, approved, rejected, executed, failed
    approval_id = Column(Integer, nullable=True)
    case_id = Column(Integer, nullable=True)
    detail = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)