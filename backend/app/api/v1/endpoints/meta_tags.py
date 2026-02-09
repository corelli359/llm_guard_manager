from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.meta_tags import MetaTagsResponse, MetaTagsCreate, MetaTagsUpdate
from app.services.meta_tags import MetaTagsService
from app.services.audit import AuditService
from app.api.v1.deps import get_current_user, get_current_user_full, require_role
from app.models.db_meta import User

router = APIRouter()

@router.get("/", response_model=List[MetaTagsResponse])
async def read_tags(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    """获取标签列表（所有角色可访问）"""
    service = MetaTagsService(db)
    return await service.get_all_tags(skip, limit)

@router.post("/", response_model=MetaTagsResponse)
async def create_tag(
    tag_in: MetaTagsCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
) -> Any:
    """创建标签（仅 SYSTEM_ADMIN）"""
    service = MetaTagsService(db)
    try:
        result = await service.create_tag(tag_in)

        # 记录审计日志
        audit_service = AuditService(db)
        await audit_service.log_create(
            user_id=current_user.id,
            username=current_user.username,
            resource_type="META_TAG",
            resource_id=result.id,
            details={"tag_code": tag_in.tag_code, "tag_name": tag_in.tag_name},
            request=request
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{tag_id}", response_model=MetaTagsResponse)
async def update_tag(
    tag_id: str,
    tag_in: MetaTagsUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
) -> Any:
    """更新标签（仅 SYSTEM_ADMIN）"""
    service = MetaTagsService(db)
    try:
        result = await service.update_tag(tag_id, tag_in)

        # 记录审计日志
        audit_service = AuditService(db)
        await audit_service.log_update(
            user_id=current_user.id,
            username=current_user.username,
            resource_type="META_TAG",
            resource_id=tag_id,
            details=tag_in.model_dump(exclude_unset=True),
            request=request
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{tag_id}", response_model=MetaTagsResponse)
async def delete_tag(
    tag_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
) -> Any:
    """删除标签（仅 SYSTEM_ADMIN）"""
    service = MetaTagsService(db)
    tag = await service.delete_tag(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # 记录审计日志
    audit_service = AuditService(db)
    await audit_service.log_delete(
        user_id=current_user.id,
        username=current_user.username,
        resource_type="META_TAG",
        resource_id=tag_id,
        request=request
    )

    return tag
