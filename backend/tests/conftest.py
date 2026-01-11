import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.main import app
from app.core.db import get_db
from app.core.config import settings
from app.models.db_meta import Base  # Import Base

# Hardcoded test credentials
TEST_USERNAME = "llm_guard"
TEST_PASSWORD = "68-8CtBhug"

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # Use in-memory SQLite for tests to avoid dropping production tables
    test_db_url = "sqlite+aiosqlite:///:memory:"
    from sqlalchemy.pool import StaticPool
    
    engine = create_async_engine(
        test_db_url, 
        poolclass=StaticPool, # Needed for in-memory SQLite with async
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with TestingSessionLocal() as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    
    app.dependency_overrides.clear()

@pytest.fixture
async def authenticated_client(client: AsyncClient) -> AsyncClient:
    login_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
    }
    response = await client.post("/api/v1/login/access-token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client