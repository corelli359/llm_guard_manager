"""
权限相关 Schema
"""

from pydantic import BaseModel
from typing import List, Dict


class PermissionInfo(BaseModel):
    """权限信息"""
    scenario_basic_info: bool
    scenario_keywords: bool
    scenario_policies: bool
    playground: bool
    performance_test: bool


class ScenarioPermissionInfo(BaseModel):
    """场景权限信息"""
    scenario_id: str
    scenario_name: str
    role: str
    permissions: PermissionInfo


class UserPermissionsResponse(BaseModel):
    """用户权限响应"""
    role: str
    scenarios: List[ScenarioPermissionInfo]


class PermissionCheckRequest(BaseModel):
    """权限检查请求"""
    scenario_id: str
    permission: str


class PermissionCheckResponse(BaseModel):
    """权限检查响应"""
    has_permission: bool
