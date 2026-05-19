from fastapi import WebSocket, WebSocketDisconnect
from typing import Set, Any
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        dead = set()
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
            except Exception:
                dead.add(conn)
        for conn in dead:
            self.active_connections.discard(conn)

    async def send_personal(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    @property
    def count(self) -> int:
        return len(self.active_connections)


manager = ConnectionManager()


async def broadcast_update(event_type: str, data: Any):
    await manager.broadcast({"type": event_type, "data": data})


async def periodic_updates():
    while True:
        await asyncio.sleep(30)
        if manager.count > 0:
            await broadcast_update("ping", {"timestamp": asyncio.get_event_loop().time()})
