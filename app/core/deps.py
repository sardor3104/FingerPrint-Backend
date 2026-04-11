from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_token, oauth2_scheme
from app.models.employee import Employee
from app.schemas.auth import TokenPayload

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Employee:
    token_data = verify_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await Employee.get(token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_active_user(current_user: Employee = Depends(get_current_user)) -> Employee:
    # Any additional checks like is_active can go here
    return current_user

class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Employee = Depends(get_current_active_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FOR_FORBIDDEN,
                detail="The user doesn't have enough privileges",
            )
        return user
