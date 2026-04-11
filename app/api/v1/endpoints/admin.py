from typing import List
from fastapi import APIRouter, Depends
from app.schemas.employee import EmployeeOut, EmployeeUpdate
from app.services.admin_service import AdminService
from app.core.deps import RoleChecker

router = APIRouter(dependencies=[Depends(RoleChecker(["admin"]))])

@router.get("/employees", response_model=List[EmployeeOut])
async def list_employees():
    return await AdminService.get_all_employees()

@router.patch("/employees/{id}", response_model=EmployeeOut)
async def update_employee(id: str, data: EmployeeUpdate):
    return await AdminService.update_employee(id, data)

@router.delete("/employees/{id}")
async def delete_employee(id: str):
    await AdminService.delete_employee(id)
    return {"message": "Employee deleted"}

@router.get("/analytics/daily")
async def daily_analytics():
    return await AdminService.get_daily_analytics()

@router.get("/analytics/attempts")
async def failed_attempts():
    return await AdminService.get_failed_attempts()

@router.get("/analytics/monthly")
async def monthly_summary():
    return await AdminService.get_monthly_summary()
