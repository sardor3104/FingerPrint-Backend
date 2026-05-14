from typing import List
from fastapi import APIRouter, Depends
from app.schemas.employee import EmployeeOut, EmployeeUpdate
from app.schemas.organization import OrganizationLocationOut, OrganizationLocationUpdate
from app.services.admin_service import AdminService
from app.core.deps import RoleChecker

router = APIRouter()

@router.get("/employees", response_model=List[EmployeeOut], dependencies=[Depends(RoleChecker(["admin"]))])
async def list_employees():
    return await AdminService.get_all_employees()

@router.patch("/employees/{id}", response_model=EmployeeOut, dependencies=[Depends(RoleChecker(["admin"]))])
async def update_employee(id: str, data: EmployeeUpdate):
    return await AdminService.update_employee(id, data)

@router.delete("/employees/{id}", dependencies=[Depends(RoleChecker(["admin"]))])
async def delete_employee(id: str):
    await AdminService.delete_employee(id)
    return {"message": "Employee deleted"}

@router.get("/analytics/daily", dependencies=[Depends(RoleChecker(["admin", "manager"]))])
async def daily_analytics():
    return await AdminService.get_daily_analytics()

@router.get("/analytics/attempts", dependencies=[Depends(RoleChecker(["admin", "manager"]))])
async def failed_attempts():
    return await AdminService.get_failed_attempts()

@router.get("/analytics/monthly", dependencies=[Depends(RoleChecker(["admin", "manager"]))])
async def monthly_summary():
    return await AdminService.get_monthly_summary()

@router.get("/organization-location", response_model=OrganizationLocationOut, dependencies=[Depends(RoleChecker(["admin"]))])
async def get_org_location():
    return await AdminService.get_organization_location()

@router.post("/organization-location", response_model=OrganizationLocationOut, dependencies=[Depends(RoleChecker(["admin"]))])
async def update_org_location(data: OrganizationLocationUpdate):
    return await AdminService.update_organization_location(data)
