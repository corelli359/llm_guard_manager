import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.main import app
from app.core.db import get_db
from app.core.config import settings

# Redefine the db dependency override for tests

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # Create engine inside the fixture to ensure it uses the current test's event loop
    engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    
    async with TestingSessionLocal() as session:
        yield session
    
    # Dispose engine to close connections attached to this loop
    await engine.dispose()

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    # Override the get_db dependency
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    
    app.dependency_overrides.clear()