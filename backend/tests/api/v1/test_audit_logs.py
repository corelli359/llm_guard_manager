"""
审计日志API测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.db_meta import User
from app.core.security import get_password_hash, create_access_token
from app.services.audit import AuditService
import uuid


@pytest.mark.asyncio
async def test_query_audit_logs_as_system_admin(client: AsyncClient, db_session: AsyncSession):
    """测试系统管理员查询审计日志"""
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

    # 创建一些审计日志
    audit_service = AuditService(db_session)
    for i in range(5):
        await audit_service.log_create(
            user_id=admin_id,
            username=admin.username,
            resource_type="KEYWORD",
            resource_id=f"keyword_{i}"
        )

    # 生成token
    token = create_access_token(data={"sub": admin.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 查询审计日志
    response = await client.get("/api/v1/audit-logs/")
    assert response.status_code == 200

    data = response.json()
    assert "items" in data or isinstance(data, list)


@pytest.mark.asyncio
async def test_query_audit_logs_as_auditor(client: AsyncClient, db_session: AsyncSession):
    """测试审计员查询审计日志"""
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

    # 创建一些审计日志
    audit_service = AuditService(db_session)
    for i in range(3):
        await audit_service.log_create(
            user_id=auditor_id,
            username=auditor.username,
            resource_type="POLICY",
            resource_id=f"policy_{i}"
        )

    # 生成token
    token = create_access_token(data={"sub": auditor.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 查询审计日志
    response = await client.get("/api/v1/audit-logs/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_query_audit_logs_as_annotator(client: AsyncClient, db_session: AsyncSession):
    """测试标注员查询审计日志（应该被拒绝）"""
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

    # 生成token
    token = create_access_token(data={"sub": annotator.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 尝试查询审计日志
    response = await client.get("/api/v1/audit-logs/")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_query_audit_logs_with_filters(client: AsyncClient, db_session: AsyncSession):
    """测试使用筛选条件查询审计日志"""
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

    # 创建不同类型的审计日志
    audit_service = AuditService(db_session)
    await audit_service.log_create(admin_id, admin.username, "KEYWORD", "k1")
    await audit_service.log_create(admin_id, admin.username, "KEYWORD", "k2")
    await audit_service.log_update(admin_id, admin.username, "POLICY", "p1")
    await audit_service.log_delete(admin_id, admin.username, "USER", "u1")

    # 生成token
    token = create_access_token(data={"sub": admin.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 按操作类型筛选
    response = await client.get("/api/v1/audit-logs/", params={"action": "CREATE"})
    assert response.status_code == 200

    # 按资源类型筛选
    response = await client.get("/api/v1/audit-logs/", params={"resource_type": "KEYWORD"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_query_audit_logs_with_pagination(client: AsyncClient, db_session: AsyncSession):
    """测试审计日志分页查询"""
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

    # 创建10条审计日志
    audit_service = AuditService(db_session)
    for i in range(10):
        await audit_service.log_create(
            admin_id, admin.username, "KEYWORD", f"k{i}"
        )

    # 生成token
    token = create_access_token(data={"sub": admin.username})
    client.headers["Authorization"] = f"Bearer {token}"

    # 第一页
    response = await client.get("/api/v1/audit-logs/", params={"skip": 0, "limit": 5})
    assert response.status_code == 200

    # 第二页
    response = await client.get("/api/v1/audit-logs/", params={"skip": 5, "limit": 5})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_query_audit_logs_without_token(client: AsyncClient):
    """测试未登录查询审计日志"""
    response = await client.get("/api/v1/audit-logs/")
    assert response.status_code == 401
