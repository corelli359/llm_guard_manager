import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.scenarios import ScenariosRepository
from app.schemas.scenarios import ScenariosCreate, ScenariosUpdate
from app.models.db_meta import Scenarios

class ScenariosService:
    def __init__(self, db: AsyncSession):
        self.repository = ScenariosRepository(Scenarios, db)

    async def create_scenario(self, scenario_in: ScenariosCreate) -> Scenarios:
        existing = await self.repository.get_by_app_id(scenario_in.app_id)
        if existing:
            raise ValueError(f"App ID {scenario_in.app_id} already exists")
            
        obj_in_data = scenario_in.model_dump()
        obj_in_data['id'] = str(uuid.uuid4())
        return await self.repository.create(obj_in_data)

    async def get_all_scenarios(self, skip: int = 0, limit: int = 100) -> List[Scenarios]:
        return await self.repository.get_all(skip, limit)

    async def get_scenario(self, scenario_id: str) -> Optional[Scenarios]:
        # get by PK
        return await self.repository.get(scenario_id)

    async def get_by_app_id(self, app_id: str) -> Optional[Scenarios]:
        return await self.repository.get_by_app_id(app_id)

    async def update_scenario(self, scenario_id: str, scenario_in: ScenariosUpdate) -> Scenarios:
        scenario = await self.repository.get(scenario_id)
        if not scenario:
            raise ValueError("Scenario not found")
        return await self.repository.update(scenario, scenario_in)

    async def delete_scenario(self, scenario_id: str) -> Optional[Scenarios]:
        return await self.repository.delete(scenario_id)
