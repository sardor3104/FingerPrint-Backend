from typing import List
from fastapi import APIRouter, Depends
from beanie import PydanticObjectId
from app.schemas.chat import ChatCreate, ChatOut, ChatUpdate, MessageCreate
from app.services.chat_service import ChatService
from app.core.deps import get_current_user, RoleChecker
from app.models.employee import Employee
from app.models.chat import Chat

router = APIRouter()

@router.post("/create")
async def create_chat(data: ChatCreate, current_user: Employee = Depends(get_current_user)):
    return await ChatService.create_chat(current_user.id, data)

@router.post("/{chat_id}/send")
async def send_message(chat_id: str, data: MessageCreate, current_user: Employee = Depends(get_current_user)):
    return await ChatService.send_message(chat_id, current_user.id, data.text)

@router.get("/my-chats")
async def get_my_chats(current_user: Employee = Depends(get_current_user)):
    """
    Return all chats where the current user is either initiator or recipient.
    """
    uid = current_user.id
    # Fetch as initiator
    as_initiator = await Chat.find(
        Chat.employee_id.id == uid
    ).to_list()
    # Fetch as recipient
    as_recipient = await Chat.find(
        Chat.manager_id.id == uid
    ).to_list()

    # Merge and deduplicate
    seen = set()
    result = []
    for chat in as_initiator + as_recipient:
        key = str(chat.id)
        if key not in seen:
            seen.add(key)
            result.append(chat)

    # Sort by updated_at descending
    result.sort(key=lambda c: c.updated_at, reverse=True)

    # Serialize manually
    output = []
    for c in result:
        emp_id = str(c.employee_id.ref.id) if hasattr(c.employee_id, 'ref') else str(c.employee_id.id) if hasattr(c.employee_id, 'id') else str(c.employee_id)
        mgr_id = str(c.manager_id.ref.id) if hasattr(c.manager_id, 'ref') else str(c.manager_id.id) if hasattr(c.manager_id, 'id') else str(c.manager_id)

        messages = []
        for m in c.messages:
            messages.append({
                "sender_id": str(m.get("sender_id", "")),
                "sender_name": m.get("sender_name", ""),
                "text": m.get("text", ""),
                "timestamp": m.get("timestamp").isoformat() if hasattr(m.get("timestamp"), "isoformat") else str(m.get("timestamp", "")),
                "status": m.get("status", "sent"),
            })

        output.append({
            "id": str(c.id),
            "employee_id": emp_id,
            "manager_id": mgr_id,
            "topic": c.topic,
            "messages": messages,
            "status": c.status,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat(),
        })

    return output

@router.patch("/{chat_id}/status", dependencies=[Depends(RoleChecker(["manager", "admin"]))])
async def update_chat_status(chat_id: str, data: ChatUpdate):
    return await ChatService.update_status(chat_id, data.status)
