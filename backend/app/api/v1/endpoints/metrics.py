"""
安全运营指标 API：日志加工 + 指标查询
"""
import sys
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from app.core.config import settings

# 将 scripts 目录加入 sys.path，以便 import log_etl / metrics_calculator
_scripts_dir = str(Path(__file__).resolve().parents[4] / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

import log_etl
import metrics_calculator

router = APIRouter()


@router.get("/apps")
async def list_metric_apps():
    """列出已有加工数据的场景（app_id 列表）"""
    processed = Path(settings.METRICS_PROCESSED_DIR)
    if not processed.exists():
        return {"apps": []}
    apps = sorted([d.name for d in processed.iterdir() if d.is_dir()])
    return {"apps": apps}


@router.post("/etl")
async def run_etl(
    log_dir: Optional[str] = None,
    log_type: str = Query("auto", regex="^(audit|request|auto)$"),
    full: bool = Query(False, description="全量模式（忽略增量 checkpoint）"),
):
    """触发日志加工（ETL），增量处理新增日志"""
    input_dir = Path(log_dir or settings.METRICS_LOG_DIR)
    output_dir = Path(settings.METRICS_PROCESSED_DIR)

    if not input_dir.exists():
        raise HTTPException(400, f"日志目录不存在: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(input_dir.glob("*.log"))
    if not files:
        raise HTTPException(400, f"目录下没有 .log 文件: {input_dir}")

    # 加载 checkpoint（增量模式）
    if full:
        checkpoint = {"files": {}, "seen_ids": []}
    else:
        checkpoint = log_etl.load_checkpoint(output_dir)

    seen_ids: set = set(checkpoint["seen_ids"])
    total_stats = {"total": 0, "processed": 0, "skipped_dup": 0, "skipped_err": 0, "skipped_unchanged": 0}

    for filepath in files:
        offset = 0 if full else log_etl.get_file_offset(checkpoint, filepath)
        if offset == -1:
            total_stats["skipped_unchanged"] += 1
            continue

        lt = log_type
        if lt == "auto":
            lt = log_etl.detect_log_type(filepath)
        stats, end_offset = log_etl.process_file(filepath, lt, output_dir, seen_ids, offset)
        for k in ("total", "processed", "skipped_dup", "skipped_err"):
            total_stats[k] += stats[k]

        checkpoint["files"][str(filepath)] = {
            "offset": end_offset,
            "size": filepath.stat().st_size,
        }

    # 保存 checkpoint
    checkpoint["seen_ids"] = list(seen_ids)
    log_etl.save_checkpoint(output_dir, checkpoint)

    return {
        "message": "日志加工完成",
        "mode": "全量" if full else "增量",
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "stats": total_stats,
    }


@router.get("/overview")
async def get_overview(
    app_id: Optional[str] = None,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
):
    """指标概览：请求分布 + 时延 + 趋势"""
    records = metrics_calculator.load_records(
        settings.METRICS_PROCESSED_DIR, app_id, date_start, date_end
    )
    if not records:
        return {"total_requests": 0, "summary": {}, "latency": {}, "trend": []}

    result = metrics_calculator.calculate_metrics(records)
    return {
        "total_requests": result["total_requests"],
        "summary": result["summary"],
        "latency": result["latency"],
        "trend": result["trend"],
    }


@router.get("/risk-distribution")
async def get_risk_distribution(
    app_id: Optional[str] = None,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
):
    """风险事件分布：标签分布 + 敏感词 TOP"""
    records = metrics_calculator.load_records(
        settings.METRICS_PROCESSED_DIR, app_id, date_start, date_end
    )
    if not records:
        return {"tag_distribution": [], "top_hit_words": [], "unique_hit_words_count": 0}

    result = metrics_calculator.calculate_metrics(records)
    return result["risk_distribution"]


@router.get("/rule-quality")
async def get_rule_quality(
    app_id: Optional[str] = None,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
):
    """规则质量：命中分布 + 贡献度"""
    records = metrics_calculator.load_records(
        settings.METRICS_PROCESSED_DIR, app_id, date_start, date_end
    )
    if not records:
        return {"rule_hit_distribution": [], "top_contributing_words": []}

    result = metrics_calculator.calculate_metrics(records)
    return result["rule_quality"]


@router.get("/log-files")
async def list_log_files(log_dir: Optional[str] = None):
    """列出日志目录下的文件（供前端选择）"""
    input_dir = Path(log_dir or settings.METRICS_LOG_DIR)
    if not input_dir.exists():
        return {"files": [], "dir": str(input_dir), "exists": False}

    files = []
    for f in sorted(input_dir.glob("*.log")):
        files.append({
            "name": f.name,
            "size_mb": round(f.stat().st_size / 1024 / 1024, 2),
        })
    return {"files": files, "dir": str(input_dir), "exists": True}
