#!/usr/bin/env python3
"""
数据库迁移脚本：添加认领相关字段
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def migrate():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        # 添加字段到 staging_global_keywords
        await conn.execute(text("""
            ALTER TABLE staging_global_keywords
            ADD COLUMN claimed_by VARCHAR(64) NULL AFTER is_modified,
            ADD COLUMN claimed_at DATETIME NULL AFTER claimed_by,
            ADD COLUMN batch_id CHAR(36) NULL AFTER claimed_at
        """))

        # 添加索引
        try:
            await conn.execute(text("CREATE INDEX idx_claimed_by ON staging_global_keywords(claimed_by)"))
        except Exception as e:
            print(f"Index idx_claimed_by: {e}")

        try:
            await conn.execute(text("CREATE INDEX idx_batch_id ON staging_global_keywords(batch_id)"))
        except Exception as e:
            print(f"Index idx_batch_id: {e}")

        try:
            await conn.execute(text("CREATE INDEX idx_annotator ON staging_global_keywords(annotator)"))
        except Exception as e:
            print(f"Index idx_annotator: {e}")

        # 添加字段到 staging_global_rules
        await conn.execute(text("""
            ALTER TABLE staging_global_rules
            ADD COLUMN claimed_by VARCHAR(64) NULL AFTER is_modified,
            ADD COLUMN claimed_at DATETIME NULL AFTER claimed_by,
            ADD COLUMN batch_id CHAR(36) NULL AFTER claimed_at
        """))

        # 添加索引
        try:
            await conn.execute(text("CREATE INDEX idx_claimed_by_rules ON staging_global_rules(claimed_by)"))
        except Exception as e:
            print(f"Index idx_claimed_by_rules: {e}")

        try:
            await conn.execute(text("CREATE INDEX idx_batch_id_rules ON staging_global_rules(batch_id)"))
        except Exception as e:
            print(f"Index idx_batch_id_rules: {e}")

        try:
            await conn.execute(text("CREATE INDEX idx_annotator_rules ON staging_global_rules(annotator)"))
        except Exception as e:
            print(f"Index idx_annotator_rules: {e}")

    await engine.dispose()
    print("Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(migrate())
