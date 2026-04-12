from fastapi import APIRouter, Request, Depends
from app.schemas.biometric import BiometricVerifyRequest, BiometricVerifyResponse
from app.services.attendance_service import AttendanceService
from app.core.deps import get_current_user
from app.models.employee import Employee

router = APIRouter()

@router.post("/check-in", response_model=BiometricVerifyResponse)
async def check_in(request: Request, data: BiometricVerifyRequest):
    auth_header = request.headers.get("Authorization")
    fallback_employee_id = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            from app.core.security import verify_token
            payload = verify_token(token)
            if payload and payload.sub:
                fallback_employee_id = payload.sub
        except:
            pass

    return await AttendanceService.verify_and_log(
        image_base64=data.image_base64,
        event_type="check_in",
        ip_address=request.client.host,
        latitude=data.latitude,
        longitude=data.longitude,
        fallback_employee_id=fallback_employee_id
    )

@router.post("/check-out", response_model=BiometricVerifyResponse)
async def check_out(request: Request, data: BiometricVerifyRequest):
    auth_header = request.headers.get("Authorization")
    fallback_employee_id = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            from app.core.security import verify_token
            payload = verify_token(token)
            if payload and payload.sub:
                fallback_employee_id = payload.sub
        except:
            pass

    return await AttendanceService.verify_and_log(
        image_base64=data.image_base64,
        event_type="check_out",
        ip_address=request.client.host,
        latitude=data.latitude,
        longitude=data.longitude,
        fallback_employee_id=fallback_employee_id
    )

@router.get("/my-stats")
async def get_my_stats(user: Employee = Depends(get_current_user)):
    return await AttendanceService.get_employee_stats(str(user.id))

@router.get("/my-history")
async def get_my_history(user: Employee = Depends(get_current_user)):
    return await AttendanceService.get_employee_history(str(user.id))
