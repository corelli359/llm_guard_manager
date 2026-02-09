"""
权限检查辅助函数
用于在 API 端点中简化权限检查逻辑
同时支持 V1（user_scenario_assignments）和 V2（user_scenario_roles）
"""

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_meta import User
from app.services.permission import PermissionService
from app.repositories.role import UserScenarioRoleRepository


async def _check_v2_permission(user_id: str, scenario_id: str, db: AsyncSession, permission: str = None) -> bool:
    """V2 RBAC 权限检查"""
    repo = UserScenarioRoleRepository(db)
    perms = await repo.get_user_permission_codes(user_id)
    global_perms = perms["global_permissions"]
    scenario_perms = perms["scenario_permissions"]

    if permission:
        # 全局权限包含 -> 放行
        if permission in global_perms:
            return True
        # 场景权限包含 -> 放行
        if scenario_id in scenario_perms and permission in scenario_perms[scenario_id]:
            return True
        return False
    else:
        # 只检查场景访问权
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
    同时检查 V1 和 V2，任一通过即放行
    """
    # SYSTEM_ADMIN 有所有权限
    if user.role == "SYSTEM_ADMIN":
        return

    # --- V2 检查 ---
    if await _check_v2_permission(user.id, scenario_id, db, permission):
        return

    # --- V1 检查（保持原有逻辑不变）---
    perm_service = PermissionService(db)

    has_access = await perm_service.check_scenario_access(user.id, scenario_id)
    if has_access:
        if not permission:
            return
        has_perm = await perm_service.check_scenario_permission(user.id, scenario_id, permission)
        if has_perm:
            return

    raise HTTPException(
        status_code=403,
        detail=f"No access to scenario: {scenario_id}" if not permission
        else f"Missing permission: {permission} for scenario: {scenario_id}"
    )


async def get_user_scenario_ids_or_all(user: User, db: AsyncSession) -> list:
    """
    获取用户有权访问的场景ID列表
    合并 V1 和 V2 的结果
    """
    if user.role in ["SYSTEM_ADMIN", "AUDITOR"]:
        return None  # None 表示可以访问所有场景

    # V2 检查：全局权限包含 app_management 或 audit_logs -> 所有场景
    repo = UserScenarioRoleRepository(db)
    perms = await repo.get_user_permission_codes(user.id)
    if "app_management" in perms["global_permissions"] or "audit_logs" in perms["global_permissions"]:
        return None

    # 合并 V1 + V2 的场景列表
    v2_ids = set(perms["scenario_permissions"].keys())

    perm_service = PermissionService(db)
    v1_ids = set(await perm_service.get_user_scenario_ids(user.id))

    return list(v1_ids | v2_ids)
