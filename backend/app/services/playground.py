import httpx
import uuid
import secrets
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.playground_history import PlaygroundHistoryRepository
from app.schemas.playground import PlaygroundInputRequest

GUARDRAIL_SERVICE_URL = "http://127.0.0.1:8000/api/input/instance/rule/run"

class PlaygroundService:
    def __init__(self, db: AsyncSession):
        self.history_repo = PlaygroundHistoryRepository(db)

    async def run_input_check(self, payload: PlaygroundInputRequest) -> Dict[str, Any]:
        request_id = str(uuid.uuid4())
        random_apikey = f"sk-{secrets.token_hex(16)}"
        
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
