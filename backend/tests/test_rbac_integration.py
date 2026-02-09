"""
RBAC 系统集成测试脚本
测试所有 RBAC 功能
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.db_meta import User, UserScenarioAssignment, ScenarioAdminPermission, AuditLog
from app.services.permission import PermissionService
from app.services.audit import AuditService
from app.services.user_management import UserManagementService
from app.core.security import get_password_hash
import uuid


async def test_rbac_system():
    """测试 RBAC 系统"""
    print("=" * 60)
    print("RBAC 系统集成测试")
    print("=" * 60)

    # 创建数据库引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            # ============================================
            # 测试 1: 创建测试用户
            # ============================================
            print("\n[测试 1] 创建测试用户...")

            # 创建系统管理员
            admin_id = str(uuid.uuid4())
            admin = User(
                id=admin_id,
                username=f"test_admin_{uuid.uuid4().hex[:8]}",
                hashed_password=get_password_hash("test123"),
                role="SYSTEM_ADMIN",
                display_name="测试管理员",
                is_active=True
            )
            db.add(admin)

            # 创建场景管理员
            scenario_admin_id = str(uuid.uuid4())
            scenario_admin = User(
                id=scenario_admin_id,
                username=f"test_scenario_admin_{uuid.uuid4().hex[:8]}",
                hashed_password=get_password_hash("test123"),
                role="SCENARIO_ADMIN",
                display_name="测试场景管理员",
                is_active=True
            )
            db.add(scenario_admin)

            # 创建标注员
            annotator_id = str(uuid.uuid4())
            annotator = User(
                id=annotator_id,
                username=f"test_annotator_{uuid.uuid4().hex[:8]}",
                hashed_password=get_password_hash("test123"),
                role="ANNOTATOR",
                display_name="测试标注员",
                is_active=True
            )
            db.add(annotator)

            await db.commit()
            print(f"✅ 创建了 3 个测试用户")
            print(f"   - SYSTEM_ADMIN: {admin.username}")
            print(f"   - SCENARIO_ADMIN: {scenario_admin.username}")
            print(f"   - ANNOTATOR: {annotator.username}")

            # ============================================
            # 测试 2: 权限服务测试
            # ============================================
            print("\n[测试 2] 权限服务测试...")

            perm_service = PermissionService(db)

            # 测试角色检查
            is_admin = await perm_service.check_role(admin_id, ["SYSTEM_ADMIN"])
            assert is_admin, "SYSTEM_ADMIN 角色检查失败"
            print("✅ 角色检查正常")

            # 测试获取用户权限
            admin_perms = await perm_service.get_user_permissions(admin_id)
            assert admin_perms["role"] == "SYSTEM_ADMIN", "权限信息错误"
            print(f"✅ 获取用户权限正常，角色: {admin_perms['role']}")

            # ============================================
            # 测试 3: 场景分配测试
            # ============================================
            print("\n[测试 3] 场景分配测试...")

            user_mgmt_service = UserManagementService(db)

            # 分配场景给场景管理员
            test_scenario_id = "test_scenario_001"
            assignment = await user_mgmt_service.assign_scenario(
                user_id=scenario_admin_id,
                scenario_id=test_scenario_id,
                role="SCENARIO_ADMIN",
                created_by=admin_id
            )
            print(f"✅ 场景分配成功: {assignment.scenario_id}")

            # 配置权限
            permissions = {
                "scenario_basic_info": True,
                "scenario_keywords": True,
                "scenario_policies": False,
                "playground": True,
                "performance_test": False
            }
            perm_config = await user_mgmt_service.configure_permissions(
                user_id=scenario_admin_id,
                scenario_id=test_scenario_id,
                permissions=permissions,
                created_by=admin_id
            )
            print(f"✅ 权限配置成功")

            # 验证权限
            has_keyword_perm = await perm_service.check_scenario_permission(
                scenario_admin_id, test_scenario_id, "scenario_keywords"
            )
            assert has_keyword_perm, "场景权限检查失败"
            print("✅ 场景权限检查正常")

            has_policy_perm = await perm_service.check_scenario_permission(
                scenario_admin_id, test_scenario_id, "scenario_policies"
            )
            assert not has_policy_perm, "场景权限检查失败（应该没有权限）"
            print("✅ 权限拒绝检查正常")

            # ============================================
            # 测试 4: 审计日志测试
            # ============================================
            print("\n[测试 4] 审计日志测试...")

            audit_service = AuditService(db)

            # 记录审计日志
            log = await audit_service.log_create(
                user_id=admin_id,
                username=admin.username,
                resource_type="TEST",
                resource_id="test_resource_001",
                scenario_id=test_scenario_id,
                details={"action": "test_action"}
            )
            print(f"✅ 审计日志记录成功: {log.id}")

            # 查询审计日志
            from app.repositories.audit_log import AuditLogRepository
            audit_repo = AuditLogRepository(AuditLog, db)
            logs = await audit_repo.search_logs(
                user_id=admin_id,
                limit=10
            )
            assert len(logs) > 0, "审计日志查询失败"
            print(f"✅ 审计日志查询成功，找到 {len(logs)} 条记录")

            # ============================================
            # 测试 5: 清理测试数据
            # ============================================
            print("\n[测试 5] 清理测试数据...")

            # 删除测试用户（级联删除关联数据）
            await db.delete(admin)
            await db.delete(scenario_admin)
            await db.delete(annotator)
            await db.commit()
            print("✅ 测试数据清理完成")

            # ============================================
            # 测试总结
            # ============================================
            print("\n" + "=" * 60)
            print("✅ 所有测试通过！")
            print("=" * 60)
            print("\n测试覆盖:")
            print("  ✅ 用户创建和角色分配")
            print("  ✅ 权限服务（角色检查、权限查询）")
            print("  ✅ 场景分配和权限配置")
            print("  ✅ 细粒度权限检查")
            print("  ✅ 审计日志记录和查询")
            print("  ✅ 数据清理（级联删除）")

            return True

        except Exception as e:
            print(f"\n❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            await engine.dispose()


if __name__ == "__main__":
    success = asyncio.run(test_rbac_system())
    sys.exit(0 if success else 1)
