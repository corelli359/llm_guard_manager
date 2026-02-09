import secrets
import time
from typing import Optional

class SessionService:
    """Session管理服务"""

    def __init__(self):
        self._sessions: dict = {}
        self._session_ttl = 28800  # 8小时

    def create_session(self, user_id: str) -> dict:
        """创建Session"""
        session_id = f"SES_{secrets.token_hex(8)}"
        now = time.time()

        self._sessions[session_id] = {
            "user_id": user_id,
            "created_at": now,
            "expires_at": now + self._session_ttl
        }

        return {
            "session_id": session_id,
            "expires_in": self._session_ttl
        }

    def validate_session(self, session_id: str) -> Optional[dict]:
        """验证Session，返回Session数据或None"""
        if session_id not in self._sessions:
            return None

        session = self._sessions[session_id]

        if time.time() > session["expires_at"]:
            # 过期，删除
            del self._sessions[session_id]
            return None

        return session

    def get_user_id(self, session_id: str) -> Optional[str]:
        """从Session获取user_id"""
        session = self.validate_session(session_id)
        if session:
            return session["user_id"]
        return None


# 单例
session_service = SessionService()
