from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

from ..websocket import manager

router = APIRouter(tags=["WebSocket"])
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "subscribe":
                await manager.send_personal(
                    {"type": "subscribed", "channel": data.get("channel", "all")},
                    websocket,
                )
            elif data.get("type") == "ping":
                await manager.send_personal({"type": "pong"}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
