"""
权限查询 API
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.api.v1.deps import get_current_user_full
from app.models.db_meta import User
from app.services.permission import PermissionService
from app.schemas.permission import (
    UserPermissionsResponse,
    PermissionCheckRequest,
    PermissionCheckResponse
)

router = APIRouter()


@router.get("/me", response_model=UserPermissionsResponse)
async def get_my_permissions(
    current_user: User = Depends(get_current_user_full),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    获取当前用户的完整权限信息

    Returns:
        用户权限信息，包括角色和所有场景的权限配置
    """
    perm_service = PermissionService(db)
    permissions = await perm_service.get_user_permissions(current_user.id)
    return permissions


@router.post("/check", response_model=PermissionCheckResponse)
async def check_permission(
    request: PermissionCheckRequest,
    current_user: User = Depends(get_current_user_full),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    检查当前用户是否有特定权限

    Args:
        request: 权限检查请求（scenario_id, permission）

    Returns:
        是否有权限
    """
    perm_service = PermissionService(db)
    has_permission = await perm_service.check_scenario_permission(
        current_user.id,
        request.scenario_id,
        request.permission
    )

    return {"has_permission": has_permission}
