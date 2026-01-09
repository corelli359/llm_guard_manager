from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.meta_tags import MetaTagsResponse, MetaTagsCreate, MetaTagsUpdate
from app.services.meta_tags import MetaTagsService

router = APIRouter()

@router.get("/", response_model=List[MetaTagsResponse])
async def read_tags(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = MetaTagsService(db)
    return await service.get_all_tags(skip, limit)

@router.post("/", response_model=MetaTagsResponse)
async def create_tag(
    tag_in: MetaTagsCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = MetaTagsService(db)
    try:
        return await service.create_tag(tag_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{tag_id}", response_model=MetaTagsResponse)
async def update_tag(
    tag_id: str,
    tag_in: MetaTagsUpdate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = MetaTagsService(db)
    try:
        return await service.update_tag(tag_id, tag_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{tag_id}", response_model=MetaTagsResponse)
async def delete_tag(
    tag_id: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = MetaTagsService(db)
    tag = await service.delete_tag(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag
