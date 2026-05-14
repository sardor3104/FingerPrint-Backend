from typing import List, Literal, Optional
from pydantic import BaseModel
from datetime import datetime

class MessageBase(BaseModel):
    text: str

class MessageCreate(MessageBase):
    pass

class MessageOut(MessageBase):
    sender_id: str
    timestamp: datetime
    status: Literal["sent", "read"]

class ChatBase(BaseModel):
    topic: str = "Umumiy suhbat"

class ChatCreate(ChatBase):
    manager_id: str
    topic: str = "Umumiy suhbat"

class ChatUpdate(BaseModel):
    status: Optional[Literal["open", "approved", "rejected"]] = None

class ChatOut(ChatBase):
    id: str
    employee_id: str
    manager_id: str
    messages: List[MessageOut]
    status: Literal["open", "approved", "rejected"]
    created_at: datetime
    updated_at: datetime
