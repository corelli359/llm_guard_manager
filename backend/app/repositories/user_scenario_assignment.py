"""
用户场景关联 Repository
负责用户与场景的关联关系数据访问
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_meta import UserScenarioAssignment
from app.repositories.base import BaseRepository


class UserScenarioAssignmentRepository(BaseRepository[UserScenarioAssignment]):
    """用户场景关联 Repository"""

    async def get_user_scenarios(self, user_id: str) -> List[UserScenarioAssignment]:
        """
        获取用户的所有场景分配

        Args:
            user_id: 用户ID

        Returns:
            用户的场景分配列表
        """
        query = select(self.model).where(self.model.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_scenario_users(self, scenario_id: str) -> List[UserScenarioAssignment]:
        """
        获取场景的所有用户分配

        Args:
            scenario_id: 场景ID

        Returns:
            场景的用户分配列表
        """
        query = select(self.model).where(self.model.scenario_id == scenario_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_user_and_scenario(
        self, user_id: str, scenario_id: str
    ) -> Optional[UserScenarioAssignment]:
        """
        获取特定用户在特定场景的分配记录

        Args:
            user_id: 用户ID
            scenario_id: 场景ID

        Returns:
            分配记录，如果不存在则返回 None
        """
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.scenario_id == scenario_id
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_user_scenarios_by_role(
        self, user_id: str, role: str
    ) -> List[UserScenarioAssignment]:
        """
        获取用户在特定角色下的场景分配

        Args:
            user_id: 用户ID
            role: 角色（SCENARIO_ADMIN, ANNOTATOR）

        Returns:
            场景分配列表
        """
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.role == role
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete_by_user_and_scenario(
        self, user_id: str, scenario_id: str
    ) -> bool:
        """
        删除特定用户在特定场景的分配

        Args:
            user_id: 用户ID
            scenario_id: 场景ID

        Returns:
            是否删除成功
        """
        assignment = await self.get_by_user_and_scenario(user_id, scenario_id)
        if assignment:
            await self.db.delete(assignment)
            await self.db.commit()
            return True
        return False

    async def get_scenario_ids_by_user(self, user_id: str) -> List[str]:
        """
        获取用户有权访问的所有场景ID列表

        Args:
            user_id: 用户ID

        Returns:
            场景ID列表
        """
        query = select(self.model.scenario_id).where(self.model.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
