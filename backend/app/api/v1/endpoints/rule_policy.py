from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.rule_policy import (
    RuleScenarioPolicyResponse, RuleScenarioPolicyCreate, RuleScenarioPolicyUpdate,
    RuleGlobalDefaultsResponse, RuleGlobalDefaultsCreate, RuleGlobalDefaultsUpdate
)
from app.services.rule_policy import RulePolicyService
from app.services.audit import AuditService
from app.api.v1.deps import get_current_user, get_current_user_full, require_role
from app.api.v1.permission_helpers import check_scenario_access_or_403
from app.models.db_meta import User

router = APIRouter()

# --- Scenario Policies ---

@router.get("/scenario/{scenario_id}", response_model=List[RuleScenarioPolicyResponse])
async def read_scenario_policies(
    scenario_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """获取场景策略列表"""
    # 权限检查：需要有场景策略权限
    await check_scenario_access_or_403(current_user, scenario_id, db, permission="scenario_policies")

    service = RulePolicyService(db)
    return await service.get_scenario_policies(scenario_id)

@router.post("/scenario/", response_model=RuleScenarioPolicyResponse)
async def create_scenario_policy(
    policy_in: RuleScenarioPolicyCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """创建场景策略"""
    # 权限检查：需要有场景策略权限
    await check_scenario_access_or_403(current_user, policy_in.scenario_id, db, permission="scenario_policies")

    service = RulePolicyService(db)
    try:
        result = await service.create_scenario_policy(policy_in)

        # 记录审计日志
        audit_service = AuditService(db)
        await audit_service.log_create(
            user_id=current_user.id,
            username=current_user.username,
            resource_type="SCENARIO_POLICY",
            resource_id=result.id,
            scenario_id=policy_in.scenario_id,
            details={"match_type": policy_in.match_type, "strategy": policy_in.strategy},
            request=request
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/scenario/{policy_id}", response_model=RuleScenarioPolicyResponse)
async def update_scenario_policy(
    policy_id: str,
    policy_in: RuleScenarioPolicyUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """更新场景策略"""
    # 先获取策略以检查权限
    from app.repositories.rule_policy import RuleScenarioPolicyRepository
    from app.models.db_meta import RuleScenarioPolicy
    repo = RuleScenarioPolicyRepository(RuleScenarioPolicy, db)
    existing = await repo.get_by_id(policy_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Policy not found")

    # 权限检查
    await check_scenario_access_or_403(current_user, existing.scenario_id, db, permission="scenario_policies")

    service = RulePolicyService(db)
    try:
        result = await service.update_scenario_policy(policy_id, policy_in)

        # 记录审计日志
        audit_service = AuditService(db)
        await audit_service.log_update(
            user_id=current_user.id,
            username=current_user.username,
            resource_type="SCENARIO_POLICY",
            resource_id=policy_id,
            scenario_id=existing.scenario_id,
            details=policy_in.model_dump(exclude_unset=True),
            request=request
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/scenario/{policy_id}", response_model=RuleScenarioPolicyResponse)
async def delete_scenario_policy(
    policy_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_full)
) -> Any:
    """删除场景策略"""
    # 先获取策略以检查权限
    from app.repositories.rule_policy import RuleScenarioPolicyRepository
    from app.models.db_meta import RuleScenarioPolicy
    repo = RuleScenarioPolicyRepository(RuleScenarioPolicy, db)
    existing = await repo.get_by_id(policy_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Policy not found")

    # 权限检查
    await check_scenario_access_or_403(current_user, existing.scenario_id, db, permission="scenario_policies")

    service = RulePolicyService(db)
    policy = await service.delete_scenario_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    # 记录审计日志
    audit_service = AuditService(db)
    await audit_service.log_delete(
        user_id=current_user.id,
        username=current_user.username,
        resource_type="SCENARIO_POLICY",
        resource_id=policy_id,
        scenario_id=existing.scenario_id,
        request=request
    )

    return policy

# --- Global Defaults ---

@router.get("/defaults/", response_model=List[RuleGlobalDefaultsResponse])
async def read_global_defaults(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    """获取全局默认规则列表（所有角色可访问）"""
    service = RulePolicyService(db)
    return await service.get_all_global_defaults(skip, limit)

@router.post("/defaults/", response_model=RuleGlobalDefaultsResponse)
async def create_global_default(
    default_in: RuleGlobalDefaultsCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
) -> Any:
    """创建全局默认规则（仅 SYSTEM_ADMIN）"""
    service = RulePolicyService(db)
    try:
        result = await service.create_global_default(default_in)

        # 记录审计日志
        audit_service = AuditService(db)
        await audit_service.log_create(
            user_id=current_user.id,
            username=current_user.username,
            resource_type="GLOBAL_DEFAULT_POLICY",
            resource_id=result.id,
            details={"tag_code": default_in.tag_code, "strategy": default_in.strategy},
            request=request
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/defaults/{default_id}", response_model=RuleGlobalDefaultsResponse)
async def update_global_default(
    default_id: str,
    default_in: RuleGlobalDefaultsUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
) -> Any:
    """更新全局默认规则（仅 SYSTEM_ADMIN）"""
    service = RulePolicyService(db)
    try:
        result = await service.update_global_default(default_id, default_in)

        # 记录审计日志
        audit_service = AuditService(db)
        await audit_service.log_update(
            user_id=current_user.id,
            username=current_user.username,
            resource_type="GLOBAL_DEFAULT_POLICY",
            resource_id=default_id,
            details=default_in.model_dump(exclude_unset=True),
            request=request
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/defaults/{default_id}", response_model=RuleGlobalDefaultsResponse)
async def delete_global_default(
    default_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"]))
) -> Any:
    """删除全局默认规则（仅 SYSTEM_ADMIN）"""
    service = RulePolicyService(db)
    default_obj = await service.delete_global_default(default_id)
    if not default_obj:
        raise HTTPException(status_code=404, detail="Global Default not found")

    # 记录审计日志
    audit_service = AuditService(db)
    await audit_service.log_delete(
        user_id=current_user.id,
        username=current_user.username,
        resource_type="GLOBAL_DEFAULT_POLICY",
        resource_id=default_id,
        request=request
    )

    return default_obj
