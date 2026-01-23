import asyncio
import time
import httpx
import uuid
import secrets
import json
import os
import shutil
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.schemas.performance import PerformanceTestStartRequest, TestType, GuardrailConfig, PerformanceHistoryMeta, PerformanceHistoryDetail, PerformanceAnalysis

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
        self.last_p95 = 0.0
        self.last_p99 = 0.0
        
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
            "window_start": time.time(),
            "window_latencies": [] # For percentile calculation
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
        self.last_p95 = 0.0
        self.last_p99 = 0.0

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
            self._snapshot_history(time.time(), self.last_rps, self.last_error_rps, self.last_p95, self.last_p99)
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
        p95 = self.last_p95
        p99 = self.last_p99
        
        if window_duration >= 1.0:
            rps = self.stats["window_requests"] / window_duration
            error_rps = self.stats["window_errors"] / window_duration
            
            latencies = self.stats["window_latencies"]
            if latencies:
                p95 = np.percentile(latencies, 95)
                p99 = np.percentile(latencies, 99)
            else:
                p95 = 0.0
                p99 = 0.0

            self.last_rps = rps
            self.last_error_rps = error_rps
            self.last_p95 = p95
            self.last_p99 = p99
            
            self._snapshot_history(now, rps, error_rps, p95, p99)
            self.stats["window_start"] = now
            self.stats["window_requests"] = 0
            self.stats["window_errors"] = 0
            self.stats["window_latencies"] = [] # Reset window latencies
        
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
            "p95_latency": round(p95, 2),
            "p99_latency": round(p99, 2),
            "history": self.history_buffer[-60:]
        }

    def _snapshot_history(self, timestamp, rps, error_rps, p95, p99):
        avg_lat = 0.0
        if self.stats["latency_count"] > 0:
            avg_lat = (self.stats["latency_sum"] / self.stats["latency_count"]) * 1000

        point = {
            "timestamp": int(timestamp),
            "rps": round(rps, 2),
            "error_rps": round(error_rps, 2),
            "latency": round(avg_lat, 2),
            "p95_latency": round(p95, 2),
            "p99_latency": round(p99, 2),
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
                        self.stats["window_latencies"].append(duration * 1000) # Store in ms
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
        """
        Standard step load test with plateau at each level.
        Each step has two phases:
        1. Ramp-up: Gradually increase users to target level (20% of duration)
        2. Plateau: Maintain constant load to observe steady-state performance (80% of duration)
        """
        workers = []
        current = 0

        # Build list of target user counts for each stage
        stages = []
        target = initial
        while target <= max_users:
            stages.append(target)
            target += step

        # Execute each stage
        for stage_target in stages:
            if self.stop_event.is_set():
                break

            users_to_add = stage_target - current
            stage_start = time.time()

            # Phase 1: Ramp-up (20% of duration)
            # Add users gradually to avoid connection pool spike
            if users_to_add > 0:
                rampup_duration = duration * 0.2
                interval = rampup_duration / users_to_add if users_to_add > 0 else 0

                for i in range(users_to_add):
                    if self.stop_event.is_set():
                        break

                    # Create new worker
                    workers.append(asyncio.create_task(self._worker()))
                    current += 1
                    self.current_users = current

                    # Wait until next user creation time
                    next_user_time = stage_start + (i + 1) * interval
                    wait_time = next_user_time - time.time()
                    if wait_time > 0:
                        await asyncio.sleep(wait_time)

            # Phase 2: Plateau (80% of duration)
            # Maintain constant load to observe steady-state performance
            plateau_end = stage_start + duration
            remaining_time = plateau_end - time.time()
            if remaining_time > 0:
                while time.time() < plateau_end and not self.stop_event.is_set():
                    await asyncio.sleep(1)

        # Stop all workers
        self.stop_event.set()
        await asyncio.gather(*workers)

    def _analyze_results(self, stats: Dict[str, Any], history: List[Dict[str, Any]]) -> PerformanceAnalysis:
        if not history:
            return PerformanceAnalysis(score=0, conclusion="未收集到有效测试数据。", suggestions=["请检查网络连接或服务状态。"])

        max_users = max(h["users"] for h in history)
        max_rps = max(h["rps"] for h in history)
        
        # 提取所有点的 P99 延迟
        p99_values = [(h.get("p99_latency") or 0.0) for h in history]
        max_p99 = max(p99_values)
        avg_p99 = sum(p99_values) / len(p99_values) if p99_values else 0.0

        total_reqs = stats["total_requests"]
        error_reqs = stats["error_requests"]
        error_rate = (error_reqs / total_reqs) * 100 if total_reqs > 0 else 0

        score = 100
        suggestions = []
        
        # 1. 错误率分析
        if error_rate > 1.0:
            score -= 40
            suggestions.append(f"错误率过高: {error_rate:.2f}% 的请求失败。请立即检查服务端日志及错误堆栈。")
        elif error_rate > 0:
            score -= 10
            suggestions.append(f"存在少量错误: 观察到 {error_rate:.2f}% 的失败率，需排查偶发性问题。")
        
        # 2. 延迟峰值分析
        if max_p99 > 2000:
            score -= 30
            suggestions.append(f"严重延迟: P99 响应时间峰值达到 {max_p99:.0f}ms，超过 2秒，用户体验受损严重。")
        elif max_p99 > 1000:
            score -= 10
            suggestions.append(f"延迟较高: P99 响应时间峰值达到 {max_p99:.0f}ms，超过 1秒。")

        # 3. 毛刺 (Spike) 检测 / 抖动分析
        # 定义毛刺: 某时刻 P99 > 平均 P99 的 2 倍，且绝对值超过 50ms (忽略极低延迟下的波动)
        spike_count = sum(1 for v in p99_values if v > max(avg_p99 * 2, 50))
        if spike_count > 0:
            score -= 5 * min(spike_count, 4) # 最多扣 20 分
            suggestions.append(f"发现延迟毛刺: 检测到 {spike_count} 次明显的延迟激增现象，系统性能存在抖动。")

        # 4. 瓶颈检测 (仅针对阶梯测试)
        if self._test_config and self._test_config.test_type == TestType.STEP:
            # 简单启发式: 检查最后阶段 RPS 是否随用户数增加而线性增长
            # 取后 20% 的数据
            tail_len = max(1, len(history) // 5)
            tail_data = history[-tail_len:]
            if len(tail_data) > 1:
                users_growth = tail_data[-1]["users"] - tail_data[0]["users"]
                rps_growth = tail_data[-1]["rps"] - tail_data[0]["rps"]
                # 如果用户增加了但 RPS 没怎么涨 (甚至跌了)，且 RPS 本身已经有一定规模
                if users_growth > 0 and rps_growth <= 0 and tail_data[0]["rps"] > 10:
                     suggestions.append("疑似达到吞吐量瓶颈: 测试末期并发用户增加但 RPS 未增长，建议检查系统资源 (CPU/DB) 限制。")

        if score == 100:
            suggestions.append("完美表现: 系统在当前测试压力下运行极其稳定，无错误且延迟低。")
        elif score >= 90:
             suggestions.append("表现优秀: 系统性能整体稳定，各项指标在可接受范围内。")

        conclusion = (
            f"本次测试共模拟峰值 {max_users} 个虚拟用户。 "
            f"系统最大吞吐量达到 {max_rps:.1f} RPS。 "
            f"P99 延迟峰值为 {max_p99:.1f} ms，平均 P99 为 {avg_p99:.1f} ms。 "
            f"累计处理请求 {total_reqs} 个，其中失败 {error_reqs} 个。"
        )

        return PerformanceAnalysis(
            score=max(0, score),
            conclusion=conclusion,
            suggestions=suggestions
        )

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
            
        # Analysis
        analysis = self._analyze_results(final_stats, self.history_buffer)
        with open(os.path.join(test_dir, "analysis.json"), "w") as f:
            json.dump(analysis.model_dump(), f, indent=2)

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
            
            analysis = None
            analysis_path = os.path.join(test_dir, "analysis.json")
            if os.path.exists(analysis_path):
                with open(analysis_path) as f:
                    analysis = json.load(f)
                
            return PerformanceHistoryDetail(
                meta=meta,
                config=config,
                stats=stats,
                history=history,
                analysis=analysis
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