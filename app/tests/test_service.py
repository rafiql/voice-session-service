import pytest
import asyncio
from datetime import datetime
from uuid import UUID

from app.db.database import AsyncSessionLocal
from app.services.session_service import SessionService, SessionStatus

# Use pytest-asyncio
pytestmark = pytest.mark.asyncio


async def test_create_get_list_update_end_session():
    # Use an async session from your factory
    async with AsyncSessionLocal() as db:
        service = SessionService(db)

        # CREATE SESSION
        # ---------------------------
        new_session = await service.create_session(
            caller_phone="+1234567890",
            business_id="test-business-001",
            ai_config={"voice": "default", "language": "en-US"}
        )
        assert isinstance(new_session.id, UUID)
        assert new_session.status == SessionStatus.active.value
        assert new_session.caller_phone == "+1234567890"

        session_id = str(new_session.id)
        
        # GET SESSION
        # ---------------------------
        fetched = await service.get_session(session_id)
        assert fetched is not None
        assert fetched.id == new_session.id
        assert fetched.business_id == "test-business-001"
       
        # LIST SESSIONS
        # ---------------------------
        sessions = await service.list_sessions(business_id="test-business-001")
        assert len(sessions) >= 1
        assert any(s.id == new_session.id for s in sessions)

        # UPDATE SESSION
        # ---------------------------
        updated = await service.update_status(
            session_id=session_id,
            status=SessionStatus.transferring
        )
        assert updated.status == SessionStatus.transferring.value

        # END SESSION
        # ---------------------------
        ended = await service.end_session(
            session_id=session_id,
            outcome="qualified",
            summary="Lead is interested in MBA program and wants callback."
        )
        assert ended.status == SessionStatus.completed.value
        assert ended.outcome == "qualified"
        assert ended.summary == "Lead is interested in MBA program and wants callback."
        assert ended.ended_at is not None
        assert hasattr(ended, "duration_seconds")
        assert ended.duration_seconds >= 0