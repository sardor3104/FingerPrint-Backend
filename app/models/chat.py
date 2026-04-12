from datetime import datetime
from typing import List, Literal
from beanie import Document, Link, PydanticObjectId
from pydantic import Field
from .employee import Employee

class ChatMessage(Document):
    sender_id: PydanticObjectId
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: Literal["sent", "read"] = "sent"

class Chat(Document):
    employee_id: Link[Employee]
    manager_id: Link[Employee]
    topic: str
    messages: List[dict] = []  # List of ChatMessage structure as dicts for simplicity or embedded
    status: Literal["open", "approved", "rejected"] = "open"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "chats"
