from typing import List, Optional
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.db_meta import ScenarioKeywords

class ScenarioKeywordsRepository(BaseRepository[ScenarioKeywords]):
    async def get_by_scenario(self, scenario_id: str) -> List[ScenarioKeywords]:
        result = await self.db.execute(select(self.model).where(self.model.scenario_id == scenario_id))
        return result.scalars().all()

    async def get_by_scenario_and_keyword(self, scenario_id: str, keyword: str) -> Optional[ScenarioKeywords]:
        query = select(self.model).where(
            (self.model.scenario_id == scenario_id) & 
            (self.model.keyword == keyword)
        )
        result = await self.db.execute(query)
        return result.scalars().first()
