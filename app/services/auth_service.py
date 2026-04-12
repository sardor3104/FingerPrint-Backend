from fastapi import HTTPException, status
from loguru import logger

from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.models.employee import Employee
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo
from app.schemas.employee import EmployeeCreate
from app.services.biometric_service import BiometricService


class AuthService:

    @staticmethod
    async def register_employee(data: EmployeeCreate) -> Employee:
        # 1. Email va JSHSHIR unikalligini tekshirish
        existing = await Employee.find_one(Employee.email == data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        existing_jshshir = await Employee.find_one(Employee.jshshir == data.jshshir)
        if existing_jshshir:
            raise HTTPException(status_code=400, detail="JSHSHIR already registered")

        # 2. Parolni hash qilish
        hashed_password = get_password_hash(data.password)

        # 3. Fingerprint rasmni qayta ishlash (ixtiyoriy)
        fingerprint_minutiae = []
        
        if data.fingerprint_image_base64:   # agar rasm yuborilgan bo'lsa
            try:
                # Rasmni dekod qilish va minutiae chiqarish
                img = BiometricService.decode_image(data.fingerprint_image_base64)
                skeleton = BiometricService.preprocess_fingerprint(img)
                fingerprint_minutiae = BiometricService.extract_minutiae(skeleton)

                if len(fingerprint_minutiae) < 8:   # minimal sifat tekshiruvi
                    raise HTTPException(
                        status_code=400,
                        detail="Fingerprint image quality is too low. Please upload a clearer image."
                    )

                logger.info(f"Fingerprint processed: {len(fingerprint_minutiae)} minutiae points extracted.")

            except Exception as e:
                logger.error(f"Fingerprint processing failed during registration: {e}")
                raise HTTPException(
                    status_code=400,
                    detail="Invalid fingerprint image. Please make sure the image is clear and try again."
                )

        # 4. Yangi xodimni yaratish
        new_employee = Employee(
            jshshir=data.jshshir,
            full_name=data.full_name,
            birth_date=data.birth_date,
            phone=data.phone,
            email=data.email,
            role=data.role,
            password_hash=hashed_password,
            fingerprint_minutiae=fingerprint_minutiae,   # bo'sh bo'lsa ham saqlanadi
        )

        await new_employee.insert()

        has_fingerprint = "Yes" if fingerprint_minutiae else "No"
        logger.info(f"Registered new employee: {new_employee.email} | Fingerprint: {has_fingerprint}")

        return new_employee

    @staticmethod
    async def authenticate(data: LoginRequest) -> LoginResponse:
        user = await Employee.find_one(Employee.email == data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        
        access_token = create_access_token(user.id, user.role)
        refresh_token = create_refresh_token(user.id, user.role)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserInfo(
                id=str(user.id),
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                phone=user.phone
            )
        )