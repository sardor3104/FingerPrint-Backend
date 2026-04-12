from fastapi import APIRouter, Request
from app.schemas.biometric import BiometricVerifyRequest, BiometricVerifyResponse
from app.services.attendance_service import AttendanceService

router = APIRouter()

@router.post("/verify", response_model=BiometricVerifyResponse)
async def verify_biometric(request: Request, data: BiometricVerifyRequest):
    # This uses the same logic as check-in but doesn't necessarily have to be check-in
    # For now, it leverages AttendanceService.verify_and_log but we could refactor 
    # if pure verification without logging is needed.
    # The prompt says "match against stored -> return {allowed, employee_id, reason}"
    return await AttendanceService.verify_and_log(
        image_base64=data.image_base64,
        event_type="verification_only",
        ip_address=request.client.host,
        latitude=data.latitude,
        longitude=data.longitude
    )
