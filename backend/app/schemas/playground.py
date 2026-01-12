from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class PlaygroundInputRequest(BaseModel):
    app_id: str = Field(..., min_length=1, description="应用标识ID (scenario_id)")
    input_prompt: str = Field(..., min_length=1, description="需要检测的用户输入文本")
    use_customize_white: bool = False
    use_customize_words: bool = False
    use_customize_rule: bool = False
    use_vip_black: bool = False
    use_vip_white: bool = False

class PlaygroundResponse(BaseModel):
    # 这里直接使用 Dict 接收围栏服务的原始响应，以便前端调试
    # 也可以根据需求定义更具体的结构
    all_decision_dict: Optional[Dict[str, Any]] = None
    final_decision: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None

class PlaygroundHistorySchema(BaseModel):
    id: str
    request_id: str
    playground_type: str
    app_id: str
    input_data: Dict[str, Any]
    config_snapshot: Dict[str, Any]
    output_data: Dict[str, Any]
    score: int
    latency: Optional[int] = None
    upstream_latency: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True