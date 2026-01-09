import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.scenario_keywords import ScenarioKeywordsRepository
from app.schemas.scenario_keywords import ScenarioKeywordsCreate, ScenarioKeywordsUpdate
from app.models.db_meta import ScenarioKeywords

class ScenarioKeywordsService:
    def __init__(self, db: AsyncSession):
        self.repository = ScenarioKeywordsRepository(ScenarioKeywords, db)

    async def create_keyword(self, keyword_in: ScenarioKeywordsCreate) -> ScenarioKeywords:
        obj_in_data = keyword_in.model_dump()
        obj_in_data['id'] = str(uuid.uuid4())
        return await self.repository.create(obj_in_data)

    async def get_by_scenario(self, scenario_id: str) -> List[ScenarioKeywords]:
        return await self.repository.get_by_scenario(scenario_id)

    async def get_keyword(self, keyword_id: str) -> Optional[ScenarioKeywords]:
        return await self.repository.get(keyword_id)

    async def update_keyword(self, keyword_id: str, keyword_in: ScenarioKeywordsUpdate) -> ScenarioKeywords:
        keyword = await self.repository.get(keyword_id)
        if not keyword:
            raise ValueError("Keyword not found")
        return await self.repository.update(keyword, keyword_in)

    async def delete_keyword(self, keyword_id: str) -> Optional[ScenarioKeywords]:
        return await self.repository.delete(keyword_id)
