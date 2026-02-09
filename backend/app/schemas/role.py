"""角色和权限相关 Schema"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================
# 角色 Schema
# ============================================

class RoleCreate(BaseModel):
    role_code: str = Field(..., max_length=64)
    role_name: str = Field(..., max_length=128)
    role_type: str = Field(default="SCENARIO", pattern="^(GLOBAL|SCENARIO)$")
    description: Optional[str] = None


class RoleUpdate(BaseModel):
    role_name: Optional[str] = Field(None, max_length=128)
    role_type: Optional[str] = Field(None, pattern="^(GLOBAL|SCENARIO)$")
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RoleResponse(BaseModel):
    id: str
    role_code: str
    role_name: str
    role_type: str
    description: Optional[str] = None
    is_system: bool
    is_active: bool
    created_at: datetime
    permission_count: int = 0

    class Config:
        from_attributes = True


class RoleDetailResponse(RoleResponse):
    permissions: List["PermissionResponse"] = []


# ============================================
# 权限 Schema
# ============================================

class PermissionResponse(BaseModel):
    id: str
    permission_code: str
    permission_name: str
    permission_type: str
    scope: str
    parent_code: Optional[str] = None
    sort_order: int = 0

    class Config:
        from_attributes = True


class RolePermissionUpdate(BaseModel):
    permission_ids: List[str] = Field(..., description="权限ID列表")


# ============================================
# 用户角色分配 Schema
# ============================================

class UserRoleAssign(BaseModel):
    role_id: str = Field(..., description="角色ID")
    scenario_id: Optional[str] = Field(None, description="场景ID，全局角色不传")


class UserRoleResponse(BaseModel):
    id: str
    user_id: str
    scenario_id: Optional[str] = None
    role_id: str
    role_code: str = ""
    role_name: str = ""
    role_type: str = ""
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# 用户权限 Schema
# ============================================

class UserPermissionsResponse(BaseModel):
    user_id: str
    global_permissions: List[str] = []  # 全局权限编码列表
    scenario_permissions: dict = {}  # {scenario_id: [permission_codes]}
