"""
权限API测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_meta import User
from app.core.security import get_password_hash, create_access_token
from app.services.user_management import UserManagementService
import uuid


@pytest.mark.asyncio
async def test_get_my_permissions_system_admin(client: AsyncClient, db_session: AsyncSession):
    """测试系统管理员获取自己的权限"""
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
    db_session.add(admin)
    await db_session.commit()

    # 生成token
    token = create_access_token(data={"sub": admin.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 获取权限
    response = await client.get("/api/v1/permissions/me")
    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == admin_id
    assert data["username"] == admin.username
    assert data["role"] == "SYSTEM_ADMIN"
    assert isinstance(data["scenarios"], list)


@pytest.mark.asyncio
async def test_get_my_permissions_scenario_admin(client: AsyncClient, db_session: AsyncSession):
    """测试场景管理员获取自己的权限"""
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

    # 分配场景
    user_mgmt_service = UserManagementService(db_session)
    test_scenario_id = "test_scenario_001"
    await user_mgmt_service.assign_scenario(
        user_id=admin_id,
        scenario_id=test_scenario_id,
        role="SCENARIO_ADMIN",
        created_by=admin_id
    )

    # 配置权限
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

    # 生成token
    token = create_access_token(data={"sub": scenario_admin.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 获取权限
    response = await client.get("/api/v1/permissions/me")
    assert response.status_code == 200

    data = response.json()
    assert data["role"] == "SCENARIO_ADMIN"
    assert len(data["scenarios"]) == 1
    assert data["scenarios"][0]["scenario_id"] == test_scenario_id
    assert data["scenarios"][0]["permissions"]["scenario_keywords"] is True
    assert data["scenarios"][0]["permissions"]["scenario_policies"] is False


@pytest.mark.asyncio
async def test_check_permission_with_permission(client: AsyncClient, db_session: AsyncSession):
    """测试检查权限（有权限）"""
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
    await user_mgmt_service.configure_permissions(
        user_id=admin_id,
        scenario_id=test_scenario_id,
        permissions={
            "scenario_basic_info": True,
            "scenario_keywords": True,
            "scenario_policies": True,
            "playground": True,
            "performance_test": True
        },
        created_by=admin_id
    )

    # 生成token
    token = create_access_token(data={"sub": scenario_admin.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 检查权限
    response = await client.get(
        "/api/v1/permissions/check",
        params={"scenario_id": test_scenario_id, "permission": "scenario_keywords"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_permission"] is True


@pytest.mark.asyncio
async def test_check_permission_without_permission(client: AsyncClient, db_session: AsyncSession):
    """测试检查权限（无权限）"""
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

    # 分配场景但不配置策略权限
    user_mgmt_service = UserManagementService(db_session)
    test_scenario_id = "test_scenario_003"
    await user_mgmt_service.assign_scenario(
        user_id=admin_id,
        scenario_id=test_scenario_id,
        role="SCENARIO_ADMIN",
        created_by=admin_id
    )
    await user_mgmt_service.configure_permissions(
        user_id=admin_id,
        scenario_id=test_scenario_id,
        permissions={
            "scenario_basic_info": True,
            "scenario_keywords": True,
            "scenario_policies": False,  # 没有策略权限
            "playground": True,
            "performance_test": False
        },
        created_by=admin_id
    )

    # 生成token
    token = create_access_token(data={"sub": scenario_admin.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 检查权限
    response = await client.get(
        "/api/v1/permissions/check",
        params={"scenario_id": test_scenario_id, "permission": "scenario_policies"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_permission"] is False


@pytest.mark.asyncio
async def test_get_permissions_without_token(client: AsyncClient):
    """测试未登录获取权限"""
    response = await client.get("/api/v1/permissions/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_check_permission_for_unassigned_scenario(client: AsyncClient, db_session: AsyncSession):
    """测试检查未分配场景的权限"""
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

    # 生成token
    token = create_access_token(data={"sub": scenario_admin.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 检查未分配场景的权限
    response = await client.get(
        "/api/v1/permissions/check",
        params={"scenario_id": "unassigned_scenario", "permission": "scenario_keywords"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_permission"] is False
