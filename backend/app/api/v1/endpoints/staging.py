from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_
from app.core.db import get_db
from app.api.v1.deps import get_current_user
from app.models.db_meta import StagingGlobalKeywords, GlobalKeywords, StagingGlobalRules, RuleGlobalDefaults
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid
import pytz

# 中国时区
CHINA_TZ = pytz.timezone('Asia/Shanghai')

def get_china_now():
    """获取中国时区的当前时间"""
    return datetime.now(CHINA_TZ)

router = APIRouter()

# --- Schemas ---
class StagingKeywordResponse(BaseModel):
    id: str
    keyword: str
    predicted_tag: str
    predicted_risk: str
    final_tag: Optional[str]
    final_risk: Optional[str]
    status: str
    is_modified: bool
    claimed_by: Optional[str]
    claimed_at: Optional[datetime]
    batch_id: Optional[str]
    annotator: Optional[str]
    annotated_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class StagingRuleResponse(BaseModel):
    id: str
    tag_code: str
    extra_condition: Optional[str]
    predicted_strategy: str
    final_strategy: Optional[str]
    status: str
    is_modified: bool
    claimed_by: Optional[str]
    claimed_at: Optional[datetime]
    batch_id: Optional[str]
    annotator: Optional[str]
    annotated_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class StagingReviewRequest(BaseModel):
    final_tag: Optional[str] = None
    final_risk: Optional[str] = None
    status: str # REVIEWED or IGNORED

class StagingRuleReviewRequest(BaseModel):
    final_strategy: str
    status: str

class SyncRequest(BaseModel):
    ids: List[str]

# --- Endpoints: Keywords ---

