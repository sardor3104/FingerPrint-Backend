from datetime import datetime
from typing import Literal, Optional
from beanie import Document, Link
from .employee import Employee

class AttendanceLog(Document):
    employee_id: Link[Employee]
    timestamp: datetime = datetime.utcnow
    event_type: Literal["check_in", "check_out", "failed_attempt"]
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    success: bool

    class Settings:
        name = "attendance_logs"
