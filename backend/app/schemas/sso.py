"""SSO相关Schema"""
from typing import Optional, List
from pydantic import BaseModel


class SSOLoginRequest(BaseModel):
    """SSO登录请求"""
    ticket: str


class SSOLoginResponse(BaseModel):
    """SSO登录响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    role: str


class SSOUserInfoResponse(BaseModel):
    """SSO用户信息响应"""
    user_id: str
    user_name: str
    email: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    role: str
    scenarios: List[dict] = []


class SSOBatchUsersRequest(BaseModel):
    """批量获取用户请求"""
    user_ids: List[str]


class SSOUserBrief(BaseModel):
    """用户简要信息"""
    user_id: str
    user_name: str
    email: Optional[str] = None
    department: Optional[str] = None


class SSOBatchUsersResponse(BaseModel):
    """批量获取用户响应"""
    users: List[SSOUserBrief]
    not_found: List[str]
