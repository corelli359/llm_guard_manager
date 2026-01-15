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
        # Validate that tag_code is required for both Blacklist and Whitelist
        if not keyword_in.tag_code:
             raise ValueError("Tag Code is required for all keywords.")

        # Check for duplicates in the same scenario and rule_mode
        existing = await self.repository.get_duplicate(
            keyword_in.scenario_id, 
            keyword_in.keyword,
            keyword_in.rule_mode
        )
        if existing:
            mode_str = "Custom Mode" if keyword_in.rule_mode == 1 else "Super Mode"
            raise ValueError(f"Keyword '{keyword_in.keyword}' already exists in scenario '{keyword_in.scenario_id}' for {mode_str}.")

        obj_in_data = keyword_in.model_dump()
        obj_in_data['id'] = str(uuid.uuid4())
        return await self.repository.create(obj_in_data)

    async def get_by_scenario(self, scenario_id: str, rule_mode: Optional[int] = None) -> List[ScenarioKeywords]:
        return await self.repository.get_by_scenario(scenario_id, rule_mode)

    async def get_keyword(self, keyword_id: str) -> Optional[ScenarioKeywords]:
        return await self.repository.get(keyword_id)

    async def update_keyword(self, keyword_id: str, keyword_in: ScenarioKeywordsUpdate) -> ScenarioKeywords:
        keyword = await self.repository.get(keyword_id)
        if not keyword:
            raise ValueError("Keyword not found")

        # Determine the final state
        new_tag_code = keyword_in.tag_code if keyword_in.tag_code is not None else keyword.tag_code
        
        if not new_tag_code:
             raise ValueError("Tag Code is required for all keywords.")

        return await self.repository.update(keyword, keyword_in)

    async def delete_keyword(self, keyword_id: str) -> Optional[ScenarioKeywords]:
        return await self.repository.delete(keyword_id)
