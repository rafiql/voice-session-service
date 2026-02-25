import asyncio
from typing import List
from fastapi import WebSocket

class ConnectionManager:
    """
    Manage active WebSocket connections and broadcast messages.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        async with self.lock:
            for connection in self.active_connections:
                try:
                    await connection.send_json(message)
                except:
                    # connection may be closed, ignore for now
                    pass

# Singleton manager
ws_manager = ConnectionManager()