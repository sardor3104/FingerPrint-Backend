from datetime import datetime
from typing import List, Literal, Optional
from beanie import Document, Link
from pydantic import Field
from .employee import Employee

class PermissionRequest(Document):
    employee_id: Link[Employee]
    type: str # 'leave', 'work_from_home', 'hourly', etc.
    start_time: datetime
    end_time: datetime
    reason: str
    status: Literal["pending", "approved", "denied"] = "pending"
    reviewed_by_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "permission_requests"
