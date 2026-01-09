import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.rule_policy import RuleScenarioPolicyRepository, RuleGlobalDefaultsRepository
from app.schemas.rule_policy import (
    RuleScenarioPolicyCreate, RuleScenarioPolicyUpdate, 
    RuleGlobalDefaultsCreate, RuleGlobalDefaultsUpdate
)
from app.models.db_meta import RuleScenarioPolicy, RuleGlobalDefaults

class RulePolicyService:
    def __init__(self, db: AsyncSession):
        self.scenario_repo = RuleScenarioPolicyRepository(RuleScenarioPolicy, db)
        self.global_repo = RuleGlobalDefaultsRepository(RuleGlobalDefaults, db)

    # --- Scenario Policy ---

    async def create_scenario_policy(self, policy_in: RuleScenarioPolicyCreate) -> RuleScenarioPolicy:
        # Business logic validation
        if policy_in.match_type == 'TAG':
            if policy_in.extra_condition and policy_in.extra_condition not in ('safe', 'unsafe', 'controversial'):
                raise ValueError("For TAG match type, extra_condition must be 'safe', 'unsafe', or 'controversial' if provided.")
        
        obj_in_data = policy_in.model_dump()
        obj_in_data['id'] = str(uuid.uuid4())
        return await self.scenario_repo.create(obj_in_data)

    async def get_scenario_policies(self, scenario_id: str) -> List[RuleScenarioPolicy]:
        return await self.scenario_repo.get_by_scenario(scenario_id)

    async def update_scenario_policy(self, policy_id: str, policy_in: RuleScenarioPolicyUpdate) -> RuleScenarioPolicy:
        policy = await self.scenario_repo.get(policy_id)
        if not policy:
            raise ValueError("Policy not found")
        return await self.scenario_repo.update(policy, policy_in)

    async def delete_scenario_policy(self, policy_id: str) -> Optional[RuleScenarioPolicy]:
        return await self.scenario_repo.delete(policy_id)

    # --- Global Defaults ---

    async def create_global_default(self, default_in: RuleGlobalDefaultsCreate) -> RuleGlobalDefaults:
        obj_in_data = default_in.model_dump()
        obj_in_data['id'] = str(uuid.uuid4())
        return await self.global_repo.create(obj_in_data)

    async def get_all_global_defaults(self, skip: int = 0, limit: int = 100) -> List[RuleGlobalDefaults]:
        return await self.global_repo.get_all(skip, limit)
    
    async def update_global_default(self, default_id: str, default_in: RuleGlobalDefaultsUpdate) -> RuleGlobalDefaults:
        default_obj = await self.global_repo.get(default_id)
        if not default_obj:
            raise ValueError("Global Default not found")
        return await self.global_repo.update(default_obj, default_in)

    async def delete_global_default(self, default_id: str) -> Optional[RuleGlobalDefaults]:
        return await self.global_repo.delete(default_id)
