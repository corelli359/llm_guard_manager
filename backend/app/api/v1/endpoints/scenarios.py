from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.scenarios import ScenariosResponse, ScenariosCreate, ScenariosUpdate
from app.services.scenarios import ScenariosService
from app.services.audit import AuditService
from app.api.v1.deps import get_current_user, get_current_user_full, require_role
from app.models.db_meta import User

router = APIRouter()

@router.get("/", response_model=List[ScenariosResponse])
async def read_scenarios(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    """获取场景列表（所有角色可访问）"""
    service = ScenariosService(db)
    return await service.get_all_scenarios(skip, limit)

@router.post("/", response_model=ScenariosResponse)
async def create_scenario(
    scenario_in: ScenariosCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
) -> Any:
    """创建场景（仅 SYSTEM_ADMIN）"""
    service = ScenariosService(db)
    try:
        result = await service.create_scenario(scenario_in)

        # 记录审计日志
        audit_service = AuditService(db)
        await audit_service.log_create(
            user_id=current_user.id,
            username=current_user.username,
            resource_type="SCENARIO",
            resource_id=result.id,
            scenario_id=result.app_id,
            details={"app_id": scenario_in.app_id, "app_name": scenario_in.app_name},
            request=request
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{app_id}", response_model=ScenariosResponse)
async def read_scenario_by_app_id(
    app_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    """获取场景详情（所有角色可访问）"""
    service = ScenariosService(db)
    scenario = await service.get_by_app_id(app_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario

@router.put("/{scenario_id}", response_model=ScenariosResponse)
async def update_scenario(
    scenario_id: str,
    scenario_in: ScenariosUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
) -> Any:
    """更新场景（仅 SYSTEM_ADMIN）"""
    service = ScenariosService(db)
    try:
        result = await service.update_scenario(scenario_id, scenario_in)

        # 记录审计日志
        audit_service = AuditService(db)
        await audit_service.log_update(
            user_id=current_user.id,
            username=current_user.username,
            resource_type="SCENARIO",
            resource_id=scenario_id,
            details=scenario_in.model_dump(exclude_unset=True),
            request=request
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{scenario_id}", response_model=ScenariosResponse)
async def delete_scenario(
    scenario_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
) -> Any:
    """删除场景（仅 SYSTEM_ADMIN）"""
    service = ScenariosService(db)
    scenario = await service.delete_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # 记录审计日志
    audit_service = AuditService(db)
    await audit_service.log_delete(
        user_id=current_user.id,
        username=current_user.username,
        resource_type="SCENARIO",
        resource_id=scenario_id,
        request=request
    )

    return scenario
