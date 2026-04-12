from typing import List, Literal, Optional, Any
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date, datetime
import re


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

    @field_validator("birth_date", mode="before")
    @classmethod
    def parse_birth_date(cls, v: Any) -> date:
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            # Try various formats
            formats = [
                "%Y-%m-%d",    # 2000-11-02
                "%d-%b-%Y",    # 02-Nov-2000
                "%d.%m.%Y",    # 02.11.2000
                "%d/%m/%Y",    # 02/11/2000
                "%Y/%m/%d"     # 2000/11/02
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
            
            # Try to catch common "Nov" style even if locale differs
            # Simple month name map as fallback
            month_map = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            match = re.match(r'(\d{1,2})[-./ ]([A-Za-z]{3})[-./ ](\d{4})', v)
            if match:
                day, mon, year = match.groups()
                mon_idx = month_map.get(mon.lower())
                if mon_idx:
                    return date(int(year), mon_idx, int(day))

        raise ValueError(f"Birth date format not recognized: {v}. Use YYYY-MM-DD or DD-MMM-YYYY.")


class EmployeeCreate(EmployeeBase):
    password: str
    
    # Yangi ixtiyoriy rasm maydoni (foydalanuvchi uchun qulay)
    fingerprint_image_base64: Optional[str] = Field(
        default=None,
        description="Base64 encoded fingerprint image (optional)"
    )
    
    # Eski minutiae maydonini yashiramiz (foydalanuvchi ko'rmasin)
    fingerprint_minutiae: Optional[List[MinutiaePoint]] = Field(
        default=None, 
        exclude=True
    )

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Literal["employee", "manager", "admin"]] = None
    password: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class EmployeeOut(EmployeeBase):
    id: str
    created_at: datetime
    updated_at: datetime
    # fingerprint_minutiae ni chiqarmaslik uchun
    fingerprint_minutiae: Optional[List[MinutiaePoint]] = Field(None, exclude=True)

    @field_validator("id", mode="before")
    @classmethod
    def parse_id(cls, v):
        return str(v) if v else v

    class Config:
        from_attributes = True
