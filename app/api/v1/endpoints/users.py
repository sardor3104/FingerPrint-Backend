from typing import List
from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.models.employee import Employee

router = APIRouter()

@router.get("/me")
async def get_me(current_user: Employee = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "phone": current_user.phone,
    }

@router.get("/contacts")
async def get_contacts(current_user: Employee = Depends(get_current_user)):
    """
    Returns ALL other users as potential chat contacts.
    Any user can chat with any other user.
    """
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
