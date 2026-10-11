from datetime import datetime
from typing import Optional

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