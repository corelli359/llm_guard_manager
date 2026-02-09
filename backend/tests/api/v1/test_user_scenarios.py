"""
用户场景分配API测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_meta import User
from app.core.security import get_password_hash, create_access_token
import uuid


@pytest.mark.asyncio
async def test_assign_scenario_as_system_admin(client: AsyncClient, db_session: AsyncSession):
    """测试系统管理员分配场景"""
    # 创建系统管理员
    admin_id = str(uuid.uuid4())
    admin = User(
        id=admin_id,
        username=f"test_admin_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SYSTEM_ADMIN",
        is_active=True
    )

    # 创建场景管理员
    scenario_admin_id = str(uuid.uuid4())
    scenario_admin = User(
        id=scenario_admin_id,
        username=f"test_scenario_admin_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SCENARIO_ADMIN",
        is_active=True
    )

    db_session.add_all([admin, scenario_admin])
    await db_session.commit()

    # 生成token
    token = create_access_token(data={"sub": admin.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 分配场景
    response = await client.post(
        f"/api/v1/users/{scenario_admin_id}/scenarios",
        json={
            "scenario_id": "test_scenario_001",
            "role": "SCENARIO_ADMIN"
        }
    )
    assert response.status_code == 200

    data = response.json()
    assert data["scenario_id"] == "test_scenario_001"
    assert data["role"] == "SCENARIO_ADMIN"


@pytest.mark.asyncio
async def test_assign_scenario_as_non_admin(client: AsyncClient, db_session: AsyncSession):
    """测试非管理员分配场景（应该被拒绝）"""
    # 创建标注员
    annotator_id = str(uuid.uuid4())
    annotator = User(
        id=annotator_id,
        username=f"test_annotator_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="ANNOTATOR",
        is_active=True
    )

    # 创建另一个用户
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        username=f"test_user_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="ANNOTATOR",
        is_active=True
    )

    db_session.add_all([annotator, user])
    await db_session.commit()

    # 生成token
    token = create_access_token(data={"sub": annotator.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 尝试分配场景
    response = await client.post(
        f"/api/v1/users/{user_id}/scenarios",
        json={
            "scenario_id": "test_scenario_002",
            "role": "ANNOTATOR"
        }
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_configure_permissions_as_system_admin(client: AsyncClient, db_session: AsyncSession):
    """测试系统管理员配置权限"""
    # 创建系统管理员
    admin_id = str(uuid.uuid4())
    admin = User(
        id=admin_id,
        username=f"test_admin_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SYSTEM_ADMIN",
        is_active=True
    )

    # 创建场景管理员
    scenario_admin_id = str(uuid.uuid4())
    scenario_admin = User(
        id=scenario_admin_id,
        username=f"test_scenario_admin_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SCENARIO_ADMIN",
        is_active=True
    )

    db_session.add_all([admin, scenario_admin])
    await db_session.commit()

    # 生成token
    token = create_access_token(data={"sub": admin.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 先分配场景
    await client.post(
        f"/api/v1/users/{scenario_admin_id}/scenarios",
        json={
            "scenario_id": "test_scenario_003",
            "role": "SCENARIO_ADMIN"
        }
    )

    # 配置权限
    response = await client.put(
        f"/api/v1/users/{scenario_admin_id}/scenarios/test_scenario_003/permissions",
        json={
            "scenario_basic_info": True,
            "scenario_keywords": True,
            "scenario_policies": False,
            "playground": True,
            "performance_test": False
        }
    )
    assert response.status_code == 200

    data = response.json()
    assert data["scenario_keywords"] is True
    assert data["scenario_policies"] is False


@pytest.mark.asyncio
async def test_get_user_scenarios(client: AsyncClient, db_session: AsyncSession):
    """测试获取用户场景列表"""
    # 创建系统管理员
    admin_id = str(uuid.uuid4())
    admin = User(
        id=admin_id,
        username=f"test_admin_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SYSTEM_ADMIN",
        is_active=True
    )

    # 创建场景管理员
    scenario_admin_id = str(uuid.uuid4())
    scenario_admin = User(
        id=scenario_admin_id,
        username=f"test_scenario_admin_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SCENARIO_ADMIN",
        is_active=True
    )

    db_session.add_all([admin, scenario_admin])
    await db_session.commit()

    # 生成token
    token = create_access_token(data={"sub": admin.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 分配多个场景
    await client.post(
        f"/api/v1/users/{scenario_admin_id}/scenarios",
        json={"scenario_id": "test_scenario_004", "role": "SCENARIO_ADMIN"}
    )
    await client.post(
        f"/api/v1/users/{scenario_admin_id}/scenarios",
        json={"scenario_id": "test_scenario_005", "role": "SCENARIO_ADMIN"}
    )

    # 获取用户场景列表
    response = await client.get(f"/api/v1/users/{scenario_admin_id}/scenarios")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_remove_scenario_assignment(client: AsyncClient, db_session: AsyncSession):
    """测试移除场景分配"""
    # 创建系统管理员
    admin_id = str(uuid.uuid4())
    admin = User(
        id=admin_id,
        username=f"test_admin_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SYSTEM_ADMIN",
        is_active=True
    )

    # 创建场景管理员
    scenario_admin_id = str(uuid.uuid4())
    scenario_admin = User(
        id=scenario_admin_id,
        username=f"test_scenario_admin_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SCENARIO_ADMIN",
        is_active=True
    )

    db_session.add_all([admin, scenario_admin])
    await db_session.commit()

    # 生成token
    token = create_access_token(data={"sub": admin.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 分配场景
    await client.post(
        f"/api/v1/users/{scenario_admin_id}/scenarios",
        json={"scenario_id": "test_scenario_006", "role": "SCENARIO_ADMIN"}
    )

    # 移除场景分配
    response = await client.delete(
        f"/api/v1/users/{scenario_admin_id}/scenarios/test_scenario_006"
    )
    assert response.status_code == 200

    # 验证已移除
    response = await client.get(f"/api/v1/users/{scenario_admin_id}/scenarios")
    data = response.json()
    assert len(data) == 0


@pytest.mark.asyncio
async def test_assign_duplicate_scenario(client: AsyncClient, db_session: AsyncSession):
    """测试重复分配场景（应该失败）"""
    # 创建系统管理员
    admin_id = str(uuid.uuid4())
    admin = User(
        id=admin_id,
        username=f"test_admin_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SYSTEM_ADMIN",
        is_active=True
    )

    # 创建场景管理员
    scenario_admin_id = str(uuid.uuid4())
    scenario_admin = User(
        id=scenario_admin_id,
        username=f"test_scenario_admin_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SCENARIO_ADMIN",
        is_active=True
    )

    db_session.add_all([admin, scenario_admin])
    await db_session.commit()

    # 生成token
    token = create_access_token(data={"sub": admin.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 第一次分配
    response = await client.post(
        f"/api/v1/users/{scenario_admin_id}/scenarios",
        json={"scenario_id": "test_scenario_007", "role": "SCENARIO_ADMIN"}
    )
    assert response.status_code == 200

    # 第二次分配（应该失败）
    response = await client.post(
        f"/api/v1/users/{scenario_admin_id}/scenarios",
        json={"scenario_id": "test_scenario_007", "role": "SCENARIO_ADMIN"}
    )
    assert response.status_code == 400
