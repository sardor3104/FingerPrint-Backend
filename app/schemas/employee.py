from typing import List, Literal, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime

class MinutiaePoint(BaseModel):
    x: int
    y: int
    angle: float
    type: Literal["ending", "bifurcation"]

class EmployeeBase(BaseModel):
    jshshir: str = Field(..., description="Unique passport/ID number")
    full_name: str
    birth_date: date
    phone: str
    email: EmailStr
    role: Literal["employee", "manager", "admin"] = "employee"

class EmployeeCreate(EmployeeBase):
    password: str
    fingerprint_minutiae: List[MinutiaePoint]

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Literal["employee", "manager", "admin"]] = None

class EmployeeOut(EmployeeBase):
    id: str
    created_at: datetime
    updated_at: datetime
