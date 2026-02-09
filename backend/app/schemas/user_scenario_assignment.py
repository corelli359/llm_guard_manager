"""
用户场景关联 Schema
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class UserScenarioAssignmentBase(BaseModel):
    """用户场景关联基础 Schema"""
    scenario_id: str
    role: str  # SCENARIO_ADMIN, ANNOTATOR


class UserScenarioAssignmentCreate(UserScenarioAssignmentBase):
    """创建用户场景关联"""
    pass


class UserScenarioAssignmentUpdate(BaseModel):
    """更新用户场景关联"""
    role: Optional[str] = None


class UserScenarioAssignmentResponse(UserScenarioAssignmentBase):
    """用户场景关联响应"""
    id: str
    user_id: str
    created_at: datetime
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
