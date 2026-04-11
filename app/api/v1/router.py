from fastapi import APIRouter
from app.api.v1.endpoints import auth, attendance, chat, admin, biometric, users, ws

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(biometric.router, prefix="/biometric", tags=["biometric"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(ws.router, prefix="/ws", tags=["websocket"])
