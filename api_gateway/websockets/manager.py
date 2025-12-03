from typing import Dict, Set
from fastapi import WebSocket


class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_json(self, user_id: str, data: dict):
        conns = self.active_connections.get(user_id, set())
        for conn in conns:
            await conn.send_json(data)

    async def broadcast_json(self, data: dict):
        for conns in self.active_connections.values():
            for conn in conns:
                await conn.send_json(data)


manager = WebSocketConnectionManager()
