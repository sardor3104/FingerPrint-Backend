from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.websocket_manager import manager
from app.core.security import verify_token
from app.models.employee import Employee
from app.models.chat import Chat
from beanie import PydanticObjectId
from loguru import logger
from datetime import datetime

router = APIRouter()

@router.websocket("/chat/{chat_id}")
async def websocket_chat(
    websocket: WebSocket,
    chat_id: str,
    token: str = Query(..., description="JWT access token for auth")
):
    """
    WebSocket endpoint for real-time chat.
    Client connects with: ws://localhost:8000/api/v1/ws/chat/{chat_id}?token=<jwt>
    """
    # 1. Authenticate
    token_data = verify_token(token)
    if not token_data:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    user = await Employee.get(token_data.sub)
    if not user:
        await websocket.close(code=4001, reason="User not found")
        return

    # 2. Verify chat exists and user belongs to it
    try:
        chat = await Chat.get(PydanticObjectId(chat_id))
    except Exception:
        await websocket.close(code=4004, reason="Chat not found")
        return

    if not chat:
        await websocket.close(code=4004, reason="Chat not found")
        return

    # Fetch linked documents
    await chat.fetch_all_links()
    
    employee_id = str(chat.employee_id.id) if hasattr(chat.employee_id, 'id') else str(chat.employee_id)
    manager_id = str(chat.manager_id.id) if hasattr(chat.manager_id, 'id') else str(chat.manager_id)
    user_id = str(user.id)

    if user_id not in [employee_id, manager_id]:
        await websocket.close(code=4003, reason="Forbidden")
        return

    # 3. Connect
    await manager.connect(chat_id, websocket)

    # 4. Send chat history on connect
    history = []
    for msg in chat.messages:
        history.append({
            "type": "history",
            "sender_id": str(msg.get("sender_id", "")),
            "sender_name": msg.get("sender_name", "Unknown"),
            "text": msg.get("text", ""),
            "timestamp": msg.get("timestamp", datetime.utcnow()).isoformat() if isinstance(msg.get("timestamp"), datetime) else str(msg.get("timestamp", "")),
            "status": msg.get("status", "sent")
        })
    await manager.send_personal(websocket, {"type": "history_batch", "messages": history})

    try:
        while True:
            data = await websocket.receive_json()
            text = data.get("text", "").strip()
            if not text:
                continue

            # Save message to DB
            message = {
                "sender_id": PydanticObjectId(user_id),
                "sender_name": user.full_name,
                "text": text,
                "timestamp": datetime.utcnow(),
                "status": "sent"
            }
            chat.messages.append(message)
            chat.updated_at = datetime.utcnow()
            await chat.save()

            # Broadcast to all in the room
            broadcast_payload = {
                "type": "message",
                "sender_id": user_id,
                "sender_name": user.full_name,
                "text": text,
                "timestamp": message["timestamp"].isoformat(),
                "status": "sent"
            }
            await manager.broadcast(chat_id, broadcast_payload)
            logger.info(f"Chat {chat_id}: Message from {user.full_name}")

    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)
        logger.info(f"User {user.full_name} disconnected from chat {chat_id}")
    except Exception as e:
        logger.error(f"WS error in chat {chat_id}: {e}")
        manager.disconnect(chat_id, websocket)
