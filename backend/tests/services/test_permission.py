"""
权限服务测试
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.permission import PermissionService
from app.services.user_management import UserManagementService
from app.models.db_meta import User
from app.core.security import get_password_hash
import uuid


@pytest.mark.asyncio
async def test_system_admin_has_all_permissions(db_session: AsyncSession):
    """测试系统管理员拥有所有权限"""
    # 创建系统管理员
    admin_id = str(uuid.uuid4())
    admin = User(
        id=admin_id,
        username=f"test_admin_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SYSTEM_ADMIN",
        is_active=True
    )
    db_session.add(admin)
    await db_session.commit()

    perm_service = PermissionService(db_session)

    # 系统管理员应该有所有角色权限
    assert await perm_service.check_role(admin_id, ["SYSTEM_ADMIN"])
    assert await perm_service.check_role(admin_id, ["SYSTEM_ADMIN", "SCENARIO_ADMIN"])

    # 系统管理员应该可以访问任何场景
    assert await perm_service.check_scenario_access(admin_id, "any_scenario")

    # 系统管理员应该有任何场景的所有权限
    assert await perm_service.check_scenario_permission(admin_id, "any_scenario", "scenario_keywords")
    assert await perm_service.check_scenario_permission(admin_id, "any_scenario", "scenario_policies")


@pytest.mark.asyncio
async def test_scenario_admin_has_assigned_scenarios(db_session: AsyncSession):
    """测试场景管理员只能访问分配的场景"""
    # 创建场景管理员
    admin_id = str(uuid.uuid4())
    scenario_admin = User(
        id=admin_id,
        username=f"test_scenario_admin_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SCENARIO_ADMIN",
        is_active=True
    )
    db_session.add(scenario_admin)
    await db_session.commit()

    # 分配场景
    user_mgmt_service = UserManagementService(db_session)
    test_scenario_id = "test_scenario_001"
    await user_mgmt_service.assign_scenario(
        user_id=admin_id,
        scenario_id=test_scenario_id,
        role="SCENARIO_ADMIN",
        created_by=admin_id
    )

    perm_service = PermissionService(db_session)

    # 应该可以访问分配的场景
    assert await perm_service.check_scenario_access(admin_id, test_scenario_id)

    # 不应该能访问未分配的场景
    assert not await perm_service.check_scenario_access(admin_id, "other_scenario")


@pytest.mark.asyncio
async def test_scenario_admin_permissions(db_session: AsyncSession):
    """测试场景管理员的细粒度权限检查"""
    # 创建场景管理员
    admin_id = str(uuid.uuid4())
    scenario_admin = User(
        id=admin_id,
        username=f"test_scenario_admin_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SCENARIO_ADMIN",
        is_active=True
    )
    db_session.add(scenario_admin)
    await db_session.commit()

    # 分配场景并配置权限
    user_mgmt_service = UserManagementService(db_session)
    test_scenario_id = "test_scenario_002"
    await user_mgmt_service.assign_scenario(
        user_id=admin_id,
        scenario_id=test_scenario_id,
        role="SCENARIO_ADMIN",
        created_by=admin_id
    )

    # 配置部分权限
    permissions = {
        "scenario_basic_info": True,
        "scenario_keywords": True,
        "scenario_policies": False,  # 没有策略权限
        "playground": True,
        "performance_test": False  # 没有性能测试权限
    }
    await user_mgmt_service.configure_permissions(
        user_id=admin_id,
        scenario_id=test_scenario_id,
        permissions=permissions,
        created_by=admin_id
    )

    perm_service = PermissionService(db_session)

    # 应该有的权限
    assert await perm_service.check_scenario_permission(admin_id, test_scenario_id, "scenario_keywords")
    assert await perm_service.check_scenario_permission(admin_id, test_scenario_id, "playground")

    # 不应该有的权限
    assert not await perm_service.check_scenario_permission(admin_id, test_scenario_id, "scenario_policies")
    assert not await perm_service.check_scenario_permission(admin_id, test_scenario_id, "performance_test")


@pytest.mark.asyncio
async def test_annotator_can_only_see_assigned_scenarios(db_session: AsyncSession):
    """测试标注员只能看到分配的场景"""
    # 创建标注员
    annotator_id = str(uuid.uuid4())
    annotator = User(
        id=annotator_id,
        username=f"test_annotator_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="ANNOTATOR",
        is_active=True
    )
    db_session.add(annotator)
    await db_session.commit()

    # 分配场景
    user_mgmt_service = UserManagementService(db_session)
    test_scenario_id = "test_scenario_003"
    await user_mgmt_service.assign_scenario(
        user_id=annotator_id,
        scenario_id=test_scenario_id,
        role="ANNOTATOR",
        created_by=annotator_id
    )

    perm_service = PermissionService(db_session)

    # 应该可以访问分配的场景
    assert await perm_service.check_scenario_access(annotator_id, test_scenario_id)

    # 不应该能访问未分配的场景
    assert not await perm_service.check_scenario_access(annotator_id, "other_scenario")

    # 标注员不应该有管理权限
    assert not await perm_service.check_scenario_permission(annotator_id, test_scenario_id, "scenario_policies")


@pytest.mark.asyncio
async def test_auditor_read_only(db_session: AsyncSession):
    """测试审计员只有只读权限"""
    # 创建审计员
    auditor_id = str(uuid.uuid4())
    auditor = User(
        id=auditor_id,
        username=f"test_auditor_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="AUDITOR",
        is_active=True
    )
    db_session.add(auditor)
    await db_session.commit()

    perm_service = PermissionService(db_session)

    # 审计员应该有AUDITOR角色
    assert await perm_service.check_role(auditor_id, ["AUDITOR"])

    # 审计员不应该有管理权限
    assert not await perm_service.check_role(auditor_id, ["SYSTEM_ADMIN"])
    assert not await perm_service.check_role(auditor_id, ["SCENARIO_ADMIN"])


@pytest.mark.asyncio
async def test_get_user_permissions(db_session: AsyncSession):
    """测试获取用户完整权限信息"""
    # 创建场景管理员
    admin_id = str(uuid.uuid4())
    scenario_admin = User(
        id=admin_id,
        username=f"test_scenario_admin_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SCENARIO_ADMIN",
        display_name="测试场景管理员",
        is_active=True
    )
    db_session.add(scenario_admin)
    await db_session.commit()

    # 分配多个场景
    user_mgmt_service = UserManagementService(db_session)
    scenario_1 = "test_scenario_004"
    scenario_2 = "test_scenario_005"

    await user_mgmt_service.assign_scenario(
        user_id=admin_id,
        scenario_id=scenario_1,
        role="SCENARIO_ADMIN",
        created_by=admin_id
    )
    await user_mgmt_service.assign_scenario(
        user_id=admin_id,
        scenario_id=scenario_2,
        role="SCENARIO_ADMIN",
        created_by=admin_id
    )

    # 配置权限
    await user_mgmt_service.configure_permissions(
        user_id=admin_id,
        scenario_id=scenario_1,
        permissions={
            "scenario_basic_info": True,
            "scenario_keywords": True,
            "scenario_policies": True,
            "playground": True,
            "performance_test": True
        },
        created_by=admin_id
    )

    perm_service = PermissionService(db_session)
    permissions = await perm_service.get_user_permissions(admin_id)

    # 验证权限信息
    assert permissions["user_id"] == admin_id
    assert permissions["username"] == scenario_admin.username
    assert permissions["role"] == "SCENARIO_ADMIN"
    assert len(permissions["scenarios"]) == 2

    # 验证场景信息
    scenario_ids = [s["scenario_id"] for s in permissions["scenarios"]]
    assert scenario_1 in scenario_ids
    assert scenario_2 in scenario_ids


@pytest.mark.asyncio
async def test_permission_update_immediately_effective(db_session: AsyncSession):
    """测试权限修改后立即生效"""
    # 创建场景管理员
    admin_id = str(uuid.uuid4())
    scenario_admin = User(
        id=admin_id,
        username=f"test_scenario_admin_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SCENARIO_ADMIN",
        is_active=True
    )
    db_session.add(scenario_admin)
    await db_session.commit()

    # 分配场景
    user_mgmt_service = UserManagementService(db_session)
    test_scenario_id = "test_scenario_006"
    await user_mgmt_service.assign_scenario(
        user_id=admin_id,
        scenario_id=test_scenario_id,
        role="SCENARIO_ADMIN",
        created_by=admin_id
    )

    # 初始权限：没有策略权限
    await user_mgmt_service.configure_permissions(
        user_id=admin_id,
        scenario_id=test_scenario_id,
        permissions={
            "scenario_basic_info": True,
            "scenario_keywords": True,
            "scenario_policies": False,
            "playground": True,
            "performance_test": False
        },
        created_by=admin_id
    )

    perm_service = PermissionService(db_session)

    # 验证初始权限
    assert not await perm_service.check_scenario_permission(admin_id, test_scenario_id, "scenario_policies")

    # 修改权限：添加策略权限
    await user_mgmt_service.configure_permissions(
        user_id=admin_id,
        scenario_id=test_scenario_id,
        permissions={
            "scenario_basic_info": True,
            "scenario_keywords": True,
            "scenario_policies": True,  # 现在有权限了
            "playground": True,
            "performance_test": False
        },
        created_by=admin_id
    )

    # 验证权限立即生效
    assert await perm_service.check_scenario_permission(admin_id, test_scenario_id, "scenario_policies")
