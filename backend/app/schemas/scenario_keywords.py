from typing import Optional
from pydantic import BaseModel, ConfigDict

class ScenarioKeywordsBase(BaseModel):
    scenario_id: str
    keyword: str
    tag_code: Optional[str] = None
    rule_mode: int = 1  # 0: Super, 1: Custom
    risk_level: Optional[str] = None
    is_active: bool = True
    category: int = 1 # Default Black

class ScenarioKeywordsCreate(ScenarioKeywordsBase):
    pass

class ScenarioKeywordsUpdate(BaseModel):
    scenario_id: Optional[str] = None
    keyword: Optional[str] = None
    tag_code: Optional[str] = None
    rule_mode: Optional[int] = None
    risk_level: Optional[str] = None
    is_active: Optional[bool] = None
    category: Optional[int] = None

class ScenarioKeywordsResponse(ScenarioKeywordsBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
