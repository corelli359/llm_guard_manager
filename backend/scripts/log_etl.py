#!/usr/bin/env python3
"""
日志加工脚本：将围栏服务的 audit.log / request.log 展平为统一的 JSONL 格式。
按 app_id 分目录、按日期分文件输出。

用法:
    python log_etl.py --input /path/to/audit.log --type audit --output ./processed/
    python log_etl.py --input /path/to/request.log --type request --output ./processed/
    python log_etl.py --input /path/to/logs/ --type auto --output ./processed/
"""

import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# audit.log 行格式: "2026-01-19 15:29:59,123 - audit:on_response - INFO - {JSON}"
AUDIT_LINE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}),?\d*\s+-\s+\S+\s+-\s+\w+\s+-\s+(.+)$")

LABEL_MAP = {0: "pass", 50: "rewrite", 100: "block", 1000: "review"}


def extract_decisions(all_decision_dict: dict) -> tuple:
    """从 all_decision_dict 提取 hit_tags, hit_words, decisions 列表"""
    hit_tags, hit_words, decisions = [], [], []
    if not all_decision_dict:
        return hit_tags, hit_words, decisions
    for score_group in all_decision_dict.values():
        if not isinstance(score_group, dict):
            continue
        for tag, detail in score_group.items():
            if not isinstance(detail, dict):
                continue
            words = detail.get("words", [])
            hit_tags.append(tag)
            hit_words.extend(words)
            decisions.append({"tag": tag, "decision": detail.get("decision"), "words": words})
    return hit_tags, list(set(hit_words)), decisions


def flatten_audit_log(raw: dict) -> dict:
    """展平 audit.log 的嵌套结构"""
    req = raw.get("request", {}) or {}
    resp = raw.get("response", {}) or {}
    fd = resp.get("final_decision", {}) or {}
    all_dec = resp.get("all_decision_dict", {}) or {}
    score = fd.get("score", 0)
    hit_tags, hit_words, decisions = extract_decisions(all_dec)

    return {
        "request_id": raw.get("request_id"),
        "biz_request_id": req.get("request_id"),
        "app_id": req.get("app_id"),
        "apikey": req.get("apikey"),
        "input_prompt": req.get("input_prompt"),
        "original_input_prompt": None,
        "is_output": None,
        "use_customize_white": req.get("use_customize_white"),
        "use_customize_words": req.get("use_customize_words"),
        "use_customize_rule": req.get("use_customize_rule"),
        "use_vip_black": req.get("use_vip_black"),
        "use_vip_white": req.get("use_vip_white"),
        "http_status": raw.get("status"),
        "latency_ms": raw.get("latency_ms"),
        "client_ip": raw.get("client_ip"),
        "endpoint": raw.get("path"),
        "score": score,
        "priority": fd.get("priority", -1),
        "decision_label": LABEL_MAP.get(score, "error" if raw.get("status") == 500 else "unknown"),
        "safety": None,
        "category": None,
        "hit_tags": hit_tags,
        "hit_words": hit_words,
        "decisions": decisions,
        "decision_dict": None,
        "global_result": None,
        "customize_result": None,
        "vip_black_words_result": None,
        "vip_white_words_result": None,
        "rewrite_result": None,
        "final_result": None,
        "exemption_set": None,
        "exemption_distance": None,
        "timestamp": raw.get("timestamp"),
        "log_source": "audit_log",
    }


def flatten_request_log(raw: dict) -> dict:
    """展平 request.log（已基本扁平，补充衍生字段）"""
    fd = raw.get("final_decision", {}) or {}
    all_dec = raw.get("all_decision_dict", {}) or {}
    score = fd.get("score", 0)
    hit_tags, hit_words, decisions = extract_decisions(all_dec)

    return {
        "request_id": raw.get("request_id"),
        "biz_request_id": None,
        "app_id": raw.get("app_id"),
        "apikey": None,
        "input_prompt": raw.get("input_prompt"),
        "original_input_prompt": raw.get("original_input_prompt"),
        "is_output": raw.get("is_output"),
        "use_customize_white": raw.get("use_customize_white"),
        "use_customize_words": raw.get("use_customize_words"),
        "use_customize_rule": raw.get("use_customize_rule"),
        "use_vip_black": raw.get("use_vip_black"),
        "use_vip_white": raw.get("use_vip_white"),
        "http_status": None,
        "latency_ms": raw.get("latency_ms"),
        "client_ip": None,
        "endpoint": raw.get("endpoint"),
        "score": score,
        "priority": fd.get("priority", -1),
        "decision_label": LABEL_MAP.get(score, "unknown"),
        "safety": raw.get("safety"),
        "category": raw.get("category"),
        "hit_tags": hit_tags,
        "hit_words": hit_words,
        "decisions": decisions,
        "decision_dict": raw.get("decision_dict"),
        "global_result": raw.get("global_result"),
        "customize_result": raw.get("customize_result"),
        "vip_black_words_result": raw.get("vip_black_words_result"),
        "vip_white_words_result": raw.get("vip_white_words_result"),
        "rewrite_result": raw.get("rewrite_result"),
        "final_result": raw.get("final_result"),
        "exemption_set": raw.get("exemption_set"),
        "exemption_distance": raw.get("exemption_distance"),
        "timestamp": raw.get("timestamp"),
        "log_source": "request_log",
    }


