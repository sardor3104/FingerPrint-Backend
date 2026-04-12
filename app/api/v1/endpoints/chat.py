from fastapi import APIRouter, Depends
from app.schemas.chat import ChatCreate, ChatUpdate, MessageCreate
from app.services.chat_service import ChatService
from app.core.deps import RoleChecker
from app.models.employee import Employee
from app.models.chat import Chat

router = APIRouter()

def _format_chat(c: Chat):
    def extract_id(link_field):
        if hasattr(link_field, 'ref') and hasattr(link_field.ref, 'id'):
            return str(link_field.ref.id)
        elif hasattr(link_field, 'id'):
            return str(link_field.id)
        return str(link_field)

    emp_id = extract_id(c.employee_id)
    mgr_id = extract_id(c.manager_id)

    messages = []
    for m in c.messages:
        messages.append({
            "sender_id": str(m.get("sender_id", "")),
            "sender_name": m.get("sender_name", ""),
            "text": m.get("text", ""),
            "timestamp": m.get("timestamp").isoformat() if hasattr(m.get("timestamp"), "isoformat") else str(m.get("timestamp", "")),
            "status": m.get("status", "sent"),
        })

    return {
        "id": str(c.id),
        "employee_id": emp_id,
        "manager_id": mgr_id,
        "topic": c.topic,
        "messages": messages,
        "status": c.status,
        "created_at": c.created_at.isoformat(),
        "updated_at": c.updated_at.isoformat(),
    }

# ==================== XODIM VA MANAGER UCHUN ====================
@router.post("/create")
async def create_chat(
    data: ChatCreate,
    current_user: Employee = Depends(RoleChecker(["employee", "manager", "admin"]))
):
    c = await ChatService.create_chat(current_user.id, data)
    return _format_chat(c)


@router.post("/{chat_id}/send")
async def send_message(
    chat_id: str,
    data: MessageCreate,
    current_user: Employee = Depends(RoleChecker(["employee", "manager", "admin"]))
):
    c = await ChatService.send_message(chat_id, current_user.id, data.text)
    return _format_chat(c)

@router.delete("/{chat_id}/messages")
async def clear_messages(
    chat_id: str,
    current_user: Employee = Depends(RoleChecker(["employee", "manager", "admin"]))
):
    c = await ChatService.clear_messages(chat_id, current_user.id)
    return _format_chat(c)


@router.get("/my-chats")
async def get_my_chats(
    current_user: Employee = Depends(RoleChecker(["employee", "manager", "admin"]))
):
    uid = current_user.id
    
    as_initiator = await Chat.find(Chat.employee_id.id == uid).to_list()
    as_recipient = await Chat.find(Chat.manager_id.id == uid).to_list()

    # Merge and deduplicate
    seen = set()
    result = []
    for chat in as_initiator + as_recipient:
        key = str(chat.id)
        if key not in seen:
            seen.add(key)
            result.append(chat)

    result.sort(key=lambda c: c.updated_at, reverse=True)

    return [_format_chat(c) for c in result]


# ==================== FAQAT MANAGER VA ADMIN UCHUN ====================
@router.patch("/{chat_id}/status")
async def update_chat_status(
    chat_id: str,
    data: ChatUpdate,
    current_user: Employee = Depends(RoleChecker(["manager", "admin"]))
):
    c = await ChatService.update_status(chat_id, data.status)
    return _format_chat(c)