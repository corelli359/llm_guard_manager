"""
创建系统管理员用户
"""
import asyncio
import sys
import uuid

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# 添加app到路径
sys.path.insert(0, '/app')

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.db_meta import User


async def create_admin_user():
    """创建系统管理员用户"""
    print("=" * 60)
    print("创建系统管理员用户")
    print("=" * 60)

    # 创建数据库引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        try:
            # 检查用户是否已存在
            query = select(User).where(User.username == "llm_guard")
            result = await db.execute(query)
            existing_user = result.scalars().first()

            if existing_user:
                print(f"\n✅ 用户 'llm_guard' 已存在")
                print(f"   - ID: {existing_user.id}")
                print(f"   - 角色: {existing_user.role}")
                print(f"   - 状态: {'激活' if existing_user.is_active else '禁用'}")

                # 更新为SYSTEM_ADMIN角色（如果不是）
                if existing_user.role != "SYSTEM_ADMIN":
                    existing_user.role = "SYSTEM_ADMIN"
                    await db.commit()
                    print(f"\n✅ 已更新角色为 SYSTEM_ADMIN")
            else:
                # 创建新用户
                admin_user = User(
                    id=str(uuid.uuid4()),
                    username="llm_guard",
                    hashed_password=get_password_hash("68-8CtBhug"),
                    role="SYSTEM_ADMIN",
                    display_name="系统管理员",
                    email="admin@example.com",
                    is_active=True
                )

                db.add(admin_user)
                await db.commit()

                print(f"\n✅ 成功创建用户 'llm_guard'")
                print(f"   - ID: {admin_user.id}")
                print(f"   - 用户名: {admin_user.username}")
                print(f"   - 角色: {admin_user.role}")
                print(f"   - 密码: 68-8CtBhug")

            print("\n" + "=" * 60)
            print("完成！")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin_user())
