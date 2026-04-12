from datetime import date, datetime
from typing import List, Literal
from beanie import Document, Indexed
from pydantic import EmailStr, Field

class Employee(Document):
    jshshir: Indexed(str, unique=True)
    full_name: str
    birth_date: date
    phone: str
    email: Indexed(EmailStr, unique=True)
    password_hash: str
    fingerprint_minutiae: List[dict] = Field(default_factory=list)  # ← default bo'sh ro'yxat
    role: Literal["employee", "manager", "admin"] = "employee"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "employees"