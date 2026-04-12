from datetime import datetime
from typing import List, Literal
from beanie import PydanticObjectId
from fastapi import HTTPException
from app.models.permission import PermissionRequest
from app.models.employee import Employee
from app.schemas.permission import PermissionCreate, PermissionOut
from loguru import logger

class PermissionService:
    @staticmethod
    async def create_request(user_id: PydanticObjectId, data: PermissionCreate) -> PermissionRequest:
        user = await Employee.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if data.start_time >= data.end_time:
            raise HTTPException(status_code=400, detail="Start time must be before end time")

        req = PermissionRequest(
            employee_id=user.id,
            type=data.type,
            start_time=data.start_time,
            end_time=data.end_time,
            reason=data.reason,
            status="pending"
        )
        await req.insert()
        logger.info(f"Permission requested by {user.full_name}: {data.type}")
        return req

    @staticmethod
    async def update_status(req_id: str, status: Literal["approved", "denied"], manager_id: PydanticObjectId) -> PermissionRequest:
        manager = await Employee.get(manager_id)
        
        req = await PermissionRequest.get(req_id)
        if not req:
            raise HTTPException(status_code=404, detail="Request not found")

        req.status = status
        req.reviewed_by_name = manager.full_name if manager else "Unknown Admin"
        req.updated_at = datetime.utcnow()
        await req.save()
        logger.info(f"Permission {req_id} {status} by {req.reviewed_by_name}")
        return req
