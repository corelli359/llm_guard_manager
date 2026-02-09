"""角色和权限 Repository"""
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_meta import Role, Permission, RolePermission, UserScenarioRole


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, active_only: bool = True) -> List[Role]:
        query = select(Role)
        if active_only:
            query = query.where(Role.is_active == True)
        query = query.order_by(Role.role_type, Role.role_code)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, role_id: str) -> Optional[Role]:
        return await self.db.get(Role, role_id)

    async def get_by_code(self, role_code: str) -> Optional[Role]:
        query = select(Role).where(Role.role_code == role_code)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, role: Role) -> Role:
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def update(self, role: Role) -> Role:
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def delete_role(self, role_id: str) -> bool:
        role = await self.get_by_id(role_id)
        if not role or role.is_system:
            return False
        # 删除关联的权限配置
        await self.db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )
        # 删除关联的用户角色分配
        await self.db.execute(
            delete(UserScenarioRole).where(UserScenarioRole.role_id == role_id)
        )
        await self.db.delete(role)
        await self.db.commit()
        return True

    # ============================================
    # 角色-权限关联
    # ============================================

    async def get_role_permissions(self, role_id: str) -> List[Permission]:
        query = (
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == role_id)
            .order_by(Permission.sort_order)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_role_permission_count(self, role_id: str) -> int:
        query = select(RolePermission).where(RolePermission.role_id == role_id)
        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def update_role_permissions(self, role_id: str, permission_ids: List[str]):
        # 删除旧的
        await self.db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )
        # 插入新的
        import uuid
        for perm_id in permission_ids:
            rp = RolePermission(
                id=str(uuid.uuid4()),
                role_id=role_id,
                permission_id=perm_id
            )
            self.db.add(rp)
        await self.db.commit()


class PermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Permission]:
        query = select(Permission).where(Permission.is_active == True).order_by(Permission.sort_order)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_ids(self, ids: List[str]) -> List[Permission]:
        query = select(Permission).where(Permission.id.in_(ids))
        result = await self.db.execute(query)
        return list(result.scalars().all())


class UserScenarioRoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_roles(self, user_id: str) -> List[UserScenarioRole]:
        query = select(UserScenarioRole).where(UserScenarioRole.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def assign_role(self, assignment: UserScenarioRole) -> UserScenarioRole:
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def remove_role(self, assignment_id: str) -> bool:
        assignment = await self.db.get(UserScenarioRole, assignment_id)
        if not assignment:
            return False
        await self.db.delete(assignment)
        await self.db.commit()
        return True

    async def get_user_permission_codes(self, user_id: str) -> dict:
        """获取用户的所有权限编码，按全局/场景分组"""
        # 查询用户所有角色分配
        query = select(UserScenarioRole).where(UserScenarioRole.user_id == user_id)
        result = await self.db.execute(query)
        assignments = result.scalars().all()

        global_perms = set()
        scenario_perms = {}  # {scenario_id: set(perm_codes)}

        for assignment in assignments:
            # 获取角色的权限
            perm_query = (
                select(Permission.permission_code, Permission.scope)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .where(RolePermission.role_id == assignment.role_id)
                .where(Permission.is_active == True)
            )
            perm_result = await self.db.execute(perm_query)
            perms = perm_result.fetchall()

            for perm_code, perm_scope in perms:
                if assignment.scenario_id is None:
                    # 全局角色：全局权限直接加入，场景权限加入所有场景
                    global_perms.add(perm_code)
                else:
                    # 场景角色：只加入对应场景
                    if assignment.scenario_id not in scenario_perms:
                        scenario_perms[assignment.scenario_id] = set()
                    scenario_perms[assignment.scenario_id].add(perm_code)

        return {
            "global_permissions": list(global_perms),
            "scenario_permissions": {k: list(v) for k, v in scenario_perms.items()}
        }
