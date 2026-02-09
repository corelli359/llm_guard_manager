import secrets
import time
from typing import Optional
from .session_service import session_service
from .user_service import user_service

class TicketService:
    """Ticket管理服务"""

    def __init__(self):
        self._tickets: dict = {}
        self._ticket_ttl = 300  # 5分钟

    def create_ticket(self, session_id: str, target_system: str) -> dict:
        """基于Session创建Ticket"""
        # 验证Session
        session = session_service.validate_session(session_id)
        if not session:
            return {"success": False, "error": "Session无效或已过期"}

        # 生成Ticket
        ticket = f"TK_{secrets.token_hex(16)}"
        now = time.time()

        self._tickets[ticket] = {
            "user_id": session["user_id"],
            "target_system": target_system,
            "created_at": now,
            "expires_at": now + self._ticket_ttl,
            "used": False
        }

        return {
            "success": True,
            "ticket": ticket,
            "expires_in": self._ticket_ttl,
            "target_system": target_system
        }

    def validate_ticket(self, ticket: str) -> dict:
        """验证Ticket"""
        if ticket not in self._tickets:
            return {"valid": False, "error": "Ticket无效"}

        ticket_data = self._tickets[ticket]

        if time.time() > ticket_data["expires_at"]:
            return {"valid": False, "error": "Ticket已过期"}

        if ticket_data["used"]:
            return {"valid": False, "error": "Ticket已被使用"}

        # 标记为已使用
        ticket_data["used"] = True

        # 获取用户信息
        user = user_service.get_user_by_id(ticket_data["user_id"])
        if not user:
            return {"valid": False, "error": "用户不存在"}

        return {
            "valid": True,
            "user_id": user["user_id"],
            "user_name": user["user_name"],
            "email": user["email"],
            "department": user["department"],
            "phone": user["phone"]
        }


# 单例
ticket_service = TicketService()
