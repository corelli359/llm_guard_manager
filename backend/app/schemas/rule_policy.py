from typing import Optional
from pydantic import BaseModel, field_validator, ConfigDict

class RuleScenarioPolicyBase(BaseModel):
    scenario_id: str
    match_type: str  # KEYWORD / TAG
    match_value: str
    rule_mode: int = 1  # 0: Super, 1: Custom
    extra_condition: Optional[str] = None
    strategy: str  # BLOCK / PASS / REWRITE
    is_active: bool = True

    @field_validator('match_type')
    def validate_match_type(cls, v):
        if v not in ('KEYWORD', 'TAG'):
            raise ValueError('match_type must be KEYWORD or TAG')
        return v

    @field_validator('rule_mode')
    def validate_rule_mode(cls, v):
        if v not in (0, 1):
            raise ValueError('rule_mode must be 0 (Super) or 1 (Custom)')
        return v

class RuleScenarioPolicyCreate(RuleScenarioPolicyBase):
    pass

class RuleScenarioPolicyUpdate(BaseModel):
    scenario_id: Optional[str] = None
    match_type: Optional[str] = None
    match_value: Optional[str] = None
    rule_mode: Optional[int] = None
    extra_condition: Optional[str] = None
    strategy: Optional[str] = None
    is_active: Optional[bool] = None

class RuleScenarioPolicyResponse(RuleScenarioPolicyBase):
    id: str
    model_config = ConfigDict(from_attributes=True)

# --- Global Defaults ---

class RuleGlobalDefaultsBase(BaseModel):
    tag_code: str | None = None
    extra_condition: str | None = None
    strategy: str
    is_active: bool = True

class RuleGlobalDefaultsCreate(RuleGlobalDefaultsBase):
    pass

class RuleGlobalDefaultsUpdate(BaseModel):
    tag_code: str | None = None
    extra_condition: str | None = None
    strategy: str | None = None
    is_active: bool | None = None

class RuleGlobalDefaultsResponse(RuleGlobalDefaultsBase):
    id: str
    model_config = ConfigDict(from_attributes=True)
