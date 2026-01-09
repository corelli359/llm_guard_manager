from typing import Optional
from pydantic import BaseModel

class ScenariosBase(BaseModel):
    app_id: str
    app_name: str
    description: Optional[str] = None
    is_active: bool = True
    enable_whitelist: bool = True
    enable_blacklist: bool = True
    enable_custom_policy: bool = True

class ScenariosCreate(ScenariosBase):
    pass

class ScenariosUpdate(BaseModel):
    app_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    enable_whitelist: Optional[bool] = None
    enable_blacklist: Optional[bool] = None
    enable_custom_policy: Optional[bool] = None

class ScenariosResponse(ScenariosBase):
    id: str
    class Config:
        from_attributes = True
