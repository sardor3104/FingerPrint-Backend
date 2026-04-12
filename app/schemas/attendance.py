from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, field_validator
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

    @field_validator("id", "employee_id", mode="before")
    @classmethod
    def parse_id(cls, v):
        if hasattr(v, "id"):  # For Link[] objects
            return str(v.id)
        return str(v) if v else v

    model_config = ConfigDict(from_attributes=True)
