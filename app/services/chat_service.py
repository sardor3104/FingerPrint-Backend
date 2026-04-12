from typing import Literal
from beanie import PydanticObjectId
from fastapi import HTTPException
from app.models.chat import Chat
from app.models.employee import Employee
from loguru import logger
from datetime import datetime


class ChatService:
    @staticmethod
    async def create_chat(initiator_id: PydanticObjectId, data) -> Chat:
        """
        Create a chat between any two users.
        'employee_id' is the initiator, 'manager_id' is the recipient (any role).
        """
        recipient = await Employee.get(data.manager_id)
        if not recipient:
            raise HTTPException(status_code=400, detail="Recipient user not found")

        # Check if chat already exists between these two users
        existing = await Chat.find_one(
            Chat.employee_id.id == initiator_id,
            Chat.manager_id.id == PydanticObjectId(data.manager_id)
        )
        if existing:
            return existing

        chat = Chat(
            employee_id=initiator_id,
            manager_id=PydanticObjectId(data.manager_id),
            topic=data.topic,
            status="open"
        )
        await chat.insert()
        logger.info(f"Chat created: {chat.id} between {initiator_id} and {data.manager_id}")
        return chat

    @staticmethod
    async def send_message(chat_id: str, sender_id: PydanticObjectId, text: str) -> Chat:
        chat = await Chat.get(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        # Get the raw IDs from Link objects
        emp_id = str(chat.employee_id.ref.id) if hasattr(chat.employee_id, 'ref') else str(chat.employee_id.id) if hasattr(chat.employee_id, 'id') else str(chat.employee_id)
        mgr_id = str(chat.manager_id.ref.id) if hasattr(chat.manager_id, 'ref') else str(chat.manager_id.id) if hasattr(chat.manager_id, 'id') else str(chat.manager_id)

        if str(sender_id) not in [emp_id, mgr_id]:
            raise HTTPException(status_code=403, detail="Not authorized to send messages in this chat")

        # Get sender's name
        sender = await Employee.get(sender_id)
        sender_name = sender.full_name if sender else "Unknown"

        message = {
            "sender_id": sender_id,
            "sender_name": sender_name,
            "text": text,
            "timestamp": datetime.utcnow(),
            "status": "sent"
        }

        chat.messages.append(message)
        chat.updated_at = datetime.utcnow()
        await chat.save()

        # Broadcast via websocket to connected clients (for REST fallback)
        from app.services.websocket_manager import manager
        broadcast_payload = {
            "type": "message",
            "sender_id": str(sender_id),
            "sender_name": sender_name,
            "text": text,
            "timestamp": message["timestamp"].isoformat(),
            "status": "sent"
        }
        await manager.broadcast(chat_id, broadcast_payload)

        return chat

    @staticmethod
    async def update_status(chat_id: str, status: Literal["open", "approved", "rejected"]) -> Chat:
        chat = await Chat.get(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        chat.status = status
        chat.updated_at = datetime.utcnow()
        await chat.save()
        logger.info(f"Chat {chat_id} status updated to {status}")
        return chat

    @staticmethod
    async def clear_messages(chat_id: str, user_id: PydanticObjectId) -> Chat:
        chat = await Chat.get(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        # Get the raw IDs from Link objects
        emp_id = str(chat.employee_id.ref.id) if hasattr(chat.employee_id, 'ref') else str(chat.employee_id.id) if hasattr(chat.employee_id, 'id') else str(chat.employee_id)
        mgr_id = str(chat.manager_id.ref.id) if hasattr(chat.manager_id, 'ref') else str(chat.manager_id.id) if hasattr(chat.manager_id, 'id') else str(chat.manager_id)

        if str(user_id) not in [emp_id, mgr_id]:
            raise HTTPException(status_code=403, detail="Not authorized to clear this chat")

        chat.messages = []
        chat.updated_at = datetime.utcnow()
        await chat.save()
        
        # Broadcast the clear event to notify connected users
        from app.services.websocket_manager import manager
        await manager.broadcast(chat_id, {"type": "clear_chat"})
        
        return chat
