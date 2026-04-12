from fastapi import Depends, HTTPException, status
from app.models.employee import Employee

# ==================== ASOSIY IMPORTLAR ====================
from app.core.security import oauth2_scheme, verify_token

# get_current_user funksiyasini shu yerda aniqlaymiz
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


async def get_current_active_user(current_user: Employee = Depends(get_current_user)):
    """Har qanday faol foydalanuvchi (barcha rollar)"""
    return current_user


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Employee = Depends(get_current_active_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Ruxsat berilmagan. Sizning rolingiz: {user.role}. "
                       f"Ruxsat berilgan rollar: {self.allowed_roles}"
            )
        return user


# Qo'shimcha qulay dependencylar
def employee_only(user: Employee = Depends(get_current_active_user)):
    """Faqat oddiy xodim (employee) uchun"""
    if user.role != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu funksiya faqat oddiy xodimlar uchun mavjud"
        )
    return user


def manager_or_admin(user: Employee = Depends(get_current_active_user)):
    """Manager yoki Admin uchun"""
    if user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu funksiya faqat manager yoki admin uchun mavjud"
        )
    return user