def parse_audit_line(line: str) -> dict | None:
    """解析 audit.log 的一行，提取 JSON 部分"""
    line = line.strip()
    if not line:
        return None
    m = AUDIT_LINE_RE.match(line)
    if m:
        json_str = m.group(2)
    else:
        # 尝试直接解析为 JSON（可能是纯 JSON 格式的日志）
        json_str = line
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def parse_request_line(line: str) -> dict | None:
    """解析 request.log 的一行（每行是纯 JSON）"""
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def extract_date(timestamp: str) -> str:
    """从 timestamp 提取日期部分 yyyy-MM-dd"""
    if not timestamp:
        return "unknown"
    return timestamp[:10]


def detect_log_type(filepath: Path) -> str:
    """自动检测日志类型：audit 或 request"""
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if AUDIT_LINE_RE.match(line):
                return "audit"
            try:
                data = json.loads(line)
                if "request" in data and "response" in data:
                    return "audit"
                return "request"
            except json.JSONDecodeError:
                continue
    return "audit"


def process_file(filepath: Path, log_type: str, output_dir: Path, seen_ids: set) -> dict:
    """处理单个日志文件，返回统计信息"""
    stats = {"total": 0, "processed": 0, "skipped_dup": 0, "skipped_err": 0}
    # 按 (app_id, date) 分组缓存
    buffers: dict[tuple, list] = defaultdict(list)

    parse_fn = parse_audit_line if log_type == "audit" else parse_request_line
    flatten_fn = flatten_audit_log if log_type == "audit" else flatten_request_log

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stats["total"] += 1
            raw = parse_fn(line)
            if raw is None:
                stats["skipped_err"] += 1
                continue

            flat = flatten_fn(raw)
            rid = flat.get("request_id")
            if rid and rid in seen_ids:
                stats["skipped_dup"] += 1
                continue
            if rid:
                seen_ids.add(rid)

            app_id = flat.get("app_id") or "unknown"
            date_str = extract_date(flat.get("timestamp"))
            buffers[(app_id, date_str)].append(flat)
            stats["processed"] += 1

    # 写入文件
    for (app_id, date_str), records in buffers.items():
        app_dir = output_dir / app_id
        app_dir.mkdir(parents=True, exist_ok=True)
        out_file = app_dir / f"{date_str}.jsonl"
        with open(out_file, "a", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return stats


def main():
    parser = argparse.ArgumentParser(description="日志加工脚本：展平 audit.log / request.log 为 JSONL")
    parser.add_argument("--input", "-i", required=True, help="输入文件或目录路径")
    parser.add_argument("--type", "-t", choices=["audit", "request", "auto"], default="auto",
                        help="日志类型（默认 auto 自动检测）")
    parser.add_argument("--output", "-o", required=True, help="输出目录路径")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    seen_ids: set = set()
    total_stats = {"total": 0, "processed": 0, "skipped_dup": 0, "skipped_err": 0}

    # 收集要处理的文件
    if input_path.is_file():
        files = [input_path]
    elif input_path.is_dir():
        files = sorted(input_path.glob("*.log"))
        if not files:
            logger.error(f"目录 {input_path} 下没有 .log 文件")
            sys.exit(1)
    else:
        logger.error(f"路径不存在: {input_path}")
        sys.exit(1)

    for filepath in files:
        log_type = args.type
        if log_type == "auto":
            log_type = detect_log_type(filepath)
            logger.info(f"自动检测 {filepath.name} 类型: {log_type}")

        logger.info(f"处理文件: {filepath} (类型: {log_type})")
        stats = process_file(filepath, log_type, output_dir, seen_ids)
        for k in total_stats:
            total_stats[k] += stats[k]
        logger.info(f"  行数={stats['total']}, 处理={stats['processed']}, "
                     f"重复跳过={stats['skipped_dup']}, 解析失败={stats['skipped_err']}")

    logger.info(f"完成! 总计: 行数={total_stats['total']}, 处理={total_stats['processed']}, "
                f"重复跳过={total_stats['skipped_dup']}, 解析失败={total_stats['skipped_err']}")
    logger.info(f"输出目录: {output_dir}")


if __name__ == "__main__":
    main()
