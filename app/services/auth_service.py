from datetime import timedelta
from fastapi import HTTPException, status
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.models.employee import Employee
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo
from app.schemas.employee import EmployeeCreate
from loguru import logger

class AuthService:
    @staticmethod
    async def register_employee(data: EmployeeCreate) -> Employee:
        existing = await Employee.find_one(Employee.email == data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        existing_jshshir = await Employee.find_one(Employee.jshshir == data.jshshir)
        if existing_jshshir:
            raise HTTPException(status_code=400, detail="JSHSHIR already registered")
            
        hashed_password = get_password_hash(data.password)
        new_employee = Employee(
            **data.model_dump(exclude={"password"}),
            password_hash=hashed_password
        )
        await new_employee.insert()
        logger.info(f"Registered new employee: {new_employee.email}")
        return new_employee

    @staticmethod
    async def authenticate(data: LoginRequest) -> LoginResponse:
        user = await Employee.find_one(Employee.email == data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        
        access_token = create_access_token(user.id, user.role)
        refresh_token = create_refresh_token(user.id, user.role)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserInfo(
                id=str(user.id),
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                phone=user.phone
            )
        )
