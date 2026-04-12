from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel

class PermissionCreate(BaseModel):
    type: str # 'kunlik', 'soatlik', 'masofaviy'
    start_time: datetime
    end_time: datetime
    reason: str

class PermissionUpdate(BaseModel):
    status: Literal["approved", "denied"]

class PermissionOut(BaseModel):
    id: str
    employee_id: str
    employee_name: str
    type: str
    start_time: datetime
    end_time: datetime
    reason: str
    status: Literal["pending", "approved", "denied"]
    reviewed_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
