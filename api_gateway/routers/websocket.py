from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websockets.manager import manager as ws_manager

router = APIRouter()


@router.websocket("/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            # Optionally handle incoming messages if needed
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)


@router.post("/notify")
async def notify_users(data: dict):
    users = data.get("users", [])
    event = data.get("event", {})
    for uid in users:
        await ws_manager.send_personal_json(uid, event)
    return {"status": "ok"}

