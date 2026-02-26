import httpx
import uuid
import secrets
import time
import random
import asyncio
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.playground_history import PlaygroundHistoryRepository
from app.schemas.playground import PlaygroundInputRequest

GUARDRAIL_SERVICE_URL = "http://127.0.0.1:8000/api/input/instance/rule/run"
#GUARDRAIL_SERVICE_URL = "http://llmsafe-guardrail-svc.llmsafe.svc:8000/api/input/instance/rule/run"

# ========== 演示 Mock 模式 ==========
# 设为 True 开启 mock，不调用真实围栏服务
DEMO_MOCK_MODE = True

def _build_mock_response(input_prompt: str) -> Dict[str, Any]:
    """根据输入文本返回 mock 围栏服务响应，结构与真实服务完全一致"""
    text = input_prompt.strip()

    # 示例1: "你大爷的" → 敏感词命中，拒答
    if "你大爷" in text and "做饭" not in text and "好吃" not in text:
        return {
            "final_decision": {"score": 100, "priority": 100},
            "all_decision_dict": {
                "100": {
                    "A.2.20-CONTROVERSIAL": {
                        "decision": 100,
                        "words": ["你大爷"]
                    }
                }
            },
            "guard_model_result": {
                "Safety": "CONTROVERSIAL",
                "Category": None
            },
            "hit_summary": {
                "triggered_by": "sensitive_words",
                "hit_tag": "A.2.20",
                "hit_words": ["CONTROVERSIAL"],
                "rule_key": "A.2.20-CONTROVERSIAL",
                "description": "命中全局敏感词(\"你大爷\",)，安全模型判定为CONTROVERSIAL，规则引擎判定为拒答。"
            }
        }

    # 示例2: "银行卡号" → 安全模型识别 PII，拒答
    if "银行卡" in text or "身份证" in text or "密码" in text:
        return {
            "final_decision": {"score": 100, "priority": 100},
            "all_decision_dict": {
                "100": {
                    "-UNSAFE": {
                        "decision": 100,
                        "words": []
                    }
                }
            },
            "guard_model_result": {
                "Safety": "UNSAFE",
                "Category": "pii"
            },
            "hit_summary": {
                "triggered_by": "guard_model",
                "hit_tag": "PII",
                "hit_words": [],
                "rule_key": "-UNSAFE",
                "description": "敏感词过滤未命中，安全模型判定为UNSAFE(PII)， 规则引擎判定为拒答。"
            }
        }

    # 默认: 通过
    return {
        "final_decision": {"score": 0, "priority": -1},
        "all_decision_dict": {},
        "sensitive_words_result": {
            "global_result": {},
            "customize_result": {},
            "vip_black_words_result": {},
            "vip_white_words_result": {},
            "final_result": {}
        },
        "guard_model_result": {
            "Safety": "SAFE",
            "Category": None
        },
        "hit_summary": {
            "triggered_by": None,
            "hit_tag": None,
            "hit_words": [],
            "rule_key": None,
            "description": "敏感词过滤未命中，安全模型判定为SAFE，规则引擎判定为通过。"
        }
    }
# ====================================

class PlaygroundService:
    def __init__(self, db: AsyncSession):
        self.history_repo = PlaygroundHistoryRepository(db)

    async def run_input_check(self, payload: PlaygroundInputRequest) -> Dict[str, Any]:
        request_id = str(uuid.uuid4())
        random_apikey = f"sk-{secrets.token_hex(16)}"
        start_time = time.time()

        # ===== Mock 模式 =====
        if DEMO_MOCK_MODE:
            # 模拟一个合理的上游延迟
            mock_delay = random.randint(80, 200) / 1000
            await asyncio.sleep(mock_delay)
            response_data = _build_mock_response(payload.input_prompt)

            return response_data
        # ===== Mock 模式结束 =====

        guard_payload = {
            "request_id": request_id,
            "app_id": payload.app_id,
            "apikey": random_apikey,
            "input_prompt": payload.input_prompt,
            "use_customize_white": payload.use_customize_white,
            "use_customize_words": payload.use_customize_words,
            "use_customize_rule": payload.use_customize_rule,
            "use_vip_black": payload.use_vip_black,
            "use_vip_white": payload.use_vip_white,
        }
        
        start_time = time.time()
        upstream_latency_ms = 0
        response_data = {}
        error_occurred = False
        error_detail = None
        
        # Call Guardrail Service
        async with httpx.AsyncClient() as client:
            try:
                upstream_start = time.time()
                response = await client.post(
                    GUARDRAIL_SERVICE_URL,
                    json=guard_payload,
                    timeout=10.0
                )
                upstream_end = time.time()
                upstream_latency_ms = int((upstream_end - upstream_start) * 1000)
                
                response.raise_for_status()
                response_data = response.json()
            except Exception as e:
                # Capture time even if it failed
                if upstream_latency_ms == 0:
                     upstream_end = time.time()
                     upstream_latency_ms = int((upstream_end - upstream_start) * 1000)

                error_occurred = True
                error_detail = str(e)
                if isinstance(e, httpx.HTTPStatusError):
                     try:
                        response_data = e.response.json()
                     except:
                        response_data = {"error": str(e), "body": e.response.text}
                else:
                     response_data = {"error": str(e)}

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        # Extract Score
        score = 0
        if error_occurred:
            score = -1
        elif "final_decision" in response_data and "score" in response_data["final_decision"]:
            score = response_data["final_decision"]["score"]
            
        # Save History
        history_data = {
            "id": str(uuid.uuid4()),
            "request_id": request_id,
            "playground_type": "INPUT",
            "app_id": payload.app_id,
            "input_data": {"input_prompt": payload.input_prompt},
            "config_snapshot": {
                "use_customize_white": payload.use_customize_white,
                "use_customize_words": payload.use_customize_words,
                "use_customize_rule": payload.use_customize_rule,
                "use_vip_black": payload.use_vip_black,
                "use_vip_white": payload.use_vip_white,
            },
            "output_data": response_data,
            "score": score,
            "latency": latency_ms,
            "upstream_latency": upstream_latency_ms
        }
        
        try:
            await self.history_repo.create(history_data)
        except Exception as db_err:
            # If DB save fails, we log it but don't stop the flow if possible, 
            # though usually we should alert.
            print(f"Failed to save history: {db_err}")

        # If it was an error, re-raise it so the controller can handle it (or return error dict)
        if error_occurred:
             # Depending on requirements, we can raise or return the error structure.
             # Controller usually expects a dict or raises HTTPException.
             # If we raise here, the controller turns it into 500/400.
             # But we successfully saved history. 
             # Let's raise to keep API contract standard.
             raise Exception(error_detail)
        
        return response_data

    async def get_history(
        self, 
        page: int, 
        size: int, 
        playground_type: Optional[str] = None, 
        app_id: Optional[str] = None
    ) -> List[Any]:
        skip = (page - 1) * size
        return await self.history_repo.get_history(skip, size, playground_type, app_id)
