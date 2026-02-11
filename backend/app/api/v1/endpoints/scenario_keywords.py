from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.scenario_keywords import ScenarioKeywordsResponse, ScenarioKeywordsCreate, ScenarioKeywordsUpdate
from app.services.scenario_keywords import ScenarioKeywordsService
from app.services.audit import AuditService
from app.api.v1.deps import get_current_user, get_current_user_full
from app.api.v1.permission_helpers import check_scenario_access_or_403
from app.models.db_meta import User

router = APIRouter()

@router.get("/{scenario_id}", response_model=List[ScenarioKeywordsResponse])
async def read_scenario_keywords(
    scenario_id: str,
    rule_mode: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """获取场景敏感词列表"""
    # 权限检查：需要有场景访问权限
    await check_scenario_access_or_403(current_user, scenario_id, db, permission="scenario_keywords")

    service = ScenarioKeywordsService(db)
    return await service.get_by_scenario(scenario_id, rule_mode)

@router.post("/", response_model=ScenarioKeywordsResponse)
async def create_scenario_keyword(
    keyword_in: ScenarioKeywordsCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """创建场景敏感词"""
    # 权限检查：需要有场景敏感词权限
    await check_scenario_access_or_403(current_user, keyword_in.scenario_id, db, permission="scenario_keywords")

    service = ScenarioKeywordsService(db)
    try:
        result = await service.create_keyword(keyword_in)

        # 记录审计日志
        audit_service = AuditService(db)
        await audit_service.log_create(
            user_id=current_user.id,
            username=current_user.username,
            resource_type="SCENARIO_KEYWORD",
            resource_id=result.id,
            scenario_id=keyword_in.scenario_id,
            details={"keyword": keyword_in.keyword, "tag_code": keyword_in.tag_code},
            request=request
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{keyword_id}", response_model=ScenarioKeywordsResponse)
async def update_scenario_keyword(
    keyword_id: str,
    keyword_in: ScenarioKeywordsUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """更新场景敏感词"""
    service = ScenarioKeywordsService(db)

    # 先获取关键词以检查权限
    from app.repositories.scenario_keywords import ScenarioKeywordsRepository
    from app.models.db_meta import ScenarioKeywords
    repo = ScenarioKeywordsRepository(ScenarioKeywords, db)
    existing = await repo.get(keyword_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Keyword not found")

    # 权限检查
    await check_scenario_access_or_403(current_user, existing.scenario_id, db, permission="scenario_keywords")

    try:
        result = await service.update_keyword(keyword_id, keyword_in)

        # 记录审计日志
        audit_service = AuditService(db)
        await audit_service.log_update(
            user_id=current_user.id,
            username=current_user.username,
            resource_type="SCENARIO_KEYWORD",
            resource_id=keyword_id,
            scenario_id=existing.scenario_id,
            details=keyword_in.model_dump(exclude_unset=True),
            request=request
        )

        return result
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
             raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)

@router.delete("/{keyword_id}", response_model=ScenarioKeywordsResponse)
async def delete_scenario_keyword(
    keyword_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """删除场景敏感词"""
    # 先获取关键词以检查权限
    from app.repositories.scenario_keywords import ScenarioKeywordsRepository
    from app.models.db_meta import ScenarioKeywords
    repo = ScenarioKeywordsRepository(ScenarioKeywords, db)
    existing = await repo.get(keyword_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Keyword not found")

    # 权限检查
    await check_scenario_access_or_403(current_user, existing.scenario_id, db, permission="scenario_keywords")

    service = ScenarioKeywordsService(db)
    keyword = await service.delete_keyword(keyword_id)
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    # 记录审计日志
    audit_service = AuditService(db)
    await audit_service.log_delete(
        user_id=current_user.id,
        username=current_user.username,
        resource_type="SCENARIO_KEYWORD",
        resource_id=keyword_id,
        scenario_id=existing.scenario_id,
        request=request
    )

    return keyword
