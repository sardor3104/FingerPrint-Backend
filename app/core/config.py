from typing import List, Optional, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, validator
import json

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    PROJECT_NAME: str = "Secure Fingerprint Attendance"
    API_V1_STR: str = "/api/v1"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 # 30 days
    
    # MongoDB
    MONGODB_URL: str
    DATABASE_NAME: str = "attendance_db"
    
    # SMTP
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_USER: Optional[str] = "sabduhoshimov536@gmail.com"
    SMTP_PASSWORD: Optional[str] = "ckxuhiyxxpudzroh"
    EMAILS_FROM_EMAIL: Optional[EmailStr] = "sabduhoshimov536@gmail.com"
    EMAILS_FROM_NAME: Optional[str] = "Fingerprint Attendance"

    # Biometric
    BIOMETRIC_THRESHOLD: float = 40.0
    
    # CORS
    BACKEND_CORS_ORIGINS: Any = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            return json.loads(v)
        elif isinstance(v, (list, str)):
            return v
        return v

settings = Settings()
