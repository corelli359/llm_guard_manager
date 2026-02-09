"""USAP客户端 - 调用USAP统一认证平台接口"""
import httpx
from typing import Optional
from pydantic import BaseModel
from app.core.config import settings


class TicketValidationResult(BaseModel):
    """Ticket验证结果"""
    valid: bool
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    error: Optional[str] = None


class UserInfo(BaseModel):
    """用户信息"""
    user_id: str
    user_name: str
    email: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None


class USAPClientError(Exception):
    """USAP客户端错误"""
    pass


class USAPClient:
    """USAP统一认证平台客户端"""

    def __init__(self):
        self.base_url = settings.USAP_BASE_URL
        self.client_id = settings.USAP_CLIENT_ID
        self.client_secret = settings.USAP_CLIENT_SECRET
        self.timeout = 5.0

    async def validate_ticket(self, ticket: str) -> TicketValidationResult:
        """
        验证Ticket

        调用USAP接口验证Ticket的有效性，返回用户信息
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/auth/validate-ticket",
                    json={"ticket": ticket},
                    headers={
                        "Content-Type": "application/json",
                        "X-Client-ID": self.client_id,
                        "X-Client-Secret": self.client_secret
                    }
                )

                if response.status_code == 401:
                    data = response.json()
                    return TicketValidationResult(
                        valid=False,
                        error=data.get("detail", "Ticket验证失败")
                    )

                if response.status_code != 200:
                    return TicketValidationResult(
                        valid=False,
                        error=f"USAP服务错误: {response.status_code}"
                    )

                data = response.json()
                return TicketValidationResult(
                    valid=True,
                    user_id=data.get("user_id"),
                    user_name=data.get("user_name"),
                    email=data.get("email"),
                    department=data.get("department"),
                    phone=data.get("phone")
                )

        except httpx.TimeoutException:
            return TicketValidationResult(
                valid=False,
                error="USAP服务超时"
            )
        except Exception as e:
            return TicketValidationResult(
                valid=False,
                error=f"USAP服务异常: {str(e)}"
            )

    async def get_user_info(self, user_id: str) -> Optional[UserInfo]:
        """
        获取用户信息
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/users/{user_id}",
                    headers={
                        "X-Client-ID": self.client_id,
                        "X-Client-Secret": self.client_secret
                    }
                )

                if response.status_code == 404:
                    return None

                if response.status_code != 200:
                    raise USAPClientError(f"USAP服务错误: {response.status_code}")

                data = response.json()
                return UserInfo(
                    user_id=data.get("user_id"),
                    user_name=data.get("user_name"),
                    email=data.get("email"),
                    department=data.get("department"),
                    phone=data.get("phone"),
                    status=data.get("status")
                )

        except httpx.TimeoutException:
            raise USAPClientError("USAP服务超时")
        except USAPClientError:
            raise
        except Exception as e:
            raise USAPClientError(f"USAP服务异常: {str(e)}")

    async def get_users_batch(self, user_ids: list[str]) -> tuple[list[UserInfo], list[str]]:
        """
        批量获取用户信息

        返回: (找到的用户列表, 未找到的user_id列表)
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/users/batch",
                    json={"user_ids": user_ids},
                    headers={
                        "Content-Type": "application/json",
                        "X-Client-ID": self.client_id,
                        "X-Client-Secret": self.client_secret
                    }
                )

                if response.status_code != 200:
                    raise USAPClientError(f"USAP服务错误: {response.status_code}")

                data = response.json()
                users = [
                    UserInfo(
                        user_id=u.get("user_id"),
                        user_name=u.get("user_name"),
                        email=u.get("email"),
                        department=u.get("department")
                    )
                    for u in data.get("users", [])
                ]
                not_found = data.get("not_found", [])

                return users, not_found

        except httpx.TimeoutException:
            raise USAPClientError("USAP服务超时")
        except USAPClientError:
            raise
        except Exception as e:
            raise USAPClientError(f"USAP服务异常: {str(e)}")

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/health")
                return response.status_code == 200
        except:
            return False


# 单例
usap_client = USAPClient()
