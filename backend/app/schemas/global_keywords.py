from pydantic import BaseModel, ConfigDict

class GlobalKeywordsBase(BaseModel):
    keyword: str
    tag_code: str
    risk_level: str
    is_active: bool = True

class GlobalKeywordsCreate(GlobalKeywordsBase):
    pass

class GlobalKeywordsUpdate(BaseModel):
    keyword: str | None = None
    tag_code: str | None = None
    risk_level: str | None = None
    is_active: bool | None = None

class GlobalKeywordsResponse(GlobalKeywordsBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
