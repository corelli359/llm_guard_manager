from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import get_db
from app.api.v1.deps import get_current_user, get_current_user_full, require_role
from app.models.db_meta import User, UserScenarioRole, Role
from app.services.audit import AuditService
from app.repositories.role import RoleRepository, UserScenarioRoleRepository
from app.schemas.role import UserRoleAssign, UserRoleResponse, UserPermissionsResponse
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

router = APIRouter()


# ============================================
# V2 Schemas - 简化的用户模型
# ============================================

class UserListResponse(BaseModel):
    """用户列表响应"""
    id: str
    user_id: str | None = None  # USAP的UserID
    username: str | None = None
    display_name: str | None = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    """修改用户角色"""
    role: str = Field(..., description="用户角色: SYSTEM_ADMIN, SCENARIO_ADMIN, ANNOTATOR, AUDITOR")


class UserStatusUpdate(BaseModel):
    """修改用户状态"""
    is_active: bool


# ============================================
# V2 用户管理端点
# ============================================

@router.get("/", response_model=List[UserListResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
):
    """
    获取用户列表

    权限：仅 SYSTEM_ADMIN
    """
    stmt = select(User).order_by(User.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_in: UserRoleUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
):
    """
    修改用户角色

    权限：仅 SYSTEM_ADMIN
    """
    # 验证角色
    valid_roles = ["SYSTEM_ADMIN", "SCENARIO_ADMIN", "ANNOTATOR", "AUDITOR"]
    if role_in.role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 不能修改自己的角色
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    old_role = user.role
    user.role = role_in.role
    await db.commit()

    # 记录审计日志
    audit_service = AuditService(db)
    await audit_service.log_update(
        user_id=current_user.id,
        username=current_user.user_id or current_user.username,
        resource_type="USER",
        resource_id=user_id,
        details={"old_role": old_role, "new_role": role_in.role},
        request=request
    )

    return {"message": "Role updated", "role": role_in.role}


@router.patch("/{user_id}/status")
async def toggle_user_status(
    user_id: str,
    status_in: UserStatusUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
):
    """
    启用/禁用用户

    权限：仅 SYSTEM_ADMIN
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 不能禁用自己
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot disable yourself")

    user.is_active = status_in.is_active
    await db.commit()

    # 记录审计日志
    audit_service = AuditService(db)
    await audit_service.log_update(
        user_id=current_user.id,
        username=current_user.user_id or current_user.username,
        resource_type="USER",
        resource_id=user_id,
        details={"is_active": status_in.is_active},
        request=request
    )

    return {"message": "Status updated"}


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
):
    """
    删除用户

    权限：仅 SYSTEM_ADMIN
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 不能删除自己
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    await db.delete(user)
    await db.commit()

    # 记录审计日志
    audit_service = AuditService(db)
    await audit_service.log_delete(
        user_id=current_user.id,
        username=current_user.user_id or current_user.username,
        resource_type="USER",
        resource_id=user_id,
        details={"deleted_user_id": user.user_id},
        request=request
    )

    return {"message": "User deleted"}


# ============================================
# V2 用户角色分配端点
# ============================================

@router.get("/{user_id}/roles", response_model=List[UserRoleResponse])
async def get_user_roles(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """获取用户所有角色分配"""
    # 权限检查：管理员可查看所有，其他用户只能查看自己
    if current_user.role != "SYSTEM_ADMIN" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    repo = UserScenarioRoleRepository(db)
    assignments = await repo.get_user_roles(user_id)

    result = []
    for a in assignments:
        role = await db.get(Role, a.role_id)
        result.append(UserRoleResponse(
            id=a.id,
            user_id=a.user_id,
            scenario_id=a.scenario_id,
            role_id=a.role_id,
            role_code=role.role_code if role else "",
            role_name=role.role_name if role else "",
            role_type=role.role_type if role else "",
            created_at=a.created_at
        ))
    return result


@router.post("/{user_id}/roles", response_model=UserRoleResponse)
async def assign_role_to_user(
    user_id: str,
    role_assign: UserRoleAssign,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
) -> Any:
    """分配角色给用户"""
    # 验证用户存在
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 验证角色存在
    role = await db.get(Role, role_assign.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # 全局角色不需要 scenario_id，场景角色需要
    if role.role_type == "GLOBAL" and role_assign.scenario_id:
        raise HTTPException(status_code=400, detail="全局角色不需要指定场景")
    if role.role_type == "SCENARIO" and not role_assign.scenario_id:
        raise HTTPException(status_code=400, detail="场景角色需要指定场景")

    # 检查是否已分配
    repo = UserScenarioRoleRepository(db)
    existing = await repo.get_user_roles(user_id)
    for a in existing:
        if a.role_id == role_assign.role_id and a.scenario_id == role_assign.scenario_id:
            raise HTTPException(status_code=400, detail="该角色已分配")

    assignment = UserScenarioRole(
        id=str(uuid.uuid4()),
        user_id=user_id,
        scenario_id=role_assign.scenario_id,
        role_id=role_assign.role_id,
        created_by=current_user.id
    )
    repo = UserScenarioRoleRepository(db)
    assignment = await repo.assign_role(assignment)

    # 记录审计日志
    audit_service = AuditService(db)
    await audit_service.log_create(
        user_id=current_user.id,
        username=current_user.user_id or current_user.username,
        resource_type="USER_ROLE_ASSIGNMENT",
        resource_id=assignment.id,
        scenario_id=role_assign.scenario_id,
        details={"user_id": user_id, "role_code": role.role_code},
        request=request
    )

    return UserRoleResponse(
        id=assignment.id,
        user_id=assignment.user_id,
        scenario_id=assignment.scenario_id,
        role_id=assignment.role_id,
        role_code=role.role_code,
        role_name=role.role_name,
        role_type=role.role_type,
        created_at=assignment.created_at
    )


@router.delete("/{user_id}/roles/{assignment_id}")
async def remove_user_role(
    user_id: str,
    assignment_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
) -> Any:
    """移除用户角色分配"""
    repo = UserScenarioRoleRepository(db)
    success = await repo.remove_role(assignment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # 记录审计日志
    audit_service = AuditService(db)
    await audit_service.log_delete(
        user_id=current_user.id,
        username=current_user.user_id or current_user.username,
        resource_type="USER_ROLE_ASSIGNMENT",
        resource_id=assignment_id,
        details={"user_id": user_id},
        request=request
    )

    return {"message": "角色分配已移除"}


# ============================================
# 用户权限查询
# ============================================

@router.get("/me/permissions", response_model=UserPermissionsResponse)
async def get_my_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """获取当前用户权限"""
    repo = UserScenarioRoleRepository(db)
    perms = await repo.get_user_permission_codes(current_user.id)
    return UserPermissionsResponse(
        user_id=current_user.user_id or current_user.id,
        global_permissions=perms["global_permissions"],
        scenario_permissions=perms["scenario_permissions"]
    )
