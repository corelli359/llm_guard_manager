import asyncio
from app.core.db import engine
from app.models.db_meta import Base

# Import all models to ensure they are registered with SQLAlchemy's metadata
from app.models.db_meta import (
    Scenarios, 
    GlobalKeywords, 
    MetaTags, 
    ScenarioKeywords, 
    RuleScenarioPolicy, 
    RuleGlobalDefaults
)

async def init_database():
    """
    Creates all database tables defined in the models.
    This function is idempotent - it will not recreate existing tables.
    """
    print("Initializing database schema...")
    async with engine.begin() as conn:
        # The create_all function checks for the existence of tables before creating.
        await conn.run_sync(Base.metadata.create_all)
    print("Database schema initialization complete.")
    await engine.dispose()

if __name__ == "__main__":
    print("Running DB initialization script...")
    asyncio.run(init_database())
    print("Script finished.")
