from fastapi import APIRouter, Depends
from app.core.deps import RoleChecker, get_current_user
from app.models.employee import Employee
from app.schemas.employee import EmployeeOut, UserUpdate
from app.core.security import get_password_hash
from datetime import datetime

router = APIRouter()


@router.get("/me", response_model=EmployeeOut)
async def get_me(current_user: Employee = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=EmployeeOut)
async def update_me(
    data: UserUpdate,
    current_user: Employee = Depends(RoleChecker(["employee", "manager", "admin"]))
):
    update_data = data.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        current_user.password_hash = get_password_hash(update_data.pop("password"))
        
    for key, value in update_data.items():
        setattr(current_user, key, value)
        
    current_user.updated_at = datetime.utcnow()
    await current_user.save()
    return current_user


@router.get("/contacts")
async def get_contacts(
    current_user: Employee = Depends(RoleChecker(["employee", "manager", "admin"]))
):
    """Barcha boshqa xodimlarni kontakt sifatida qaytaradi"""
    contacts = await Employee.find(
        Employee.id != current_user.id
    ).to_list()

    return [
        {
            "id": str(u.id),
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role,
        }
        for u in contacts
    ]