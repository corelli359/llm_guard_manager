from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.rule_policy import (
    RuleScenarioPolicyResponse, RuleScenarioPolicyCreate, RuleScenarioPolicyUpdate,
    RuleGlobalDefaultsResponse, RuleGlobalDefaultsCreate, RuleGlobalDefaultsUpdate
)
from app.services.rule_policy import RulePolicyService
from app.api.v1.deps import get_current_user

router = APIRouter()

# --- Scenario Policies ---

@router.get("/scenario/{scenario_id}", response_model=List[RuleScenarioPolicyResponse])
async def read_scenario_policies(
    scenario_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    service = RulePolicyService(db)
    return await service.get_scenario_policies(scenario_id)

@router.post("/scenario/", response_model=RuleScenarioPolicyResponse)
async def create_scenario_policy(
    policy_in: RuleScenarioPolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    service = RulePolicyService(db)
    try:
        return await service.create_scenario_policy(policy_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/scenario/{policy_id}", response_model=RuleScenarioPolicyResponse)
async def update_scenario_policy(
    policy_id: str,
    policy_in: RuleScenarioPolicyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    service = RulePolicyService(db)
    try:
        return await service.update_scenario_policy(policy_id, policy_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/scenario/{policy_id}", response_model=RuleScenarioPolicyResponse)
async def delete_scenario_policy(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    service = RulePolicyService(db)
    policy = await service.delete_scenario_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

# --- Global Defaults ---

@router.get("/defaults/", response_model=List[RuleGlobalDefaultsResponse])
async def read_global_defaults(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    service = RulePolicyService(db)
    return await service.get_all_global_defaults(skip, limit)

@router.post("/defaults/", response_model=RuleGlobalDefaultsResponse)
async def create_global_default(
    default_in: RuleGlobalDefaultsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    service = RulePolicyService(db)
    return await service.create_global_default(default_in)

@router.put("/defaults/{default_id}", response_model=RuleGlobalDefaultsResponse)
async def update_global_default(
    default_id: str,
    default_in: RuleGlobalDefaultsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    service = RulePolicyService(db)
    try:
        return await service.update_global_default(default_id, default_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/defaults/{default_id}", response_model=RuleGlobalDefaultsResponse)
async def delete_global_default(
    default_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
) -> Any:
    service = RulePolicyService(db)
    default_obj = await service.delete_global_default(default_id)
    if not default_obj:
        raise HTTPException(status_code=404, detail="Global Default not found")
    return default_obj
