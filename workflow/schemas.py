from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class RetrieveCaseInput(BaseModel):
    case_id: int = Field(gt=0)


class CaseDetails(BaseModel):
    id: int
    title: str
    description: str
    status: str
    created_at: datetime


class ToolError(BaseModel):
    code: str
    message: str


class RetrieveCaseResult(BaseModel):
    ok: bool
    case: Optional[CaseDetails] = None
    error: Optional[ToolError] = None


class UpdateTicketInput(BaseModel):
    case_id: int = Field(gt=0)
    status: Literal["open", "in_progress", "resolved", "closed"]
    comment: Optional[str] = Field(default=None, max_length=500)
    idempotency_key: str = Field(min_length=8)


class TicketDetails(BaseModel):
    ticket_id: str
    case_id: int
    status: str
    comment: Optional[str] = None
    updated_at: Optional[datetime] = None


class UpdateTicketResult(BaseModel):
    ok: bool
    ticket: Optional[TicketDetails] = None
    error: Optional[ToolError] = None