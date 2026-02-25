from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class EvalTestCaseCreate(BaseModel):
    content: str = Field(..., min_length=1)
    tag_codes: Optional[List[str]] = None
    risk_point: Optional[str] = None
    expected_result: str = Field(..., pattern="^(COMPLIANT|VIOLATION)$")


class EvalTestCaseUpdate(BaseModel):
    content: Optional[str] = None
    tag_codes: Optional[List[str]] = None
    risk_point: Optional[str] = None
    expected_result: Optional[str] = None
    is_active: Optional[bool] = None


class EvalTaskCreate(BaseModel):
    task_name: str = Field(..., min_length=1)
    app_id: str = Field(..., min_length=1)
    concurrency: int = Field(default=5, ge=1, le=20)
    filter_tag_codes: Optional[List[str]] = None
    filter_expected_result: Optional[str] = None