@router.get("/keywords", response_model=List[StagingKeywordResponse])
async def list_staging_keywords(
    status: Optional[str] = None,
    my_tasks: bool = Query(False, description="只显示我认领的任务"),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    stmt = select(StagingGlobalKeywords)
    if status:
        stmt = stmt.where(StagingGlobalKeywords.status == status)
    if my_tasks:
        # 只显示当前用户认领的任务（CLAIMED状态）
        stmt = stmt.where(
            and_(
                StagingGlobalKeywords.claimed_by == current_user,
                StagingGlobalKeywords.status == "CLAIMED"
            )
        )
    stmt = stmt.order_by(StagingGlobalKeywords.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.patch("/keywords/{keyword_id}", response_model=StagingKeywordResponse)
async def review_keyword(
    keyword_id: str,
    review_data: StagingReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    stmt = select(StagingGlobalKeywords).where(StagingGlobalKeywords.id == keyword_id)
    result = await db.execute(stmt)
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    if review_data.final_tag:
        item.final_tag = review_data.final_tag
    if review_data.final_risk:
        item.final_risk = review_data.final_risk
        
    item.status = review_data.status
    item.annotator = current_user
    item.annotated_at = get_china_now()

    # Check modification
    if item.final_tag != item.predicted_tag or item.final_risk != item.predicted_risk:
        item.is_modified = True
    else:
        item.is_modified = False
    
    await db.commit()
    await db.refresh(item)
    return item

@router.post("/keywords/sync")
async def sync_keywords(
    sync_req: SyncRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    if current_user != "llm_guard":
        raise HTTPException(status_code=403, detail="Only admin can sync")
        
    stmt = select(StagingGlobalKeywords).where(StagingGlobalKeywords.id.in_(sync_req.ids))
    result = await db.execute(stmt)
    items = result.scalars().all()
    
    synced_count = 0
    for item in items:
        if item.status != "REVIEWED":
            continue
            
        g_stmt = select(GlobalKeywords).where(GlobalKeywords.keyword == item.keyword)
        g_res = await db.execute(g_stmt)
        existing = g_res.scalars().first()
        
        if existing:
            existing.tag_code = item.final_tag
            existing.risk_level = item.final_risk
        else:
            new_kw = GlobalKeywords(
                id=str(uuid.uuid4()),
                keyword=item.keyword,
                tag_code=item.final_tag,
                risk_level=item.final_risk,
                is_active=True
            )
            db.add(new_kw)
            
        item.status = "SYNCED"
        synced_count += 1
        
    await db.commit()
    return {"synced_count": synced_count}

@router.post("/keywords/import-mock")
async def import_mock_keywords(db: AsyncSession = Depends(get_db)):
    data = [
        ("bad_word_1", "POLITICAL", "High"),
        ("bad_word_2", "PORN", "High"),
        ("maybe_bad", "AD", "Low"),
    ]
    for k, t, r in data:
        obj = StagingGlobalKeywords(
            id=str(uuid.uuid4()),
            keyword=k,
            predicted_tag=t,
            predicted_risk=r,
            final_tag=t,
            final_risk=r,
            status="PENDING"
        )
        db.add(obj)
    await db.commit()
    return {"message": "Mock keywords imported"}

@router.delete("/keywords/{keyword_id}")
async def delete_staging_keyword(
    keyword_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    # Optional: Check if user is admin or annotator
    stmt = select(StagingGlobalKeywords).where(StagingGlobalKeywords.id == keyword_id)
    result = await db.execute(stmt)
    item = result.scalars().first()
    if item:
        await db.delete(item)
        await db.commit()
    return {"message": "Deleted"}

# --- Endpoints: Rules ---

@router.get("/rules", response_model=List[StagingRuleResponse])
async def list_staging_rules(
    status: Optional[str] = None,
    my_tasks: bool = Query(False, description="只显示我认领的任务"),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    stmt = select(StagingGlobalRules)
    if status:
        stmt = stmt.where(StagingGlobalRules.status == status)
    if my_tasks:
        # 只显示当前用户认领的任务（CLAIMED状态）
        stmt = stmt.where(
            and_(
                StagingGlobalRules.claimed_by == current_user,
                StagingGlobalRules.status == "CLAIMED"
            )
        )
    stmt = stmt.order_by(StagingGlobalRules.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.patch("/rules/{rule_id}", response_model=StagingRuleResponse)
async def review_rule(
    rule_id: str,
    review_data: StagingRuleReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    stmt = select(StagingGlobalRules).where(StagingGlobalRules.id == rule_id)
    result = await db.execute(stmt)
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    item.final_strategy = review_data.final_strategy
    item.status = review_data.status
    item.annotator = current_user
    item.annotated_at = get_china_now()

    if item.final_strategy != item.predicted_strategy:
        item.is_modified = True
    else:
        item.is_modified = False
        
    await db.commit()
    await db.refresh(item)
    return item

@router.post("/rules/sync")
async def sync_rules(
    sync_req: SyncRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    if current_user != "llm_guard":
        raise HTTPException(status_code=403, detail="Only admin can sync")
        
    stmt = select(StagingGlobalRules).where(StagingGlobalRules.id.in_(sync_req.ids))
    result = await db.execute(stmt)
    items = result.scalars().all()
    
    synced_count = 0
    for item in items:
        if item.status != "REVIEWED":
            continue
            
        g_stmt = select(RuleGlobalDefaults).where(
            RuleGlobalDefaults.tag_code == item.tag_code,
            RuleGlobalDefaults.extra_condition == item.extra_condition
        )
        g_res = await db.execute(g_stmt)
        existing = g_res.scalars().first()
        
        if existing:
            existing.strategy = item.final_strategy
        else:
            new_rule = RuleGlobalDefaults(
                id=str(uuid.uuid4()),
                tag_code=item.tag_code,
                extra_condition=item.extra_condition,
                strategy=item.final_strategy,
                is_active=True
            )
            db.add(new_rule)
            
        item.status = "SYNCED"
        synced_count += 1
        
    await db.commit()
    return {"synced_count": synced_count}

@router.post("/rules/import-mock")
async def import_mock_rules(db: AsyncSession = Depends(get_db)):
    data = [
        ("POLITICAL", None, "BLOCK"),
        ("AD", "HighRisk", "BLOCK"),
        ("PORN", None, "BLOCK"),
    ]
    for t, e, s in data:
        obj = StagingGlobalRules(
            id=str(uuid.uuid4()),
            tag_code=t,
            extra_condition=e,
            predicted_strategy=s,
            final_strategy=s,
            status="PENDING"
        )
        db.add(obj)
    await db.commit()
    return {"message": "Mock rules imported"}

@router.delete("/rules/{rule_id}")
async def delete_staging_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    stmt = select(StagingGlobalRules).where(StagingGlobalRules.id == rule_id)
    result = await db.execute(stmt)
    item = result.scalars().first()
    if item:
        await db.delete(item)
        await db.commit()
    return {"message": "Deleted"}


# --- Batch Claim Endpoints ---

class ClaimRequest(BaseModel):
    batch_size: int = 50  # 默认一次认领50条
    task_type: str = "keywords"  # keywords or rules

class ClaimResponse(BaseModel):
    claimed_count: int
    batch_id: str
    expires_at: datetime
    timeout_minutes: int

@router.post("/claim", response_model=ClaimResponse)
async def claim_batch(
    claim_req: ClaimRequest,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """批量认领任务"""
    batch_id = str(uuid.uuid4())
    timeout_minutes = 30  # 30分钟超时
    expires_at = get_china_now() + timedelta(minutes=timeout_minutes)

    if claim_req.task_type == "keywords":
        # 查询可认领的任务（PENDING状态）
        stmt = select(StagingGlobalKeywords).where(
            StagingGlobalKeywords.status == "PENDING"
        ).limit(claim_req.batch_size)
        result = await db.execute(stmt)
        items = result.scalars().all()

        # 更新为CLAIMED状态
        for item in items:
            item.status = "CLAIMED"
            item.claimed_by = current_user
            item.claimed_at = get_china_now()
            item.batch_id = batch_id
    else:
        # 规则认领
        stmt = select(StagingGlobalRules).where(
            StagingGlobalRules.status == "PENDING"
        ).limit(claim_req.batch_size)
        result = await db.execute(stmt)
        items = result.scalars().all()

        for item in items:
            item.status = "CLAIMED"
            item.claimed_by = current_user
            item.claimed_at = get_china_now()
            item.batch_id = batch_id

    await db.commit()

    return ClaimResponse(
        claimed_count=len(items),
        batch_id=batch_id,
        expires_at=expires_at,
        timeout_minutes=timeout_minutes
    )


@router.post("/release-expired")
async def release_expired_claims(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """释放超时的认领任务（管理员或系统定时任务调用）"""
    timeout_threshold = get_china_now() - timedelta(minutes=30)

    # 释放超时的关键词任务
    stmt_kw = update(StagingGlobalKeywords).where(
        and_(
            StagingGlobalKeywords.status == "CLAIMED",
            StagingGlobalKeywords.claimed_at < timeout_threshold
        )
    ).values(
        status="PENDING",
        claimed_by=None,
        claimed_at=None,
        batch_id=None
    )
    result_kw = await db.execute(stmt_kw)

    # 释放超时的规则任务
    stmt_rule = update(StagingGlobalRules).where(
        and_(
            StagingGlobalRules.status == "CLAIMED",
            StagingGlobalRules.claimed_at < timeout_threshold
        )
    ).values(
        status="PENDING",
        claimed_by=None,
        claimed_at=None,
        batch_id=None
    )
    result_rule = await db.execute(stmt_rule)

    await db.commit()

    return {
        "released_keywords": result_kw.rowcount,
        "released_rules": result_rule.rowcount
    }


class AnnotatorStats(BaseModel):
    annotator: str
    reviewed_count: int
    ignored_count: int
    total_count: int

@router.get("/stats/annotators", response_model=List[AnnotatorStats])
async def get_annotator_stats(
    task_type: str = Query("keywords", description="keywords or rules"),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取标注员统计信息（管理员查看）"""
    if task_type == "keywords":
        # 统计每个标注员的完成情况
        stmt = select(
            StagingGlobalKeywords.annotator,
            func.sum(func.if_(StagingGlobalKeywords.status == "REVIEWED", 1, 0)).label("reviewed_count"),
            func.sum(func.if_(StagingGlobalKeywords.status == "IGNORED", 1, 0)).label("ignored_count"),
            func.count(StagingGlobalKeywords.id).label("total_count")
        ).where(
            StagingGlobalKeywords.annotator.isnot(None)
        ).group_by(
            StagingGlobalKeywords.annotator
        )
    else:
        stmt = select(
            StagingGlobalRules.annotator,
            func.sum(func.if_(StagingGlobalRules.status == "REVIEWED", 1, 0)).label("reviewed_count"),
            func.sum(func.if_(StagingGlobalRules.status == "IGNORED", 1, 0)).label("ignored_count"),
            func.count(StagingGlobalRules.id).label("total_count")
        ).where(
            StagingGlobalRules.annotator.isnot(None)
        ).group_by(
            StagingGlobalRules.annotator
        )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        AnnotatorStats(
            annotator=row.annotator,
            reviewed_count=row.reviewed_count,
            ignored_count=row.ignored_count,
            total_count=row.total_count
        )
        for row in rows
    ]


class MyTasksStats(BaseModel):
    claimed_count: int
    reviewed_count: int
    ignored_count: int
    batch_id: Optional[str]
    claimed_at: Optional[datetime]
    expires_at: Optional[datetime]

@router.get("/my-tasks/stats", response_model=MyTasksStats)
async def get_my_tasks_stats(
    task_type: str = Query("keywords", description="keywords or rules"),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """获取当前用户的任务统计"""
    if task_type == "keywords":
        # 查询当前用户认领的任务
        stmt_claimed = select(StagingGlobalKeywords).where(
            and_(
                StagingGlobalKeywords.claimed_by == current_user,
                StagingGlobalKeywords.status == "CLAIMED"
            )
        )
        result_claimed = await db.execute(stmt_claimed)
        claimed_items = result_claimed.scalars().all()

        # 查询已完成的任务（本批次）
        batch_id = claimed_items[0].batch_id if claimed_items else None
        claimed_at = claimed_items[0].claimed_at if claimed_items else None

        if batch_id:
            stmt_batch = select(
                func.sum(func.if_(StagingGlobalKeywords.status == "REVIEWED", 1, 0)).label("reviewed_count"),
                func.sum(func.if_(StagingGlobalKeywords.status == "IGNORED", 1, 0)).label("ignored_count")
            ).where(
                StagingGlobalKeywords.batch_id == batch_id
            )
            result_batch = await db.execute(stmt_batch)
            row = result_batch.first()
            reviewed_count = row.reviewed_count if row else 0
            ignored_count = row.ignored_count if row else 0
        else:
            reviewed_count = 0
            ignored_count = 0
    else:
        # 规则任务统计
        stmt_claimed = select(StagingGlobalRules).where(
            and_(
                StagingGlobalRules.claimed_by == current_user,
                StagingGlobalRules.status == "CLAIMED"
            )
        )
        result_claimed = await db.execute(stmt_claimed)
        claimed_items = result_claimed.scalars().all()

        batch_id = claimed_items[0].batch_id if claimed_items else None
        claimed_at = claimed_items[0].claimed_at if claimed_items else None

        if batch_id:
            stmt_batch = select(
                func.sum(func.if_(StagingGlobalRules.status == "REVIEWED", 1, 0)).label("reviewed_count"),
                func.sum(func.if_(StagingGlobalRules.status == "IGNORED", 1, 0)).label("ignored_count")
            ).where(
                StagingGlobalRules.batch_id == batch_id
            )
            result_batch = await db.execute(stmt_batch)
            row = result_batch.first()
            reviewed_count = row.reviewed_count if row else 0
            ignored_count = row.ignored_count if row else 0
        else:
            reviewed_count = 0
            ignored_count = 0

    expires_at = None
    if claimed_at:
        # 如果 claimed_at 是 naive datetime，将其视为中国时区
        if claimed_at.tzinfo is None:
            claimed_at = CHINA_TZ.localize(claimed_at)
        expires_at = claimed_at + timedelta(minutes=30)

    return MyTasksStats(
        claimed_count=len(claimed_items),
        reviewed_count=reviewed_count,
        ignored_count=ignored_count,
        batch_id=batch_id,
        claimed_at=claimed_at,
        expires_at=expires_at
    )