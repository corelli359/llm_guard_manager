"""
场景管理员权限配置 Schema
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ScenarioAdminPermissionBase(BaseModel):
    """场景管理员权限配置基础 Schema"""
    scenario_basic_info: bool = True
    scenario_keywords: bool = True
    scenario_policies: bool = False
    playground: bool = True
    performance_test: bool = False


class ScenarioAdminPermissionCreate(ScenarioAdminPermissionBase):
    """创建场景管理员权限配置"""
    user_id: str
    scenario_id: str


class ScenarioAdminPermissionUpdate(BaseModel):
    """更新场景管理员权限配置"""
    scenario_basic_info: Optional[bool] = None
    scenario_keywords: Optional[bool] = None
    scenario_policies: Optional[bool] = None
    playground: Optional[bool] = None
    performance_test: Optional[bool] = None


class ScenarioAdminPermissionResponse(ScenarioAdminPermissionBase):
    """场景管理员权限配置响应"""
    id: str
    user_id: str
    scenario_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
