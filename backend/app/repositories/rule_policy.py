from typing import List, Optional
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.db_meta import RuleScenarioPolicy, RuleGlobalDefaults

class RuleScenarioPolicyRepository(BaseRepository[RuleScenarioPolicy]):
    async def get_by_scenario(self, scenario_id: str) -> List[RuleScenarioPolicy]:
        result = await self.db.execute(select(self.model).where(self.model.scenario_id == scenario_id))
        return result.scalars().all()

class RuleGlobalDefaultsRepository(BaseRepository[RuleGlobalDefaults]):
    pass
