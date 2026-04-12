from datetime import datetime, timedelta
from typing import List, Dict
from app.models.employee import Employee
from app.models.attendance import AttendanceLog
from app.models.organization import OrganizationLocation
from app.schemas.employee import EmployeeUpdate
from app.schemas.organization import OrganizationLocationUpdate
from fastapi import HTTPException

from app.core.security import get_password_hash

class AdminService:
    @staticmethod
    async def get_all_employees() -> List[Employee]:
        return await Employee.find_all().to_list()

    @staticmethod
    async def update_employee(employee_id: str, data: EmployeeUpdate) -> Employee:
        employee = await Employee.get(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        update_data = data.model_dump(exclude_unset=True)
        if "password" in update_data:
            employee.password_hash = get_password_hash(update_data.pop("password"))
            
        for key, value in update_data.items():
            setattr(employee, key, value)
        
        employee.updated_at = datetime.utcnow()
        await employee.save()
        return employee

    @staticmethod
    async def delete_employee(employee_id: str):
        employee = await Employee.get(employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        await employee.delete()

    @staticmethod
    async def get_daily_analytics() -> List[Dict]:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        logs = await AttendanceLog.find(AttendanceLog.timestamp >= today).to_list()
        
        analytics = []
        # Group by employee_id or similar
        # For MVP, just return the logs with basic info
        return logs

    @staticmethod
    async def get_failed_attempts() -> List[AttendanceLog]:
        return await AttendanceLog.find(AttendanceLog.event_type == "failed_attempt").to_list()

    @staticmethod
    async def get_monthly_summary() -> List[Dict]:
        # Implementation for monthly summary
        # Grouping by employee and counting successes
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        logs = await AttendanceLog.find(AttendanceLog.timestamp >= thirty_days_ago).to_list()
        
        # Simple summary logic
        summary = {}
        for log in logs:
            if log.employee_id:
                eid = str(log.employee_id.id)
                if eid not in summary:
                    summary[eid] = {"check_ins": 0, "check_outs": 0}
                if log.event_type == "check_in":
                    summary[eid]["check_ins"] += 1
                elif log.event_type == "check_out":
                    summary[eid]["check_outs"] += 1
        
        return [{"employee_id": k, **v} for k, v in summary.items()]

    @staticmethod
    async def get_organization_location() -> OrganizationLocation:
        loc = await OrganizationLocation.find_one({})
        if not loc:
            raise HTTPException(status_code=404, detail="Organization location not set")
        return loc

    @staticmethod
    async def update_organization_location(data: OrganizationLocationUpdate) -> OrganizationLocation:
        loc = await OrganizationLocation.find_one({})
        if not loc:
            loc = OrganizationLocation(**data.model_dump())
            await loc.insert()
        else:
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(loc, key, value)
            await loc.save()
        return loc
