from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate
from app.services.auth_service import AuthService
from app.core.config import settings

async def test_reg():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(database=client[settings.DATABASE_NAME], document_models=[Employee])
    
    data = {
        "jshshir": "12345678909078",
        "full_name": "Ali Vali",
        "birth_date": "2000-11-02",
        "phone": "+998909008070",
        "email": "sabduhoshimov538@gmail.com",
        "password": "Password",
        "role": "employee",
        "fingerprint_minutiae": []
    }
    
    try:
        # Manually validate schema first
        reg_data = EmployeeCreate(**data)
        print("Schema validation successful")
        
        # Try service
        user = await AuthService.register_employee(reg_data)
        print(f"User created: {user.email}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Use a mock MONGODB_URL if needed, but here we try to connect to the real one if possible
    # Actually, settings might have 'mongodb' which is only reachable inside docker
    # I'll just try to validate the schema for now
    from pydantic import ValidationError
    try:
        data = {
            "jshshir": "12345678909078",
            "full_name": "Ali Vali",
            "birth_date": "2000-11-02",
            "phone": "+998909008070",
            "email": "sabduhoshimov538@gmail.com",
            "password": "Password",
            "role": "employee",
            "fingerprint_minutiae": []
        }
        EmployeeCreate(**data)
        print("Validation Successful")
    except ValidationError as e:
        print(f"Validation Error: {e}")
