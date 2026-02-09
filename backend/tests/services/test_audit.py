"""
审计日志服务测试
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.audit import AuditService
from app.repositories.audit_log import AuditLogRepository
from app.models.db_meta import User, AuditLog
from app.core.security import get_password_hash
import uuid


@pytest.mark.asyncio
async def test_log_create_action(db_session: AsyncSession):
    """测试记录CREATE操作"""
    # 创建测试用户
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        username=f"test_user_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SYSTEM_ADMIN",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    audit_service = AuditService(db_session)

    # 记录CREATE操作
    log = await audit_service.log_create(
        user_id=user_id,
        username=user.username,
        resource_type="KEYWORD",
        resource_id="keyword_001",
        scenario_id="scenario_001",
        details={"keyword": "test_keyword", "tag_code": "TAG001"}
    )

    assert log.id is not None
    assert log.action == "CREATE"
    assert log.resource_type == "KEYWORD"
    assert log.resource_id == "keyword_001"
    assert log.scenario_id == "scenario_001"
    assert log.details["keyword"] == "test_keyword"


@pytest.mark.asyncio
async def test_log_update_action(db_session: AsyncSession):
    """测试记录UPDATE操作"""
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        username=f"test_user_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SYSTEM_ADMIN",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    audit_service = AuditService(db_session)

    log = await audit_service.log_update(
        user_id=user_id,
        username=user.username,
        resource_type="POLICY",
        resource_id="policy_001",
        details={"old_strategy": "BLOCK", "new_strategy": "REWRITE"}
    )

    assert log.action == "UPDATE"
    assert log.resource_type == "POLICY"


@pytest.mark.asyncio
async def test_log_delete_action(db_session: AsyncSession):
    """测试记录DELETE操作"""
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        username=f"test_user_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SYSTEM_ADMIN",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    audit_service = AuditService(db_session)

    log = await audit_service.log_delete(
        user_id=user_id,
        username=user.username,
        resource_type="USER",
        resource_id="user_001",
        details={"username": "deleted_user"}
    )

    assert log.action == "DELETE"
    assert log.resource_type == "USER"


@pytest.mark.asyncio
async def test_search_logs_by_user(db_session: AsyncSession):
    """测试按用户查询审计日志"""
    # 创建两个用户
    user1_id = str(uuid.uuid4())
    user1 = User(
        id=user1_id,
        username=f"test_user1_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SYSTEM_ADMIN",
        is_active=True
    )
    user2_id = str(uuid.uuid4())
    user2 = User(
        id=user2_id,
        username=f"test_user2_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SCENARIO_ADMIN",
        is_active=True
    )
    db_session.add_all([user1, user2])
    await db_session.commit()

    audit_service = AuditService(db_session)

    # 用户1创建3条日志
    for i in range(3):
        await audit_service.log_create(
            user_id=user1_id,
            username=user1.username,
            resource_type="KEYWORD",
            resource_id=f"keyword_{i}"
        )

    # 用户2创建2条日志
    for i in range(2):
        await audit_service.log_create(
            user_id=user2_id,
            username=user2.username,
            resource_type="POLICY",
            resource_id=f"policy_{i}"
        )

    # 查询用户1的日志
    audit_repo = AuditLogRepository(AuditLog, db_session)
    user1_logs = await audit_repo.search_logs(user_id=user1_id)
    assert len(user1_logs) == 3

    # 查询用户2的日志
    user2_logs = await audit_repo.search_logs(user_id=user2_id)
    assert len(user2_logs) == 2


@pytest.mark.asyncio
async def test_search_logs_by_action(db_session: AsyncSession):
    """测试按操作类型查询审计日志"""
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        username=f"test_user_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SYSTEM_ADMIN",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    audit_service = AuditService(db_session)

    # 创建不同类型的操作
    await audit_service.log_create(user_id, user.username, "KEYWORD", "k1")
    await audit_service.log_create(user_id, user.username, "KEYWORD", "k2")
    await audit_service.log_update(user_id, user.username, "POLICY", "p1")
    await audit_service.log_delete(user_id, user.username, "USER", "u1")

    # 查询CREATE操作
    audit_repo = AuditLogRepository(AuditLog, db_session)
    create_logs = await audit_repo.search_logs(action="CREATE")
    assert len(create_logs) == 2

    # 查询UPDATE操作
    update_logs = await audit_repo.search_logs(action="UPDATE")
    assert len(update_logs) == 1

    # 查询DELETE操作
    delete_logs = await audit_repo.search_logs(action="DELETE")
    assert len(delete_logs) == 1


@pytest.mark.asyncio
async def test_search_logs_by_resource_type(db_session: AsyncSession):
    """测试按资源类型查询审计日志"""
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        username=f"test_user_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SYSTEM_ADMIN",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    audit_service = AuditService(db_session)

    # 创建不同资源类型的日志
    await audit_service.log_create(user_id, user.username, "KEYWORD", "k1")
    await audit_service.log_create(user_id, user.username, "KEYWORD", "k2")
    await audit_service.log_create(user_id, user.username, "POLICY", "p1")
    await audit_service.log_create(user_id, user.username, "META_TAG", "t1")

    # 查询KEYWORD类型
    audit_repo = AuditLogRepository(AuditLog, db_session)
    keyword_logs = await audit_repo.search_logs(resource_type="KEYWORD")
    assert len(keyword_logs) == 2

    # 查询POLICY类型
    policy_logs = await audit_repo.search_logs(resource_type="POLICY")
    assert len(policy_logs) == 1


@pytest.mark.asyncio
async def test_search_logs_by_scenario(db_session: AsyncSession):
    """测试按场景查询审计日志"""
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        username=f"test_user_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SYSTEM_ADMIN",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    audit_service = AuditService(db_session)

    # 创建不同场景的日志
    await audit_service.log_create(user_id, user.username, "KEYWORD", "k1", scenario_id="scenario_001")
    await audit_service.log_create(user_id, user.username, "KEYWORD", "k2", scenario_id="scenario_001")
    await audit_service.log_create(user_id, user.username, "KEYWORD", "k3", scenario_id="scenario_002")

    # 查询scenario_001的日志
    audit_repo = AuditLogRepository(AuditLog, db_session)
    scenario1_logs = await audit_repo.search_logs(scenario_id="scenario_001")
    assert len(scenario1_logs) == 2

    # 查询scenario_002的日志
    scenario2_logs = await audit_repo.search_logs(scenario_id="scenario_002")
    assert len(scenario2_logs) == 1


@pytest.mark.asyncio
async def test_search_logs_with_pagination(db_session: AsyncSession):
    """测试审计日志分页查询"""
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        username=f"test_user_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SYSTEM_ADMIN",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    audit_service = AuditService(db_session)

    # 创建10条日志
    for i in range(10):
        await audit_service.log_create(
            user_id, user.username, "KEYWORD", f"k{i}"
        )

    audit_repo = AuditLogRepository(AuditLog, db_session)

    # 第一页：前5条
    page1 = await audit_repo.search_logs(skip=0, limit=5)
    assert len(page1) == 5

    # 第二页：后5条
    page2 = await audit_repo.search_logs(skip=5, limit=5)
    assert len(page2) == 5

    # 验证不重复
    page1_ids = {log.id for log in page1}
    page2_ids = {log.id for log in page2}
    assert len(page1_ids & page2_ids) == 0


@pytest.mark.asyncio
async def test_log_with_ip_and_user_agent(db_session: AsyncSession):
    """测试记录IP地址和User Agent"""
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        username=f"test_user_{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("test123"),
        role="SYSTEM_ADMIN",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    audit_service = AuditService(db_session)

    log = await audit_service.log_create(
        user_id=user_id,
        username=user.username,
        resource_type="KEYWORD",
        resource_id="k1",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )

    assert log.ip_address == "192.168.1.100"
    assert "Mozilla" in log.user_agent
