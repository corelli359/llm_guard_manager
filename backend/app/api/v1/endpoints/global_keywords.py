from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.global_keywords import GlobalKeywordsResponse, GlobalKeywordsCreate, GlobalKeywordsUpdate
from app.services.global_keywords import GlobalKeywordsService
from app.services.audit import AuditService
from app.api.v1.deps import get_current_user, get_current_user_full, require_role
from app.models.db_meta import User

router = APIRouter()

@router.get("/", response_model=List[GlobalKeywordsResponse])
async def read_keywords(
    skip: int = 0,
    limit: int = 100,
    q: str = None,
    tag: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    """获取全局敏感词列表（所有角色可访问）"""
    service = GlobalKeywordsService(db)
    return await service.get_all_keywords(skip, limit, keyword=q, tag_code=tag)

@router.post("/", response_model=GlobalKeywordsResponse)
async def create_keyword(
    keyword_in: GlobalKeywordsCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
) -> Any:
    """创建全局敏感词（仅 SYSTEM_ADMIN）"""
    service = GlobalKeywordsService(db)
    try:
        result = await service.create_keyword(keyword_in)

        # 记录审计日志
        audit_service = AuditService(db)
        await audit_service.log_create(
            user_id=current_user.id,
            username=current_user.username,
            resource_type="GLOBAL_KEYWORD",
            resource_id=result.id,
            details={"keyword": keyword_in.keyword, "tag_code": keyword_in.tag_code},
            request=request
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{keyword_id}", response_model=GlobalKeywordsResponse)
async def update_keyword(
    keyword_id: str,
    keyword_in: GlobalKeywordsUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
) -> Any:
    """更新全局敏感词（仅 SYSTEM_ADMIN）"""
    service = GlobalKeywordsService(db)
    try:
        result = await service.update_keyword(keyword_id, keyword_in)

        # 记录审计日志
        audit_service = AuditService(db)
        await audit_service.log_update(
            user_id=current_user.id,
            username=current_user.username,
            resource_type="GLOBAL_KEYWORD",
            resource_id=keyword_id,
            details=keyword_in.model_dump(exclude_unset=True),
            request=request
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{keyword_id}", response_model=GlobalKeywordsResponse)
async def delete_keyword(
    keyword_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
) -> Any:
    """删除全局敏感词（仅 SYSTEM_ADMIN）"""
    service = GlobalKeywordsService(db)
    keyword = await service.delete_keyword(keyword_id)
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    # 记录审计日志
    audit_service = AuditService(db)
    await audit_service.log_delete(
        user_id=current_user.id,
        username=current_user.username,
        resource_type="GLOBAL_KEYWORD",
        resource_id=keyword_id,
        request=request
    )

    return keyword
