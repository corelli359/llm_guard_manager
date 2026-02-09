from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.api.v1.deps import get_current_user, get_current_user_full
from app.api.v1.permission_helpers import check_scenario_access_or_403
from app.schemas.playground import PlaygroundInputRequest, PlaygroundHistorySchema
from app.services.playground import PlaygroundService
from app.services.audit import AuditService
from app.models.db_meta import User

router = APIRouter()

@router.post("/input", response_model=Any)
async def playground_input(
    payload: PlaygroundInputRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """运行输入测试"""
    # 权限检查：需要有 playground 权限
    await check_scenario_access_or_403(current_user, payload.app_id, db, permission="playground")

    service = PlaygroundService(db)
    try:
        result = await service.run_input_check(payload)

        # 记录审计日志
        audit_service = AuditService(db)
        await audit_service.log_create(
            user_id=current_user.id,
            username=current_user.username,
            resource_type="PLAYGROUND_TEST",
            scenario_id=payload.app_id,
            details={"playground_type": payload.playground_type, "score": result.get("score")},
            request=request
        )

        return result
    except Exception as e:
        # Check if it's an HTTPException already
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error processing playground request: {str(e)}"
        )

@router.get("/history", response_model=List[PlaygroundHistorySchema])
async def get_playground_history(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    playground_type: Optional[str] = None,
    app_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """获取测试历史记录"""
    # 如果指定了 app_id，检查权限
    if app_id:
        await check_scenario_access_or_403(current_user, app_id, db, permission="playground")

    service = PlaygroundService(db)
    return await service.get_history(page, size, playground_type, app_id)
