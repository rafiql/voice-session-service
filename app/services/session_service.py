from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
from typing import Optional, List
from datetime import datetime, timezone

from app.models.session import CallSession, SessionStatus
from app.services.events import emit_event

from uuid import UUID

class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        caller_phone: str,
        business_id: str,
        ai_config: dict,
    ) -> CallSession:
        session = CallSession(
            caller_phone=caller_phone,
            business_id=business_id,
            ai_config=ai_config,
            started_at=datetime.now(timezone.utc),
            status=SessionStatus.active
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return session


    async def get_session(self, session_id: str):
        result = await self.db.execute(
            select(CallSession).where(CallSession.id == session_id)
        )
        return result.scalar_one_or_none()
    

    async def list_sessions(
        self,
        business_id: Optional[str] = None,
        status: Optional[SessionStatus] = None,
        cursor: Optional[str] = None,
        limit: int = 10,
    ) -> List[CallSession]:

        query = select(CallSession)
        conditions = []

        if business_id:
            conditions.append(CallSession.business_id == business_id)

        if status:
            conditions.append(CallSession.status == status)

        if cursor:
            conditions.append(CallSession.id > cursor)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(CallSession.id).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()


    async def update_status(
        self,
        session_id: str,
        status: SessionStatus,
    ) -> CallSession:

        result = await self.db.execute(
            select(CallSession).where(CallSession.id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            raise ValueError("Session not found")

        session.status = status
        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def end_session(
        self,
        session_id: str,
        outcome: str,
        summary: str,
    ) -> CallSession:

        result = await self.db.execute(
            select(CallSession).where(CallSession.id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            raise ValueError("Session not found")

        session.status = SessionStatus.completed
        session.ended_at = datetime.now(timezone.utc)
        session.outcome = outcome
        session.summary = summary

        # Safely calculate duration_seconds
        if session.started_at:
            session.duration_seconds = int(
                (session.ended_at - session.started_at).total_seconds()
            )
        else:
            session.duration_seconds = 0  # fallback
            
        await self.db.commit()
        await self.db.refresh(session)

        await emit_event(
            "call.completed",
            {
                "session_id": str(session.id),
                "business_id": session.business_id,
                "caller_phone": session.caller_phone,
                "outcome": session.outcome,
                "summary": session.summary
            },
        )

        return session