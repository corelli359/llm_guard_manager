"""
权限检查辅助函数
用于在 API 端点中简化权限检查逻辑（V2 RBAC）
"""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_meta import User
from app.repositories.role import UserScenarioRoleRepository


async def _check_v2_permission(user_id: str, scenario_id: str, db: AsyncSession, permission: str = None) -> bool:
    """V2 RBAC 权限检查"""
    repo = UserScenarioRoleRepository(db)
    perms = await repo.get_user_permission_codes(user_id)
    global_perms = perms["global_permissions"]
    scenario_perms = perms["scenario_permissions"]

    if permission:
        if permission in global_perms:
            return True
        if scenario_id in scenario_perms and permission in scenario_perms[scenario_id]:
            return True
        return False
    else:
        if "app_management" in global_perms:
            return True
        if scenario_id in scenario_perms:
            return True
        return False


async def check_scenario_access_or_403(
    user: User,
    scenario_id: str,
    db: AsyncSession,
    permission: str = None
) -> None:
    """
    检查用户是否有权访问场景，如果没有则抛出 403
    """
    # SYSTEM_ADMIN 有所有权限
    if user.role == "SYSTEM_ADMIN":
        return

    if await _check_v2_permission(user.id, scenario_id, db, permission):
        return

    raise HTTPException(
        status_code=403,
        detail=f"No access to scenario: {scenario_id}" if not permission
        else f"Missing permission: {permission} for scenario: {scenario_id}"
    )


async def get_user_scenario_ids_or_all(user: User, db: AsyncSession) -> list:
    """
    获取用户有权访问的场景ID列表
    """
    if user.role in ["SYSTEM_ADMIN", "AUDITOR"]:
        return None  # None 表示可以访问所有场景

    repo = UserScenarioRoleRepository(db)
    perms = await repo.get_user_permission_codes(user.id)
    if "app_management" in perms["global_permissions"] or "audit_logs" in perms["global_permissions"]:
        return None

    return list(perms["scenario_permissions"].keys())
