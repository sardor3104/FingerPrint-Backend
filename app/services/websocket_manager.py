from typing import Dict, List
from fastapi import WebSocket
from loguru import logger
import json
from datetime import datetime


class ConnectionManager:
    """Manages all active WebSocket connections per chat_id."""
    
    def __init__(self):
        # chat_id -> list of connected WebSockets
        self._connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, chat_id: str, websocket: WebSocket):
        await websocket.accept()
        if chat_id not in self._connections:
            self._connections[chat_id] = []
        self._connections[chat_id].append(websocket)
        logger.info(f"WS connected to chat {chat_id}. Total: {len(self._connections[chat_id])}")

    def disconnect(self, chat_id: str, websocket: WebSocket):
        if chat_id in self._connections:
            try:
                self._connections[chat_id].remove(websocket)
            except ValueError:
                pass
            if not self._connections[chat_id]:
                del self._connections[chat_id]
        logger.info(f"WS disconnected from chat {chat_id}")

    async def broadcast(self, chat_id: str, message: dict, sender_ws: WebSocket = None):
        """Send message to all connected clients in a chat room."""
        if chat_id not in self._connections:
            return
        dead = []
        for ws in self._connections[chat_id]:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to WS: {e}")
                dead.append(ws)
        for ws in dead:
            self.disconnect(chat_id, ws)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message only to a specific client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send personal WS message: {e}")


# Singleton instance — used across the app
manager = ConnectionManager()
