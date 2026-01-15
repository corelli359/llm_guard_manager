import asyncio
import time
import httpx
import uuid
import secrets
import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.schemas.performance import PerformanceTestStartRequest, TestType, GuardrailConfig, PerformanceHistoryMeta, PerformanceHistoryDetail

GUARDRAIL_SERVICE_URL = "http://127.0.0.1:8000/api/input/instance/rule/run"
HISTORY_DIR = "performance_history"

class LoadRunner:
    def __init__(self):
        self.running = False
        self.stop_event = asyncio.Event()
        self.start_time = 0.0
        self.end_time = 0.0
        self.stats = self._init_stats()
        self.history_buffer = []
        self._target_config: Optional[GuardrailConfig] = None
        self._test_config: Optional[PerformanceTestStartRequest] = None
        self.current_users = 0
        self.test_id = None
        
        # Tracking last valid metrics
        self.last_rps = 0.0
        self.last_error_rps = 0.0
        
        if not os.path.exists(HISTORY_DIR):
            os.makedirs(HISTORY_DIR)

    def _init_stats(self):
        return {
            "total": 0,
            "success": 0,
            "error": 0,
            "latency_sum": 0.0,
            "latency_count": 0, # Only for success
            "start_ts": time.time(),
            "window_requests": 0,
            "window_errors": 0, # Added for Error RPS
            "window_start": time.time()
        }

    async def dry_run(self, config: GuardrailConfig) -> Dict[str, Any]:
        """Execute a single request to verify connectivity and config."""
        payload = self._build_payload(config)
        start = time.time()
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(GUARDRAIL_SERVICE_URL, json=payload, timeout=10.0)
                resp.raise_for_status()
                data = resp.json()
                latency = int((time.time() - start) * 1000)
                return {"success": True, "latency": latency, "data": data}
            except Exception as e:
                latency = int((time.time() - start) * 1000)
                return {"success": False, "latency": latency, "error": str(e)}

    def _build_payload(self, config: GuardrailConfig) -> Dict[str, Any]:
        return {
            "request_id": str(uuid.uuid4()),
            "app_id": config.app_id,
            "apikey": f"perf-test-{secrets.token_hex(4)}",
            "input_prompt": config.input_prompt,
            "use_customize_white": config.use_customize_white,
            "use_customize_words": config.use_customize_words,
            "use_customize_rule": config.use_customize_rule,
            "use_vip_black": config.use_vip_black,
            "use_vip_white": config.use_vip_white,
        }

    async def start_test(self, request: PerformanceTestStartRequest):
        if self.running:
            return

        self.running = True
        self.stop_event.clear()
        self.stats = self._init_stats()
        self.history_buffer = []
        self._target_config = request.target_config
        self._test_config = request
        self.start_time = time.time()
        self.end_time = 0.0
        self.current_users = 0
        self.test_id = str(uuid.uuid4())
        self.last_rps = 0.0
        self.last_error_rps = 0.0

        try:
            if request.test_type == TestType.FATIGUE:
                if request.fatigue_config:
                    await self._run_fatigue(request.fatigue_config.concurrency, request.fatigue_config.duration)
            elif request.test_type == TestType.STEP:
                if request.step_config:
                    await self._run_step(
                        request.step_config.initial_users,
                        request.step_config.step_size,
                        request.step_config.step_duration,
                        request.step_config.max_users
                    )
        except Exception as e:
            print(f"Test execution error: {e}")
        finally:
            self.running = False
            self.end_time = time.time()
            self.stop_event.set()
            self._snapshot_history(time.time(), self.last_rps, self.last_error_rps)
            self._save_history()
            self.current_users = 0

    async def stop(self):
        self.running = False
        self.end_time = time.time()
        self.stop_event.set()

    def get_status(self):
        now = time.time()
        if self.running:
            duration = int(now - self.start_time)
        elif self.end_time > 0:
            duration = int(self.end_time - self.start_time)
        else:
            duration = 0
        
        window_duration = now - self.stats["window_start"]
        
        rps = self.last_rps
        error_rps = self.last_error_rps
        
        if window_duration >= 1.0:
            rps = self.stats["window_requests"] / window_duration
            error_rps = self.stats["window_errors"] / window_duration
            
            self.last_rps = rps
            self.last_error_rps = error_rps
            
            self._snapshot_history(now, rps, error_rps)
            self.stats["window_start"] = now
            self.stats["window_requests"] = 0
            self.stats["window_errors"] = 0
        
        avg_lat = 0.0
        # Only use successful latency count
        if self.stats["latency_count"] > 0:
            avg_lat = (self.stats["latency_sum"] / self.stats["latency_count"]) * 1000

        return {
            "is_running": self.running,
            "duration": duration,
            "current_users": self.current_users,
            "total_requests": self.stats["total"],
            "success_requests": self.stats["success"],
            "error_requests": self.stats["error"],
            "current_rps": round(rps, 2),
            "avg_latency": round(avg_lat, 2),
            "history": self.history_buffer[-60:]
        }

    def _snapshot_history(self, timestamp, rps, error_rps):
        avg_lat = 0.0
        if self.stats["latency_count"] > 0:
            avg_lat = (self.stats["latency_sum"] / self.stats["latency_count"]) * 1000

        point = {
            "timestamp": int(timestamp),
            "rps": round(rps, 2),
            "error_rps": round(error_rps, 2), # New field
            "latency": round(avg_lat, 2),
            "users": self.current_users
        }
        self.history_buffer.append(point)

    async def _worker(self):
        async with httpx.AsyncClient() as client:
            while not self.stop_event.is_set() and self.running:
                payload = self._build_payload(self._target_config)
                start = time.time()
                try:
                    resp = await client.post(GUARDRAIL_SERVICE_URL, json=payload, timeout=10.0)
                    duration = time.time() - start
                    
                    self.stats["total"] += 1
                    self.stats["window_requests"] += 1
                    
                    if resp.status_code == 200:
                        self.stats["success"] += 1
                        # Only add latency for success
                        self.stats["latency_sum"] += duration
                        self.stats["latency_count"] += 1
                    else:
                        self.stats["error"] += 1
                        self.stats["window_errors"] += 1
                        
                except Exception:
                    self.stats["total"] += 1
                    self.stats["window_requests"] += 1
                    self.stats["error"] += 1
                    self.stats["window_errors"] += 1
                
                await asyncio.sleep(0.01)

    async def _run_fatigue(self, concurrency: int, duration: int):
        self.current_users = concurrency
        workers = [asyncio.create_task(self._worker()) for _ in range(concurrency)]
        
        end_time = time.time() + duration
        while time.time() < end_time and not self.stop_event.is_set():
            await asyncio.sleep(1)
            
        self.stop_event.set()
        await asyncio.gather(*workers)

    async def _run_step(self, initial: int, step: int, duration: int, max_users: int):
        current = initial
        workers = []
        
        while current <= max_users and not self.stop_event.is_set():
            self.current_users = current
            new_workers_count = current - len(workers)
            for _ in range(new_workers_count):
                workers.append(asyncio.create_task(self._worker()))
            
            step_end = time.time() + duration
            while time.time() < step_end and not self.stop_event.is_set():
                await asyncio.sleep(1)
            
            if current >= max_users:
                break
            current += step
            
        self.stop_event.set()
        await asyncio.gather(*workers)

    def _save_history(self):
        if not self.test_id or not self._target_config:
            return

        test_dir = os.path.join(HISTORY_DIR, self.test_id)
        os.makedirs(test_dir, exist_ok=True)
        
        end_ts = self.end_time if self.end_time > 0 else time.time()
        duration = int(end_ts - self.start_time)
        status = "COMPLETED"

        meta = {
            "test_id": self.test_id,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(end_ts).isoformat(),
            "duration": duration,
            "test_type": self._test_config.test_type,
            "app_id": self._target_config.app_id,
            "status": status
        }
        with open(os.path.join(test_dir, "meta.json"), "w") as f:
            json.dump(meta, f, indent=2)

        config = self._test_config.model_dump()
        with open(os.path.join(test_dir, "config.json"), "w") as f:
            json.dump(config, f, indent=2)

        avg_latency = 0.0
        if self.stats["latency_count"] > 0:
            avg_latency = (self.stats["latency_sum"] / self.stats["latency_count"]) * 1000
        
        max_rps = 0.0
        if self.history_buffer:
            max_rps = max(p["rps"] for p in self.history_buffer)

        final_stats = {
            "total_requests": self.stats["total"],
            "success_requests": self.stats["success"],
            "error_requests": self.stats["error"],
            "avg_latency": round(avg_latency, 2),
            "max_rps": max_rps
        }
        with open(os.path.join(test_dir, "stats.json"), "w") as f:
            json.dump(final_stats, f, indent=2)

        with open(os.path.join(test_dir, "history.json"), "w") as f:
            json.dump(self.history_buffer, f)

    def get_history_list(self) -> List[PerformanceHistoryMeta]:
        results = []
        if not os.path.exists(HISTORY_DIR):
            return []
            
        for d in os.listdir(HISTORY_DIR):
            meta_path = os.path.join(HISTORY_DIR, d, "meta.json")
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r") as f:
                        data = json.load(f)
                        results.append(PerformanceHistoryMeta(**data))
                except Exception:
                    pass
        results.sort(key=lambda x: x.start_time, reverse=True)
        return results

    def get_history_detail(self, test_id: str) -> Optional[PerformanceHistoryDetail]:
        test_dir = os.path.join(HISTORY_DIR, test_id)
        if not os.path.exists(test_dir):
            return None
        
        try:
            with open(os.path.join(test_dir, "meta.json")) as f:
                meta = json.load(f)
            with open(os.path.join(test_dir, "config.json")) as f:
                config = json.load(f)
            with open(os.path.join(test_dir, "stats.json")) as f:
                stats = json.load(f)
            with open(os.path.join(test_dir, "history.json")) as f:
                history = json.load(f)
                
            return PerformanceHistoryDetail(
                meta=meta,
                config=config,
                stats=stats,
                history=history
            )
        except Exception as e:
            print(f"Error loading history: {e}")
            return None

    def delete_history(self, test_id: str):
        test_dir = os.path.join(HISTORY_DIR, test_id)
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

# Global Instance
runner_instance = LoadRunner()