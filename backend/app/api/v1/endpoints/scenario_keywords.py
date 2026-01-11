from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.scenario_keywords import ScenarioKeywordsResponse, ScenarioKeywordsCreate, ScenarioKeywordsUpdate
from app.services.scenario_keywords import ScenarioKeywordsService
from app.api.v1.deps import get_current_user

router = APIRouter()

@router.get("/{scenario_id}", response_model=List[ScenarioKeywordsResponse])
async def read_scenario_keywords(
    scenario_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    service = ScenarioKeywordsService(db)
    return await service.get_by_scenario(scenario_id)

@router.post("/", response_model=ScenarioKeywordsResponse)
async def create_scenario_keyword(
    keyword_in: ScenarioKeywordsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    service = ScenarioKeywordsService(db)
    try:
        return await service.create_keyword(keyword_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{keyword_id}", response_model=ScenarioKeywordsResponse)
async def update_scenario_keyword(
    keyword_id: str,
    keyword_in: ScenarioKeywordsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    service = ScenarioKeywordsService(db)
    try:
        return await service.update_keyword(keyword_id, keyword_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{keyword_id}", response_model=ScenarioKeywordsResponse)
async def delete_scenario_keyword(
    keyword_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    service = ScenarioKeywordsService(db)
    keyword = await service.delete_keyword(keyword_id)
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    return keyword
