from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class AttendanceLogBase(BaseModel):
    event_type: Literal["check_in", "check_out", "failed_attempt"]
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    success: bool

class AttendanceLogCreate(AttendanceLogBase):
    employee_id: str

class AttendanceLogOut(AttendanceLogBase):
    id: str
    employee_id: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
