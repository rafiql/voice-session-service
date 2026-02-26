from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models.session import SessionStatus

class UpdateStatusRequest(BaseModel):
    status: SessionStatus

class CreateSessionRequest(BaseModel):
    caller_phone: str
    business_id: str
    ai_config: dict


class UpdateStatusRequest(BaseModel):
    status: str


class EndSessionRequest(BaseModel):
    outcome: str
    summary: str


class SessionResponse(BaseModel):
    id: UUID
    caller_phone: str
    business_id: str
    status: SessionStatus
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]
    outcome: Optional[str]
    summary: Optional[str]

    class Config:
        from_attributes = True