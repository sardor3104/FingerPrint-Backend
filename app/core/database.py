from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from loguru import logger

from app.core.config import settings
from app.models.employee import Employee
from app.models.attendance import AttendanceLog
from app.models.chat import Chat
from app.core.security import get_password_hash
from datetime import date

async def init_db():
    logger.info("Initializing MongoDB connection...")
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[
            Employee,
            AttendanceLog,
            Chat
        ]
    )
    logger.info("MongoDB initialized successfully with Beanie.")
    
    # Seed default admin if no employees exist
    admin_exists = await Employee.find_one({"role": "admin"})
    if not admin_exists:
        logger.info("No admin user found. Seeding default administrator...")
        admin = Employee(
            jshshir="00000000000000",
            full_name="System Administrator",
            birth_date=date(1990, 1, 1),
            phone="+998900000000",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            role="admin",
            fingerprint_minutiae=[]
        )
        await admin.insert()
        logger.info("Default admin user created: admin@example.com / admin123")
