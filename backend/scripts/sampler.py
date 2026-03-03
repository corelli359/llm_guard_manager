#!/usr/bin/env python3
"""
抽样工具：从加工后的 JSONL 中按 decision_label 分层随机抽样，输出 CSV 供人工标注。

用法:
    # 从 block/rewrite 各抽 50 条，pass 抽 50 条
    python sampler.py --input ./processed/ --output sample.csv

    # 指定抽样数量
    python sampler.py --input ./processed/ --block-n 100 --pass-n 100 --output sample.csv

    # 按场景和日期过滤
    python sampler.py --input ./processed/ --app-id test_002 \
        --date-start 2026-02-01 --date-end 2026-02-28 --output sample.csv
"""

import argparse
import csv
import json
import logging
import random
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# CSV 输出字段（供标注人员使用）
CSV_FIELDS = [
    "request_id", "app_id", "timestamp", "decision_label",
    "input_prompt", "hit_tags", "hit_words", "score",
    # 标注列（人工填写）
    "is_correct",       # 1=判断正确, 0=判断错误
    "annotator_note",   # 备注
]


def load_records(input_dir: str, app_id: str = None,
                 date_start: str = None, date_end: str = None) -> list[dict]:
    records = []
    base = Path(input_dir)
    app_dirs = [base / app_id] if app_id else [d for d in base.iterdir() if d.is_dir()]
    for app_dir in app_dirs:
        if not app_dir.is_dir():
            continue
        for jsonl_file in sorted(app_dir.glob("*.jsonl")):
            date_str = jsonl_file.stem
            if date_start and date_str < date_start:
                continue
            if date_end and date_str > date_end:
                continue
            with open(jsonl_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
    return records


def sample_records(records: list[dict], block_n: int, pass_n: int,
                   rewrite_n: int, seed: int) -> list[dict]:
    """分层随机抽样"""
    random.seed(seed)
    groups: dict[str, list] = {"block": [], "rewrite": [], "pass": [], "review": []}
    for r in records:
        label = r.get("decision_label", "unknown")
        if label in groups:
            groups[label].append(r)

    sampled = []
    for label, n in [("block", block_n), ("rewrite", rewrite_n), ("pass", pass_n)]:
        pool = groups[label]
        k = min(n, len(pool))
        sampled.extend(random.sample(pool, k))
        logger.info(f"  {label}: 池={len(pool)}, 抽取={k}")

    random.shuffle(sampled)
    return sampled


def write_csv(records: list[dict], output_path: str):
    """写出 CSV 文件"""
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            row = {
                "request_id": r.get("request_id", ""),
                "app_id": r.get("app_id", ""),
                "timestamp": r.get("timestamp", ""),
                "decision_label": r.get("decision_label", ""),
                "input_prompt": r.get("input_prompt", ""),
                "hit_tags": "|".join(r.get("hit_tags", [])),
                "hit_words": "|".join(r.get("hit_words", [])),
                "score": r.get("score", ""),
                "is_correct": "",
                "annotator_note": "",
            }
            writer.writerow(row)
    logger.info(f"已输出 {len(records)} 条抽样记录到: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="分层随机抽样工具（供人工标注）")
    parser.add_argument("--input", "-i", required=True, help="加工后的 JSONL 目录")
    parser.add_argument("--output", "-o", required=True, help="输出 CSV 文件路径")
    parser.add_argument("--app-id", default=None, help="按场景过滤")
    parser.add_argument("--date-start", default=None, help="开始日期 yyyy-MM-dd")
    parser.add_argument("--date-end", default=None, help="结束日期 yyyy-MM-dd")
    parser.add_argument("--block-n", type=int, default=50, help="block 抽样数量（默认50）")
    parser.add_argument("--rewrite-n", type=int, default=50, help="rewrite 抽样数量（默认50）")
    parser.add_argument("--pass-n", type=int, default=50, help="pass 抽样数量（默认50）")
    parser.add_argument("--seed", type=int, default=42, help="随机种子（默认42，保证可复现）")
    args = parser.parse_args()

    logger.info(f"加载数据: dir={args.input}, app_id={args.app_id}")
    records = load_records(args.input, args.app_id, args.date_start, args.date_end)
    logger.info(f"加载 {len(records)} 条记录")

    if not records:
        logger.warning("没有数据，退出")
        sys.exit(0)

    logger.info(f"开始抽样: block={args.block_n}, rewrite={args.rewrite_n}, pass={args.pass_n}")
    sampled = sample_records(records, args.block_n, args.pass_n, args.rewrite_n, args.seed)

    write_csv(sampled, args.output)


if __name__ == "__main__":
    main()
