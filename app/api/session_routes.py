# app/api/session_routes.py

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID

from app.db.database import get_db
from app.services.session_service import SessionService, SessionStatus
from app.schemas.session_schema import (
    CreateSessionRequest,
    UpdateStatusRequest,
    EndSessionRequest,
    SessionResponse
)
from app.services.ws_manager import ws_manager
from app.services.events import emit_event

router = APIRouter(prefix="/sessions", tags=["Sessions"])

# ------------------------------
# REST Endpoints
# ------------------------------

@router.post("", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    service = SessionService(db)
    session = await service.create_session(
        caller_phone=request.caller_phone,
        business_id=request.business_id,
        ai_config=request.ai_config
    )
    return session

@router.patch("/{session_id}/status", response_model=SessionResponse)
async def update_status(
    session_id: str,
    request: UpdateStatusRequest,
    db: AsyncSession = Depends(get_db),
):
    service = SessionService(db)
    try:
        status = SessionStatus(request.status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")

    try:
        session = await service.update_status(session_id, status)
        return session
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = SessionService(db)
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("", response_model=List[SessionResponse])
async def list_sessions(
    business_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    cursor: Optional[str] = Query(None),
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
):
    service = SessionService(db)
    session_status = None
    if status:
        try:
            session_status = SessionStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")

    sessions = await service.list_sessions(
        business_id=business_id,
        status=session_status,
        cursor=cursor,
        limit=limit
    )
    return sessions

@router.post("/{session_id}/end", response_model=SessionResponse)
async def end_session(
    session_id: str,
    request: EndSessionRequest,
    db: AsyncSession = Depends(get_db),
):
    service = SessionService(db)
    try:
        session = await service.end_session(
            session_id=session_id,
            outcome=request.outcome,
            summary=request.summary
        )
        
        return session
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")


# ------------------------------
# WebSocket Endpoint
# ------------------------------

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for clients to receive session updates in real-time.
    Connect at: ws://localhost:8000/sessions/ws
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # Receive message from client (optional, can be ignored)
            try:
                data = await websocket.receive_text()
                # Echo ack
                await ws_manager.send_personal_message({"ack": data}, websocket)
            except:
                pass  # ignore if client sends nothing
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)