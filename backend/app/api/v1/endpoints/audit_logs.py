"""
审计日志 API
"""

from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.api.v1.deps import get_current_user_full, require_role
from app.models.db_meta import User
from app.services.audit import AuditService
from app.repositories.audit_log import AuditLogRepository
from app.models.db_meta import AuditLog
from app.schemas.audit_log import AuditLogResponse

router = APIRouter()


@router.get("/", response_model=List[AuditLogResponse])
async def query_audit_logs(
    user_id: Optional[str] = Query(None, description="用户ID"),
    username: Optional[str] = Query(None, description="用户名"),
    action: Optional[str] = Query(None, description="操作类型"),
    resource_type: Optional[str] = Query(None, description="资源类型"),
    scenario_id: Optional[str] = Query(None, description="场景ID"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN", "AUDITOR"])),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    查询审计日志

    权限：仅 SYSTEM_ADMIN 和 AUDITOR

    Args:
        user_id: 用户ID（可选）
        username: 用户名（可选）
        action: 操作类型（可选）
        resource_type: 资源类型（可选）
        scenario_id: 场景ID（可选）
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
        skip: 跳过记录数
        limit: 返回记录数

    Returns:
        审计日志列表
    """
    audit_repo = AuditLogRepository(AuditLog, db)

    logs = await audit_repo.search_logs(
        user_id=user_id,
        username=username,
        action=action,
        resource_type=resource_type,
        scenario_id=scenario_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )

    return logs


@router.get("/count")
async def count_audit_logs(
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    scenario_id: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN", "AUDITOR"])),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    统计审计日志数量

    权限：仅 SYSTEM_ADMIN 和 AUDITOR

    Returns:
        日志数量
    """
    audit_repo = AuditLogRepository(AuditLog, db)

    count = await audit_repo.count_logs(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        scenario_id=scenario_id,
        start_date=start_date,
        end_date=end_date
    )

    return {"count": count}
