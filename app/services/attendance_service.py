from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from app.models.employee import Employee
from app.models.attendance import AttendanceLog
from app.services.biometric_service import BiometricService
from app.schemas.biometric import BiometricVerifyRequest, BiometricVerifyResponse
from loguru import logger

class AttendanceService:
    @staticmethod
    async def verify_and_log(
        image_base64: str,
        event_type: str,
        device_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> BiometricVerifyResponse:
        # 1. Preprocess and extract minutiae from request image
        try:
            img = BiometricService.decode_image(image_base64)
            skeleton = BiometricService.preprocess_fingerprint(img)
            minutiae_query = BiometricService.extract_minutiae(skeleton)
        except Exception as e:
            logger.error(f"Biometric processing failed: {e}")
            return BiometricVerifyResponse(allowed=False, reason="Invalid image format or processing error")

        # 2. Iterate through employees to find a match (simplified for MVP)
        # In production, use a more efficient indexing or search mechanism
        employees = await Employee.find_all().to_list()
        
        best_match_employee = None
        highest_score = 0.0
        
        for employee in employees:
            if not employee.fingerprint_minutiae:
                continue
                
            is_match, score = BiometricService.match_minutiae(minutiae_query, employee.fingerprint_minutiae)
            if is_match and score > highest_score:
                highest_score = score
                best_match_employee = employee

        # 3. Log the attempt
        success = best_match_employee is not None
        log_type = event_type if success else "failed_attempt"
        
        log = AttendanceLog(
            employee_id=best_match_employee.id if success else None,
            event_type=log_type,
            device_id=device_id,
            ip_address=ip_address,
            success=success,
            timestamp=datetime.utcnow()
        )
        await log.insert()
        
        if success:
            logger.info(f"Attendance success: {best_match_employee.email} - {event_type}")
            return BiometricVerifyResponse(
                allowed=True,
                employee_id=str(best_match_employee.id),
                match_score=highest_score
            )
        else:
            logger.warning(f"Attendance failed attempt from IP: {ip_address}")
            return BiometricVerifyResponse(allowed=False, reason="No matching fingerprint found")

    @staticmethod
    async def get_employee_stats(employee_id: str):
        from datetime import datetime, timedelta
        from beanie import PydanticObjectId
        
        # Calculate last 30 days and 7 days
        now = datetime.utcnow()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        previous_30_days = now - timedelta(days=60)

        logs = await AttendanceLog.find(
            AttendanceLog.employee_id.id == PydanticObjectId(employee_id),
            AttendanceLog.timestamp >= previous_30_days
        ).to_list()

        # Last Check-in
        check_ins = [log for log in logs if log.event_type == "check_in" and log.success]
        # Sort manually just in case
        check_ins.sort(key=lambda x: x.timestamp)
        last_check_in = check_ins[-1].timestamp.strftime("%I:%M %p") if check_ins else "N/A"

        # Weekly Attendance
        weekly_logs = [log for log in check_ins if log.timestamp >= last_7_days]
        unique_days_this_week = len(set([log.timestamp.date() for log in weekly_logs]))
        weekly_attendance_pct = min(100, int((unique_days_this_week / 5) * 100))

        # Monthly Trend
        current_month_logs = [log for log in check_ins if log.timestamp >= last_30_days]
        prev_month_logs = [log for log in check_ins if last_30_days > log.timestamp >= previous_30_days]
        
        curr_days = len(set([log.timestamp.date() for log in current_month_logs]))
        prev_days = len(set([log.timestamp.date() for log in prev_month_logs]))
        
        if prev_days == 0:
            monthly_trend = f"+{curr_days * 10}%" if curr_days > 0 else "0%"
        else:
            diff = curr_days - prev_days
            trend_pct = int((diff / prev_days) * 100)
            monthly_trend = f"+{trend_pct}%" if trend_pct >= 0 else f"{trend_pct}%"

        # Failed Attempts (Replacing Pending Requests)
        failed = len([log for log in logs if log.timestamp >= last_30_days and log.event_type == "failed_attempt"])

        # Chart Data
        weekly_chart = []
        for i in range(6, -1, -1):
            d = (now - timedelta(days=i)).date()
            day_logs = [l for l in weekly_logs if l.timestamp.date() == d]
            weekly_chart.append({"name": d.strftime("%a"), "value": 100 if len(day_logs)>0 else 0})

        monthly_chart = []
        for i in range(4):
            start_d = last_30_days + timedelta(days=i*7)
            end_d = start_d + timedelta(days=7)
            w_logs = [l for l in current_month_logs if start_d <= l.timestamp < end_d]
            w_days = len(set([l.timestamp.date() for l in w_logs]))
            monthly_chart.append({"name": f"Week {i+1}", "value": w_days * 20}) # Approx pct

        return {
            "last_check_in": last_check_in,
            "weekly_attendance": f"{weekly_attendance_pct}%",
            "failed_attempts": str(failed),
            "monthly_trend": monthly_trend,
            "charts": {
                "weekly": weekly_chart,
                "monthly": monthly_chart
            }
        }

    @staticmethod
    async def get_employee_history(employee_id: str, limit: int = 10):
        from beanie import PydanticObjectId
        logs = await AttendanceLog.find(
            AttendanceLog.employee_id.id == PydanticObjectId(employee_id)
        ).sort("-timestamp").limit(limit).to_list()
        
        history = []
        for log in logs:
            history.append({
                "id": str(log.id),
                "type": "Check-in" if log.event_type == "check_in" else ("Check-out" if log.event_type == "check_out" else "Failed"),
                "time": log.timestamp.strftime("%I:%M %p"),
                "date": log.timestamp.strftime("%b %d"),
                "status": "Success" if log.success else "Failed"
            })
        return history
