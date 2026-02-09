from typing import List, Optional
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.db_meta import RuleScenarioPolicy, RuleGlobalDefaults

class RuleScenarioPolicyRepository(BaseRepository[RuleScenarioPolicy]):
    async def get_by_scenario(self, scenario_id: str) -> List[RuleScenarioPolicy]:
        result = await self.db.execute(select(self.model).where(self.model.scenario_id == scenario_id))
        return result.scalars().all()

    async def get_duplicate(self, scenario_id: str, rule_mode: int, match_type: str, match_value: str) -> Optional[RuleScenarioPolicy]:
        query = select(self.model).where(
            (self.model.scenario_id == scenario_id) &
            (self.model.rule_mode == rule_mode) &
            (self.model.match_type == match_type) &
            (self.model.match_value == match_value)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

class RuleGlobalDefaultsRepository(BaseRepository[RuleGlobalDefaults]):
    async def get_duplicate(self, tag_code: str | None, extra_condition: str | None) -> RuleGlobalDefaults | None:
        # Build query based on tag_code
        if tag_code:
            query = select(self.model).where(self.model.tag_code == tag_code)
        else:
            query = select(self.model).where(self.model.tag_code.is_(None) | (self.model.tag_code == ''))

        # Add extra_condition filter
        if extra_condition:
            query = query.where(self.model.extra_condition == extra_condition)
        else:
            query = query.where(self.model.extra_condition.is_(None) | (self.model.extra_condition == ''))

        result = await self.db.execute(query)
        return result.scalars().first()
