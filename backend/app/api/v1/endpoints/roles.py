"""角色管理 API"""
import uuid
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.api.v1.deps import get_current_user_full
from app.models.db_meta import Role, User
from app.repositories.role import RoleRepository, PermissionRepository
from app.schemas.role import (
    RoleCreate, RoleUpdate, RoleResponse, RoleDetailResponse,
    PermissionResponse, RolePermissionUpdate
)

router = APIRouter()


def _check_admin(user: User):
    """检查是否有管理权限（暂用 role 字段兼容）"""
    if user.role != "SYSTEM_ADMIN":
        raise HTTPException(status_code=403, detail="需要系统管理员权限")


# ============================================
# 角色管理
# ============================================

@router.get("/", response_model=List[RoleResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """获取角色列表"""
    repo = RoleRepository(db)
    roles = await repo.get_all(active_only=False)

    result = []
    for role in roles:
        count = await repo.get_role_permission_count(role.id)
        result.append(RoleResponse(
            id=role.id,
            role_code=role.role_code,
            role_name=role.role_name,
            role_type=role.role_type,
            description=role.description,
            is_system=role.is_system,
            is_active=role.is_active,
            created_at=role.created_at,
            permission_count=count
        ))
    return result


@router.post("/", response_model=RoleResponse)
async def create_role(
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """创建角色"""
    _check_admin(current_user)

    repo = RoleRepository(db)
    existing = await repo.get_by_code(role_in.role_code)
    if existing:
        raise HTTPException(status_code=400, detail="角色编码已存在")

    role = Role(
        id=str(uuid.uuid4()),
        role_code=role_in.role_code,
        role_name=role_in.role_name,
        role_type=role_in.role_type,
        description=role_in.description,
        is_system=False,
        is_active=True
    )
    role = await repo.create(role)
    return RoleResponse(
        id=role.id,
        role_code=role.role_code,
        role_name=role.role_name,
        role_type=role.role_type,
        description=role.description,
        is_system=role.is_system,
        is_active=role.is_active,
        created_at=role.created_at,
        permission_count=0
    )


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """更新角色"""
    _check_admin(current_user)

    repo = RoleRepository(db)
    role = await repo.get_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    if role_in.role_name is not None:
        role.role_name = role_in.role_name
    if role_in.role_type is not None:
        role.role_type = role_in.role_type
    if role_in.description is not None:
        role.description = role_in.description
    if role_in.is_active is not None:
        role.is_active = role_in.is_active

    role = await repo.update(role)
    count = await repo.get_role_permission_count(role.id)
    return RoleResponse(
        id=role.id,
        role_code=role.role_code,
        role_name=role.role_name,
        role_type=role.role_type,
        description=role.description,
        is_system=role.is_system,
        is_active=role.is_active,
        created_at=role.created_at,
        permission_count=count
    )


@router.delete("/{role_id}")
async def delete_role(
    role_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """删除角色（系统角色不可删）"""
    _check_admin(current_user)

    repo = RoleRepository(db)
    role = await repo.get_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if role.is_system:
        raise HTTPException(status_code=400, detail="系统预置角色不可删除")

    await repo.delete_role(role_id)
    return {"message": "角色已删除"}


# ============================================
# 角色权限配置
# ============================================

@router.get("/{role_id}/permissions", response_model=List[PermissionResponse])
async def get_role_permissions(
    role_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """获取角色权限"""
    repo = RoleRepository(db)
    role = await repo.get_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    permissions = await repo.get_role_permissions(role_id)
    return permissions


@router.put("/{role_id}/permissions")
async def update_role_permissions(
    role_id: str,
    perm_in: RolePermissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """更新角色权限"""
    _check_admin(current_user)

    repo = RoleRepository(db)
    role = await repo.get_by_id(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    # 验证权限ID是否存在
    perm_repo = PermissionRepository(db)
    valid_perms = await perm_repo.get_by_ids(perm_in.permission_ids)
    valid_ids = {p.id for p in valid_perms}
    invalid_ids = set(perm_in.permission_ids) - valid_ids
    if invalid_ids:
        raise HTTPException(status_code=400, detail=f"无效的权限ID: {invalid_ids}")

    await repo.update_role_permissions(role_id, perm_in.permission_ids)
    return {"message": "权限已更新", "count": len(perm_in.permission_ids)}


# ============================================
# 权限列表
# ============================================

@router.get("/permissions/all", response_model=List[PermissionResponse])
async def list_all_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """获取所有权限列表"""
    repo = PermissionRepository(db)
    return await repo.get_all()
