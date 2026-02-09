"""
审计日志 Schema
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime


class AuditLogBase(BaseModel):
    """审计日志基础 Schema"""
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    scenario_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class AuditLogCreate(AuditLogBase):
    """创建审计日志"""
    user_id: str
    username: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    """审计日志响应"""
    id: str
    user_id: str
    username: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogQuery(BaseModel):
    """审计日志查询参数"""
    user_id: Optional[str] = None
    username: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    scenario_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = 0
    limit: int = 100
