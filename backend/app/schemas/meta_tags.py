from typing import Optional
from pydantic import BaseModel, ConfigDict

class MetaTagsBase(BaseModel):
    tag_code: str
    tag_name: str
    parent_code: Optional[str] = None
    level: int = 2
    is_active: bool = True

class MetaTagsCreate(MetaTagsBase):
    pass

class MetaTagsUpdate(BaseModel):
    tag_name: Optional[str] = None
    parent_code: Optional[str] = None
    level: Optional[int] = None
    is_active: Optional[bool] = None

class MetaTagsResponse(MetaTagsBase):
    id: str
    
    model_config = ConfigDict(from_attributes=True)
