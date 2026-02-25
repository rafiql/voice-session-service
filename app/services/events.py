import asyncio
import json


from app.services.ws_manager import ws_manager
import asyncio
import json

async def emit_event(event_name: str, payload: dict):
    """
    Emit an event internally (for now, print) and broadcast via WebSocket
    """
    # Internal logging / event bus
    print(f"[EVENT EMITTED] {event_name} -> {json.dumps(payload)}")

    # Broadcast to all connected WebSocket clients
    await ws_manager.broadcast({
        "event": event_name,
        "payload": payload
    })