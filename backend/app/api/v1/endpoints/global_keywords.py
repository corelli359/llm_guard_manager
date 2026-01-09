from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.global_keywords import GlobalKeywordsResponse, GlobalKeywordsCreate, GlobalKeywordsUpdate
from app.services.global_keywords import GlobalKeywordsService

router = APIRouter()

@router.get("/", response_model=List[GlobalKeywordsResponse])
async def read_keywords(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = GlobalKeywordsService(db)
    return await service.get_all_keywords(skip, limit)

@router.post("/", response_model=GlobalKeywordsResponse)
async def create_keyword(
    keyword_in: GlobalKeywordsCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = GlobalKeywordsService(db)
    return await service.create_keyword(keyword_in)

@router.put("/{keyword_id}", response_model=GlobalKeywordsResponse)
async def update_keyword(
    keyword_id: str,
    keyword_in: GlobalKeywordsUpdate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = GlobalKeywordsService(db)
    try:
        return await service.update_keyword(keyword_id, keyword_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{keyword_id}", response_model=GlobalKeywordsResponse)
async def delete_keyword(
    keyword_id: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = GlobalKeywordsService(db)
    keyword = await service.delete_keyword(keyword_id)
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")
    return keyword
