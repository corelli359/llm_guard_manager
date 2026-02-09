"""
用户管理服务
负责用户的 CRUD 和场景分配
"""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_meta import User, UserScenarioAssignment, ScenarioAdminPermission
from app.repositories.user_scenario_assignment import UserScenarioAssignmentRepository
from app.repositories.scenario_admin_permission import ScenarioAdminPermissionRepository
from app.core.security import get_password_hash


class UserManagementService:
    """用户管理服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.assignment_repo = UserScenarioAssignmentRepository(UserScenarioAssignment, db)
        self.permission_repo = ScenarioAdminPermissionRepository(ScenarioAdminPermission, db)

    async def assign_scenario(
        self,
        user_id: str,
        scenario_id: str,
        role: str,
        created_by: str
    ) -> UserScenarioAssignment:
        """
        分配场景给用户

        Args:
            user_id: 用户ID
            scenario_id: 场景ID
            role: 角色（SCENARIO_ADMIN, ANNOTATOR）
            created_by: 创建人ID

        Returns:
            场景分配对象

        Raises:
            ValueError: 如果已存在分配
        """
        # 检查是否已存在
        existing = await self.assignment_repo.get_by_user_and_scenario(user_id, scenario_id)
        if existing:
            raise ValueError(f"User already assigned to scenario {scenario_id}")

        # 创建分配
        assignment_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "scenario_id": scenario_id,
            "role": role,
            "created_by": created_by
        }

        return await self.assignment_repo.create(assignment_data)

    async def remove_scenario_assignment(
        self,
        user_id: str,
        scenario_id: str
    ) -> bool:
        """
        移除用户的场景分配

        Args:
            user_id: 用户ID
            scenario_id: 场景ID

        Returns:
            是否删除成功
        """
        # 删除场景分配
        assignment_deleted = await self.assignment_repo.delete_by_user_and_scenario(
            user_id, scenario_id
        )

        # 同时删除权限配置（如果存在）
        await self.permission_repo.delete_by_user_and_scenario(user_id, scenario_id)

        return assignment_deleted

    async def configure_permissions(
        self,
        user_id: str,
        scenario_id: str,
        permissions: dict,
        created_by: str
    ) -> ScenarioAdminPermission:
        """
        配置场景管理员权限

        Args:
            user_id: 用户ID
            scenario_id: 场景ID
            permissions: 权限配置字典
            created_by: 创建人ID

        Returns:
            权限配置对象

        Raises:
            ValueError: 如果用户不是场景管理员
        """
        # 检查用户是否是该场景的管理员
        assignment = await self.assignment_repo.get_by_user_and_scenario(user_id, scenario_id)
        if not assignment or assignment.role != "SCENARIO_ADMIN":
            raise ValueError(f"User is not a SCENARIO_ADMIN for scenario {scenario_id}")

        # 添加必要字段
        permissions["created_by"] = created_by
        if "id" not in permissions:
            permissions["id"] = str(uuid.uuid4())

        # 创建或更新权限
        return await self.permission_repo.create_or_update(user_id, scenario_id, permissions)

    async def get_user_scenarios(self, user_id: str) -> List[dict]:
        """
        获取用户的所有场景分配（包含权限信息）

        Args:
            user_id: 用户ID

        Returns:
            场景分配列表
        """
        assignments = await self.assignment_repo.get_user_scenarios(user_id)
        result = []

        for assignment in assignments:
            item = {
                "id": assignment.id,
                "scenario_id": assignment.scenario_id,
                "role": assignment.role,
                "created_at": assignment.created_at,
                "permissions": None
            }

            # 如果是场景管理员，获取权限配置
            if assignment.role == "SCENARIO_ADMIN":
                permission_config = await self.permission_repo.get_user_permission(
                    user_id, assignment.scenario_id
                )
                if permission_config:
                    item["permissions"] = {
                        "scenario_basic_info": permission_config.scenario_basic_info,
                        "scenario_keywords": permission_config.scenario_keywords,
                        "scenario_policies": permission_config.scenario_policies,
                        "playground": permission_config.playground,
                        "performance_test": permission_config.performance_test
                    }

            result.append(item)

        return result
