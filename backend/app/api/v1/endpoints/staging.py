from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.db import get_db
from app.api.v1.deps import get_current_user
from app.models.db_meta import StagingGlobalKeywords, GlobalKeywords, StagingGlobalRules, RuleGlobalDefaults
from pydantic import BaseModel
from datetime import datetime
import uuid

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
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    stmt = select(StagingGlobalKeywords)
    if status:
        stmt = stmt.where(StagingGlobalKeywords.status == status)
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
    item.annotated_at = datetime.now()
    
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
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    stmt = select(StagingGlobalRules)
    if status:
        stmt = stmt.where(StagingGlobalRules.status == status)
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
    item.annotated_at = datetime.now()
    
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