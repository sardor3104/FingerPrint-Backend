from fastapi import APIRouter, Depends
from typing import List
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionOut
from app.services.permission_service import PermissionService
from app.models.permission import PermissionRequest
from app.core.deps import RoleChecker, get_current_user
from app.models.employee import Employee

router = APIRouter()

def _format_permission(p: PermissionRequest) -> PermissionOut:
    def extract_id(link_field):
        if hasattr(link_field, 'ref') and hasattr(link_field.ref, 'id'):
            return str(link_field.ref.id)
        elif hasattr(link_field, 'id'):
            return str(link_field.id)
        return str(link_field)

    emp_name = "Unknown"
    # Handling employee link safely to extract name without throwing if not fetched
    if hasattr(p.employee_id, 'full_name'):
        emp_name = p.employee_id.full_name
    elif hasattr(p.employee_id, 'ref') and hasattr(p.employee_id.ref, 'full_name'):
        emp_name = p.employee_id.ref.full_name

    return PermissionOut(
        id=str(p.id),
        employee_id=extract_id(p.employee_id),
        employee_name=emp_name,
        type=p.type,
        start_time=p.start_time,
        end_time=p.end_time,
        reason=p.reason,
        status=p.status,
        reviewed_by_name=p.reviewed_by_name,
        created_at=p.created_at,
        updated_at=p.updated_at
    )

@router.post("/create", response_model=PermissionOut)
async def create_request(
    data: PermissionCreate,
    current_user: Employee = Depends(get_current_user)
):
    req = await PermissionService.create_request(current_user.id, data)
    await req.fetch_all_links() # To get the employee name
    return _format_permission(req)


@router.get("/my", response_model=List[PermissionOut])
async def get_my_requests(
    current_user: Employee = Depends(get_current_user)
):
    reqs = await PermissionRequest.find(
        PermissionRequest.employee_id.id == current_user.id
    ).sort("-created_at").to_list()
    
    for r in reqs:
        await r.fetch_all_links()
        
    return [_format_permission(r) for r in reqs]


@router.get("/team", response_model=List[PermissionOut])
async def get_team_requests(
    current_user: Employee = Depends(RoleChecker(["manager", "admin"]))
):
    reqs = await PermissionRequest.find_all().sort("-created_at").to_list()
    for r in reqs:
        await r.fetch_all_links()
    return [_format_permission(r) for r in reqs]


@router.patch("/{req_id}/status", response_model=PermissionOut)
async def update_status(
    req_id: str,
    data: PermissionUpdate,
    current_user: Employee = Depends(RoleChecker(["manager", "admin"]))
):
    req = await PermissionService.update_status(req_id, data.status, current_user.id)
    await req.fetch_all_links()
    return _format_permission(req)
