from typing import Optional
from pydantic import BaseModel

class BiometricVerifyRequest(BaseModel):
    image_base64: Optional[str] = None      
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class BiometricVerifyResponse(BaseModel):
    allowed: bool
    employee_id: Optional[str] = None
    reason: Optional[str] = None
    match_score: Optional[float] = None
