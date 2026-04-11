from fastapi import APIRouter, Request, Depends
from app.schemas.biometric import BiometricVerifyRequest, BiometricVerifyResponse
from app.services.attendance_service import AttendanceService
from app.core.deps import get_current_user
from app.models.employee import Employee

router = APIRouter()

@router.post("/check-in", response_model=BiometricVerifyResponse)
async def check_in(request: Request, data: BiometricVerifyRequest):
    return await AttendanceService.verify_and_log(
        image_base64=data.image_base64,
        event_type="check_in",
        ip_address=request.client.host
    )

@router.post("/check-out", response_model=BiometricVerifyResponse)
async def check_out(request: Request, data: BiometricVerifyRequest):
    return await AttendanceService.verify_and_log(
        image_base64=data.image_base64,
        event_type="check_out",
        ip_address=request.client.host
    )

@router.get("/my-stats")
async def get_my_stats(user: Employee = Depends(get_current_user)):
    return await AttendanceService.get_employee_stats(str(user.id))

@router.get("/my-history")
async def get_my_history(user: Employee = Depends(get_current_user)):
    return await AttendanceService.get_employee_history(str(user.id))
