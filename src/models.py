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