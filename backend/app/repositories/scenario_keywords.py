from typing import List, Optional
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.db_meta import ScenarioKeywords

class ScenarioKeywordsRepository(BaseRepository[ScenarioKeywords]):
    async def get_by_scenario(self, scenario_id: str, rule_mode: Optional[int] = None) -> List[ScenarioKeywords]:
        query = select(self.model).where(self.model.scenario_id == scenario_id)
        if rule_mode is not None:
            query = query.where(self.model.rule_mode == rule_mode)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_duplicate(self, scenario_id: str, keyword: str, rule_mode: int) -> Optional[ScenarioKeywords]:
        query = select(self.model).where(
            (self.model.scenario_id == scenario_id) & 
            (self.model.keyword == keyword) &
            (self.model.rule_mode == rule_mode)
        )
        result = await self.db.execute(query)
        return result.scalars().first()
