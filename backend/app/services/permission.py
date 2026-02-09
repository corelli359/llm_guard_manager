"""
权限检查服务
负责所有权限相关的业务逻辑
"""

from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.db_meta import User, UserScenarioAssignment, ScenarioAdminPermission, Scenarios
from app.repositories.user_scenario_assignment import UserScenarioAssignmentRepository
from app.repositories.scenario_admin_permission import ScenarioAdminPermissionRepository


class PermissionService:
    """权限检查服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.assignment_repo = UserScenarioAssignmentRepository(UserScenarioAssignment, db)
        self.permission_repo = ScenarioAdminPermissionRepository(ScenarioAdminPermission, db)

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        根据ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            用户对象，如果不存在则返回 None
        """
        return await self.db.get(User, user_id)

    async def check_role(self, user_id: str, required_roles: List[str]) -> bool:
        """
        检查用户是否拥有指定角色之一

        Args:
            user_id: 用户ID
            required_roles: 需要的角色列表

        Returns:
            是否拥有权限
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        return user.role in required_roles

    async def check_scenario_access(self, user_id: str, scenario_id: str) -> bool:
        """
        检查用户是否有权访问指定场景

        Args:
            user_id: 用户ID
            scenario_id: 场景ID

        Returns:
            是否有权访问
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        # SYSTEM_ADMIN 有所有场景的访问权限
        if user.role == "SYSTEM_ADMIN":
            return True

        # AUDITOR 有所有场景的只读权限
        if user.role == "AUDITOR":
            return True

        # SCENARIO_ADMIN 和 ANNOTATOR 需要检查场景分配
        assignment = await self.assignment_repo.get_by_user_and_scenario(user_id, scenario_id)
        return assignment is not None

    async def check_scenario_permission(
        self, user_id: str, scenario_id: str, permission: str
    ) -> bool:
        """
        检查用户在指定场景是否有特定权限

        Args:
            user_id: 用户ID
            scenario_id: 场景ID
            permission: 权限名称（scenario_basic_info, scenario_keywords, etc.）

        Returns:
            是否有权限
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        # SYSTEM_ADMIN 有所有权限
        if user.role == "SYSTEM_ADMIN":
            return True

        # AUDITOR 只有只读权限，没有修改权限
        if user.role == "AUDITOR":
            return False

        # ANNOTATOR 没有场景配置权限
        if user.role == "ANNOTATOR":
            return False

        # SCENARIO_ADMIN 需要检查细粒度权限
        if user.role == "SCENARIO_ADMIN":
            # 首先检查是否有场景访问权限
            has_access = await self.check_scenario_access(user_id, scenario_id)
            if not has_access:
                return False

            # 检查细粒度权限
            return await self.permission_repo.check_permission(user_id, scenario_id, permission)

        return False

    async def get_user_permissions(self, user_id: str) -> Dict:
        """
        获取用户的完整权限信息

        Args:
            user_id: 用户ID

        Returns:
            权限信息字典，格式：
            {
                "role": "SCENARIO_ADMIN",
                "scenarios": [
                    {
                        "scenario_id": "app001",
                        "scenario_name": "客服场景",
                        "role": "SCENARIO_ADMIN",
                        "permissions": {
                            "scenario_basic_info": true,
                            "scenario_keywords": true,
                            "scenario_policies": false,
                            "playground": true,
                            "performance_test": false
                        }
                    }
                ]
            }
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return {"role": None, "scenarios": []}

        result = {
            "role": user.role,
            "scenarios": []
        }

        # SYSTEM_ADMIN 返回所有场景（带完整权限）
        if user.role == "SYSTEM_ADMIN":
            query = select(Scenarios).where(Scenarios.is_active == True)
            scenarios_result = await self.db.execute(query)
            scenarios = scenarios_result.scalars().all()

            for scenario in scenarios:
                result["scenarios"].append({
                    "scenario_id": scenario.app_id,
                    "scenario_name": scenario.app_name,
                    "role": "SYSTEM_ADMIN",
                    "permissions": {
                        "scenario_basic_info": True,
                        "scenario_keywords": True,
                        "scenario_policies": True,
                        "playground": True,
                        "performance_test": True
                    }
                })

        # SCENARIO_ADMIN 和 ANNOTATOR 返回分配的场景
        elif user.role in ["SCENARIO_ADMIN", "ANNOTATOR"]:
            assignments = await self.assignment_repo.get_user_scenarios(user_id)

            for assignment in assignments:
                # 获取场景信息
                scenario = await self.db.get(Scenarios, assignment.scenario_id)
                if not scenario:
                    continue

                scenario_info = {
                    "scenario_id": assignment.scenario_id,
                    "scenario_name": scenario.app_name if scenario else assignment.scenario_id,
                    "role": assignment.role,
                    "permissions": {}
                }

                # 如果是 SCENARIO_ADMIN，获取细粒度权限
                if assignment.role == "SCENARIO_ADMIN":
                    permission_config = await self.permission_repo.get_user_permission(
                        user_id, assignment.scenario_id
                    )

                    if permission_config:
                        scenario_info["permissions"] = {
                            "scenario_basic_info": permission_config.scenario_basic_info,
                            "scenario_keywords": permission_config.scenario_keywords,
                            "scenario_policies": permission_config.scenario_policies,
                            "playground": permission_config.playground,
                            "performance_test": permission_config.performance_test
                        }
                    else:
                        # 如果没有权限配置，使用默认值
                        scenario_info["permissions"] = {
                            "scenario_basic_info": True,
                            "scenario_keywords": True,
                            "scenario_policies": False,
                            "playground": True,
                            "performance_test": False
                        }
                else:
                    # ANNOTATOR 没有场景配置权限
                    scenario_info["permissions"] = {
                        "scenario_basic_info": False,
                        "scenario_keywords": False,
                        "scenario_policies": False,
                        "playground": False,
                        "performance_test": False
                    }

                result["scenarios"].append(scenario_info)

        # AUDITOR 返回所有场景（只读权限）
        elif user.role == "AUDITOR":
            query = select(Scenarios).where(Scenarios.is_active == True)
            scenarios_result = await self.db.execute(query)
            scenarios = scenarios_result.scalars().all()

            for scenario in scenarios:
                result["scenarios"].append({
                    "scenario_id": scenario.app_id,
                    "scenario_name": scenario.app_name,
                    "role": "AUDITOR",
                    "permissions": {
                        "scenario_basic_info": False,
                        "scenario_keywords": False,
                        "scenario_policies": False,
                        "playground": False,
                        "performance_test": False
                    }
                })

        return result

    async def get_user_scenario_ids(self, user_id: str) -> List[str]:
        """
        获取用户有权访问的所有场景ID列表

        Args:
            user_id: 用户ID

        Returns:
            场景ID列表
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return []

        # SYSTEM_ADMIN 和 AUDITOR 可以访问所有场景
        if user.role in ["SYSTEM_ADMIN", "AUDITOR"]:
            query = select(Scenarios.app_id).where(Scenarios.is_active == True)
            result = await self.db.execute(query)
            return list(result.scalars().all())

        # SCENARIO_ADMIN 和 ANNOTATOR 只能访问分配的场景
        return await self.assignment_repo.get_scenario_ids_by_user(user_id)
