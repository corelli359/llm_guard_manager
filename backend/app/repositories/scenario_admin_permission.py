"""
场景管理员权限配置 Repository
负责场景管理员的细粒度权限配置数据访问
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_meta import ScenarioAdminPermission
from app.repositories.base import BaseRepository


class ScenarioAdminPermissionRepository(BaseRepository[ScenarioAdminPermission]):
    """场景管理员权限配置 Repository"""

    async def get_user_permission(
        self, user_id: str, scenario_id: str
    ) -> Optional[ScenarioAdminPermission]:
        """
        获取用户在特定场景的权限配置

        Args:
            user_id: 用户ID
            scenario_id: 场景ID

        Returns:
            权限配置，如果不存在则返回 None
        """
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.scenario_id == scenario_id
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_user_all_permissions(
        self, user_id: str
    ) -> List[ScenarioAdminPermission]:
        """
        获取用户在所有场景的权限配置

        Args:
            user_id: 用户ID

        Returns:
            权限配置列表
        """
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_scenario_permissions(
        self, scenario_id: str
    ) -> List[ScenarioAdminPermission]:
        """
        获取场景的所有用户权限配置

        Args:
            scenario_id: 场景ID

        Returns:
            权限配置列表
        """
        query = select(self.model).where(self.model.scenario_id == scenario_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_or_update(
        self, user_id: str, scenario_id: str, permissions: dict
    ) -> ScenarioAdminPermission:
        """
        创建或更新权限配置

        Args:
            user_id: 用户ID
            scenario_id: 场景ID
            permissions: 权限配置字典

        Returns:
            权限配置对象
        """
        existing = await self.get_user_permission(user_id, scenario_id)

        if existing:
            # 更新现有权限
            return await self.update(existing, permissions)
        else:
            # 创建新权限
            permissions['user_id'] = user_id
            permissions['scenario_id'] = scenario_id
            return await self.create(permissions)

    async def delete_by_user_and_scenario(
        self, user_id: str, scenario_id: str
    ) -> bool:
        """
        删除特定用户在特定场景的权限配置

        Args:
            user_id: 用户ID
            scenario_id: 场景ID

        Returns:
            是否删除成功
        """
        permission = await self.get_user_permission(user_id, scenario_id)
        if permission:
            await self.db.delete(permission)
            await self.db.commit()
            return True
        return False

    async def check_permission(
        self, user_id: str, scenario_id: str, permission_name: str
    ) -> bool:
        """
        检查用户在特定场景是否有特定权限

        Args:
            user_id: 用户ID
            scenario_id: 场景ID
            permission_name: 权限名称（scenario_basic_info, scenario_keywords, etc.）

        Returns:
            是否有权限
        """
        permission_config = await self.get_user_permission(user_id, scenario_id)

        if not permission_config:
            return False

        # 获取权限字段的值
        return getattr(permission_config, permission_name, False)
