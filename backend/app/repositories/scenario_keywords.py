from typing import List
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.db_meta import ScenarioKeywords

class ScenarioKeywordsRepository(BaseRepository[ScenarioKeywords]):
    async def get_by_scenario(self, scenario_id: str) -> List[ScenarioKeywords]:
        result = await self.db.execute(select(self.model).where(self.model.scenario_id == scenario_id))
        return result.scalars().all()
