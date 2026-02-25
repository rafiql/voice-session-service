import uuid
import enum
from sqlalchemy import Column, String, DateTime, Enum, JSON, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.database import Base


class SessionStatus(str, enum.Enum):
    active = "active"
    on_hold = "on-hold"
    transferring = "transferring"
    completed = "completed"
    failed = "failed"


class CallSession(Base):
    __tablename__ = "call_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    caller_phone = Column(String(20), nullable=False, index=True)
    business_id = Column(String(50), nullable=False, index=True)

    ai_config = Column(JSON, nullable=False)

    status = Column(Enum(SessionStatus), default=SessionStatus.active, nullable=False)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

    outcome = Column(String(100), nullable=True)
    summary = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)