from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import LoginRequest, Token, LoginResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.schemas.employee import EmployeeCreate, EmployeeOut
from app.services.auth_service import AuthService
from app.services.email_service import send_reset_password_email
from app.core.deps import RoleChecker, get_current_user
from app.core.security import create_access_token, verify_token, get_password_hash
from app.models.employee import Employee

router = APIRouter()

@router.post("/register", response_model=EmployeeOut, dependencies=[Depends(RoleChecker(["admin"]))])
async def register(data: EmployeeCreate):
    return await AuthService.register_employee(data)

@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest):
    return await AuthService.authenticate(data)

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    user = await Employee.find_one(Employee.email == data.email)
    if user:
        from datetime import timedelta
        # Use 30-minute expiry for password reset tokens
        token = create_access_token(user.id, user.role, expires_delta=timedelta(minutes=30))
        await send_reset_password_email(user.email, token)
    return {"message": "If the email exists, a reset link has been sent."}

@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    token_data = verify_token(data.token)
    if not token_data:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    user = await Employee.get(token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.password_hash = get_password_hash(data.new_password)
    await user.save()
    return {"message": "Password updated successfully."}
