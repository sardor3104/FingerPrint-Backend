import asyncio
from app.core.database import init_db
from app.models.employee import Employee

async def main():
    await init_db()
    users = await Employee.find_all().to_list()
    if not users:
        print("NO USERS FOUND in database!")
    for u in users:
        print(f"email={u.email} | role={u.role} | name={u.full_name}")

asyncio.run(main())
