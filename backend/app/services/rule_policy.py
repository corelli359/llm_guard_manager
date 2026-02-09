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
        
        # Check for duplicates
        existing = await self.scenario_repo.get_duplicate(
            policy_in.scenario_id, 
            policy_in.rule_mode, 
            policy_in.match_type, 
            policy_in.match_value
        )
        if existing:
            raise ValueError(
                f"Duplicate policy: Scenario '{policy_in.scenario_id}' already has a rule for "
                f"Mode {policy_in.rule_mode}, Type {policy_in.match_type}, Value '{policy_in.match_value}'."
            )

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
        # Business logic validation: if tag_code is empty, extra_condition must be provided
        if not default_in.tag_code and not default_in.extra_condition:
            raise ValueError("When tag_code is empty, extra_condition must be provided.")

        # Check for duplicates
        existing = await self.global_repo.get_duplicate(default_in.tag_code, default_in.extra_condition)
        if existing:
            tag_display = default_in.tag_code if default_in.tag_code else "(空)"
            condition_display = default_in.extra_condition if default_in.extra_condition else "(无)"
            raise ValueError(
                f"Duplicate global default: Rule for Tag '{tag_display}' "
                f"with condition '{condition_display}' already exists."
            )

        obj_in_data = default_in.model_dump()
        obj_in_data['id'] = str(uuid.uuid4())
        return await self.global_repo.create(obj_in_data)

    async def get_all_global_defaults(self, skip: int = 0, limit: int = 100) -> List[RuleGlobalDefaults]:
        return await self.global_repo.get_all(skip, limit)
    
    async def update_global_default(self, default_id: str, default_in: RuleGlobalDefaultsUpdate) -> RuleGlobalDefaults:
        default_obj = await self.global_repo.get(default_id)
        if not default_obj:
            raise ValueError("Global Default not found")

        # Business logic validation: if tag_code is being set to empty, extra_condition must be provided
        updated_tag_code = default_in.tag_code if default_in.tag_code is not None else default_obj.tag_code
        updated_extra_condition = default_in.extra_condition if default_in.extra_condition is not None else default_obj.extra_condition

        if not updated_tag_code and not updated_extra_condition:
            raise ValueError("When tag_code is empty, extra_condition must be provided.")

        return await self.global_repo.update(default_obj, default_in)

    async def delete_global_default(self, default_id: str) -> Optional[RuleGlobalDefaults]:
        return await self.global_repo.delete(default_id)
