from datetime import datetime
from typing import Optional
from loguru import logger

from app.models.employee import Employee
from app.models.attendance import AttendanceLog
from app.models.organization import OrganizationLocation
from app.services.biometric_service import BiometricService
from app.schemas.biometric import BiometricVerifyResponse
from app.core.utils import haversine_distance
from beanie import PydanticObjectId


class AttendanceService:

    @staticmethod
    async def verify_and_log(
        event_type: str,                    # Majburiy parametr - birinchi o'rinda
        image_base64: Optional[str] = None, # ixtiyoriy (fingerprint rasm)
        device_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        fallback_employee_id: Optional[str] = None  # ixtiyoriy, agar token bo'lsa
    ) -> BiometricVerifyResponse:
        
        best_match_employee = None
        highest_score = 0.0
        reason = None

        # 1. Biometric tekshirish (agar rasm yuborilgan bo'lsa)
        if image_base64:
            try:
                img = BiometricService.decode_image(image_base64)
                skeleton = BiometricService.preprocess_fingerprint(img)
                minutiae_query = BiometricService.extract_minutiae(skeleton)

                employees = await Employee.find_all().to_list()
                
                for employee in employees:
                    if not employee.fingerprint_minutiae or len(employee.fingerprint_minutiae) == 0:
                        continue
                        
                    is_match, score = BiometricService.match_minutiae(
                        minutiae_query, employee.fingerprint_minutiae
                    )
                    if is_match and score > highest_score:
                        highest_score = score
                        best_match_employee = employee

            except Exception as e:
                logger.error(f"Biometric processing failed: {e}")
                return BiometricVerifyResponse(
                    allowed=False, 
                    reason="Invalid image format or processing error"
                )
        elif fallback_employee_id:
            # Agar rasm yo'q bo'lsa-yu, foydalanuvchi tizimga kirgan bo'lsa (frontendda ixtiyoriy qilingan holat)
            best_match_employee = await Employee.get(fallback_employee_id)
            highest_score = 100.0  # token orqali aniq bo'lgani uchun 100%
            if not best_match_employee:
                reason = "Invalid user session"
        else:
            reason = "No biometric image or valid session provided"

        # 2. Geofencing (joylashuv tekshirish)
        if latitude is not None and longitude is not None:
            org_loc = await OrganizationLocation.find_one({})
            if org_loc:
                distance = haversine_distance(
                    latitude, longitude, 
                    org_loc.latitude, org_loc.longitude
                )
                if distance > org_loc.radius_meters:
                    logger.warning(f"Geofencing violation: User is {distance:.2f}m away (radius: {org_loc.radius_meters}m)")
                    
                    # Failed attempt log
                    failed_log = AttendanceLog(
                        employee_id=best_match_employee.id if best_match_employee else None,
                        event_type="failed_attempt",
                        device_id=device_id,
                        ip_address=ip_address,
                        attempt_latitude=latitude,
                        attempt_longitude=longitude,
                        success=False,
                        timestamp=datetime.utcnow()
                    )
                    await failed_log.insert()
                    
                    return BiometricVerifyResponse(
                        allowed=False, 
                        reason=f"Outside organization premises. Distance: {int(distance)}m"
                    )

        # 3. Natijani aniqlash va log saqlash
        success = best_match_employee is not None
        log_type = event_type if success else "failed_attempt"

        log = AttendanceLog(
            employee_id=best_match_employee.id if best_match_employee else None,
            event_type=log_type,
            device_id=device_id,
            ip_address=ip_address,
            attempt_latitude=latitude,
            attempt_longitude=longitude,
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
            logger.warning(f"Attendance failed attempt: {reason or 'No matching fingerprint found'}")
            return BiometricVerifyResponse(
                allowed=False, 
                reason=reason or "No matching fingerprint found"
            )

    @staticmethod
    async def get_employee_stats(employee_id: str):
        from datetime import timedelta
        
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
        check_ins.sort(key=lambda x: x.timestamp)
        last_check_in = check_ins[-1].timestamp.strftime("%I:%M %p") if check_ins else "N/A"

        # Weekly Attendance
        weekly_logs = [log for log in check_ins if log.timestamp >= last_7_days]
        unique_days_this_week = len(set(log.timestamp.date() for log in weekly_logs))
        weekly_attendance_pct = min(100, int((unique_days_this_week / 5) * 100))

        # Monthly Trend
        current_month_logs = [log for log in check_ins if log.timestamp >= last_30_days]
        prev_month_logs = [log for log in check_ins if last_30_days > log.timestamp >= previous_30_days]
        
        curr_days = len(set(log.timestamp.date() for log in current_month_logs))
        prev_days = len(set(log.timestamp.date() for log in prev_month_logs))
        
        if prev_days == 0:
            monthly_trend = f"+{curr_days * 10}%" if curr_days > 0 else "0%"
        else:
            diff = curr_days - prev_days
            trend_pct = int((diff / prev_days) * 100)
            monthly_trend = f"+{trend_pct}%" if trend_pct >= 0 else f"{trend_pct}%"

        # Failed Attempts
        failed = len([log for log in logs 
                     if log.timestamp >= last_30_days and log.event_type == "failed_attempt"])

        # Weekly Chart
        weekly_chart = []
        for i in range(6, -1, -1):
            d = (now - timedelta(days=i)).date()
            day_logs = [l for l in weekly_logs if l.timestamp.date() == d]
            weekly_chart.append({
                "name": d.strftime("%a"), 
                "value": 100 if len(day_logs) > 0 else 0
            })

        # Monthly Chart
        monthly_chart = []
        for i in range(4):
            start_d = last_30_days + timedelta(days=i*7)
            end_d = start_d + timedelta(days=7)
            w_logs = [l for l in current_month_logs if start_d <= l.timestamp < end_d]
            w_days = len(set(l.timestamp.date() for l in w_logs))
            monthly_chart.append({"name": f"Week {i+1}", "value": w_days * 20})

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
        logs = await AttendanceLog.find(
            AttendanceLog.employee_id.id == PydanticObjectId(employee_id)
        ).sort("-timestamp").limit(limit).to_list()
        
        history = []
        for log in logs:
            history.append({
                "id": str(log.id),
                "type": "Check-in" if log.event_type == "check_in" 
                      else "Check-out" if log.event_type == "check_out" 
                      else "Failed",
                "time": log.timestamp.strftime("%I:%M %p"),
                "date": log.timestamp.strftime("%b %d"),
                "status": "Success" if log.success else "Failed"
            })
        return history