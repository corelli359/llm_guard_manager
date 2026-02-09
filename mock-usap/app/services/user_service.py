import json
from pathlib import Path
from typing import Optional

class UserService:
    """用户服务"""

    def __init__(self):
        self._users = self._load_users()

    def _load_users(self) -> list:
        """加载Mock用户数据"""
        data_path = Path(__file__).parent.parent / "data" / "mock_users.json"
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["users"]

    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """验证用户名密码"""
        for user in self._users:
            if user["username"] == username and user["password"] == password:
                return user
        return None

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """根据user_id获取用户"""
        for user in self._users:
            if user["user_id"] == user_id:
                return user
        return None

    def get_users_by_ids(self, user_ids: list) -> tuple[list, list]:
        """批量获取用户，返回(找到的用户列表, 未找到的user_id列表)"""
        found = []
        not_found = []

        for user_id in user_ids:
            user = self.get_user_by_id(user_id)
            if user:
                found.append(user)
            else:
                not_found.append(user_id)

        return found, not_found


# 单例
user_service = UserService()
