from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services import user_service, session_service, ticket_service

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class TicketRequest(BaseModel):
    session_id: str
    target_system: str


class ValidateTicketRequest(BaseModel):
    ticket: str


@router.post("/login")
async def login(request: LoginRequest):
    """用户登录，建立Session"""
    user = user_service.authenticate(request.username, request.password)

    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if user.get("status") != "active":
        raise HTTPException(status_code=403, detail="用户已被禁用")

    session = session_service.create_session(user["user_id"])

    return {
        "success": True,
        "session_id": session["session_id"],
        "user_id": user["user_id"],
        "user_name": user["user_name"],
        "expires_in": session["expires_in"]
    }


@router.post("/ticket")
async def get_ticket(request: TicketRequest):
    """获取Ticket（跳转时调用）"""
    result = ticket_service.create_ticket(
        session_id=request.session_id,
        target_system=request.target_system
    )

    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])

    return result


@router.post("/validate-ticket")
async def validate_ticket(request: ValidateTicketRequest):
    """验证Ticket（目标系统调用）"""
    result = ticket_service.validate_ticket(request.ticket)

    if not result["valid"]:
        raise HTTPException(status_code=401, detail=result["error"])

    return result
