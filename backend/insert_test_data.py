#!/usr/bin/env python3
"""
插入100条测试数据到 staging_global_keywords 表
"""
import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.db_meta import StagingGlobalKeywords

# 测试数据：敏感词列表
test_keywords = [
    # 政治敏感词
    ("习近平", "POLITICAL", "High"),
    ("共产党", "POLITICAL", "High"),
    ("民主", "POLITICAL", "Medium"),
    ("自由", "POLITICAL", "Medium"),
    ("人权", "POLITICAL", "Medium"),
    ("六四", "POLITICAL", "High"),
    ("天安门", "POLITICAL", "High"),
    ("法轮功", "POLITICAL", "High"),
    ("达赖", "POLITICAL", "High"),
    ("台独", "POLITICAL", "High"),

    # 色情相关
    ("色情", "PORN", "High"),
    ("裸体", "PORN", "High"),
    ("性交", "PORN", "High"),
    ("成人电影", "PORN", "High"),
    ("黄色网站", "PORN", "High"),
    ("AV", "PORN", "Medium"),
    ("约炮", "PORN", "High"),
    ("一夜情", "PORN", "Medium"),
    ("援交", "PORN", "High"),
    ("卖淫", "PORN", "High"),

    # 广告相关
    ("加微信", "AD", "Medium"),
    ("免费领取", "AD", "Low"),
    ("点击链接", "AD", "Medium"),
    ("限时优惠", "AD", "Low"),
    ("扫码关注", "AD", "Low"),
    ("代理招募", "AD", "Medium"),
    ("兼职赚钱", "AD", "Medium"),
    ("日赚千元", "AD", "High"),
    ("投资理财", "AD", "Medium"),
    ("股票推荐", "AD", "Medium"),

    # 暴力相关
    ("杀人", "VIOLENCE", "High"),
    ("自杀", "VIOLENCE", "High"),
    ("爆炸", "VIOLENCE", "High"),
    ("恐怖袭击", "VIOLENCE", "High"),
    ("枪支", "VIOLENCE", "Medium"),
    ("炸弹", "VIOLENCE", "High"),
    ("毒品", "VIOLENCE", "High"),
    ("海洛因", "VIOLENCE", "High"),
    ("冰毒", "VIOLENCE", "High"),
    ("大麻", "VIOLENCE", "Medium"),

    # 其他敏感词
    ("赌博", "OTHER", "High"),
    ("博彩", "OTHER", "High"),
    ("洗钱", "OTHER", "High"),
    ("诈骗", "OTHER", "High"),
    ("传销", "OTHER", "High"),
    ("非法集资", "OTHER", "High"),
    ("高利贷", "OTHER", "High"),
    ("套路贷", "OTHER", "High"),
    ("黑客", "OTHER", "Medium"),
    ("病毒", "OTHER", "Medium"),
]

# 扩展到100条
extended_keywords = []
for i in range(100):
    if i < len(test_keywords):
        keyword, tag, risk = test_keywords[i]
    else:
        # 生成更多测试数据
        idx = i % len(test_keywords)
        keyword, tag, risk = test_keywords[idx]
        keyword = f"{keyword}_{i}"  # 添加后缀避免重复

    extended_keywords.append((keyword, tag, risk))

async def insert_test_data():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            # 清空现有的 PENDING 数据（可选）
            print("清空现有的 PENDING 数据...")
            from sqlalchemy import delete
            stmt = delete(StagingGlobalKeywords).where(StagingGlobalKeywords.status == "PENDING")
            await session.execute(stmt)

            # 插入100条新数据
            print("插入100条测试数据...")
            for keyword, tag, risk in extended_keywords:
                item = StagingGlobalKeywords(
                    id=str(uuid.uuid4()),
                    keyword=keyword,
                    predicted_tag=tag,
                    predicted_risk=risk,
                    final_tag=tag,
                    final_risk=risk,
                    status="PENDING",
                    is_modified=False
                )
                session.add(item)

            await session.commit()
            print(f"✅ 成功插入 {len(extended_keywords)} 条测试数据！")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(insert_test_data())
