from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.scenarios import ScenariosResponse, ScenariosCreate, ScenariosUpdate
from app.services.scenarios import ScenariosService

router = APIRouter()

@router.get("/", response_model=List[ScenariosResponse])
async def read_scenarios(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = ScenariosService(db)
    return await service.get_all_scenarios(skip, limit)

@router.post("/", response_model=ScenariosResponse)
async def create_scenario(
    scenario_in: ScenariosCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = ScenariosService(db)
    try:
        return await service.create_scenario(scenario_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{app_id}", response_model=ScenariosResponse)
async def read_scenario_by_app_id(
    app_id: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = ScenariosService(db)
    scenario = await service.get_by_app_id(app_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario

@router.put("/{scenario_id}", response_model=ScenariosResponse)
async def update_scenario(
    scenario_id: str,
    scenario_in: ScenariosUpdate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = ScenariosService(db)
    try:
        return await service.update_scenario(scenario_id, scenario_in)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{scenario_id}", response_model=ScenariosResponse)
async def delete_scenario(
    scenario_id: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = ScenariosService(db)
    scenario = await service.delete_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario
