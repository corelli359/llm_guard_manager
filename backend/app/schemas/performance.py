from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from enum import Enum

class TestType(str, Enum):
    STEP = "STEP"
    FATIGUE = "FATIGUE"

class GuardrailConfig(BaseModel):
    app_id: str
    input_prompt: str
    use_customize_white: bool = False
    use_customize_words: bool = False
    use_customize_rule: bool = False
    use_vip_black: bool = False
    use_vip_white: bool = False

class StepLoadConfig(BaseModel):
    initial_users: int = Field(1, ge=1)
    step_size: int = Field(1, ge=1)
    step_duration: int = Field(10, ge=5, description="Duration of each step in seconds")
    max_users: int = Field(50, ge=1)

class FatigueLoadConfig(BaseModel):
    concurrency: int = Field(10, ge=1)
    duration: int = Field(60, ge=10, description="Total duration in seconds")

class PerformanceTestStartRequest(BaseModel):
    test_type: TestType
    target_config: GuardrailConfig
    step_config: Optional[StepLoadConfig] = None
    fatigue_config: Optional[FatigueLoadConfig] = None

class PerformanceStatusResponse(BaseModel):
    is_running: bool
    duration: int = 0
    current_users: int = 0
    total_requests: int = 0
    success_requests: int = 0
    error_requests: int = 0
    current_rps: float = 0.0
    avg_latency: float = 0.0
    p95_latency: float = 0.0
    p99_latency: float = 0.0
    history: List[Dict[str, Any]] = [] # Time-series data points
    error: Optional[str] = None

class PerformanceHistoryMeta(BaseModel):
    test_id: str
    start_time: str
    end_time: str
    duration: int
    test_type: str
    app_id: str
    status: str # COMPLETED, STOPPED, FAILED

class PerformanceAnalysis(BaseModel):
    score: int = 100
    conclusion: str
    suggestions: List[str] = []

class PerformanceHistoryDetail(BaseModel):
    meta: PerformanceHistoryMeta
    config: Dict[str, Any]
    stats: Dict[str, Any]
    history: List[Dict[str, Any]]
    analysis: Optional[PerformanceAnalysis] = None
