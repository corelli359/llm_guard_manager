import sys
import os
import asyncio
import uuid
from sqlalchemy import select

sys.path.append(os.getcwd())

from app.core.db import AsyncSessionLocal
from app.models.db_meta import Scenarios, MetaTags, RuleScenarioPolicy

async def seed():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Scenarios))
        if res.scalars().first():
            print("Data exists.")
            return

        print("Seeding data...")
        app_id = "test_app_001"
        s = Scenarios(
            id=str(uuid.uuid4()),
            app_id=app_id,
            app_name="Test App (Recovered)",
            description="Generated to restore UI functionality.",
            is_active=True,
            enable_whitelist=True,
            enable_blacklist=True,
            enable_custom_policy=True
        )
        db.add(s)
        
        t = MetaTags(id=str(uuid.uuid4()), tag_code="TEST", tag_name="Test Tag", level=1)
        db.add(t)

        await db.commit()
        print(f"Created App: {app_id}")

if __name__ == "__main__":
    asyncio.run(seed())