#!/usr/bin/env python3
"""
指标计算脚本：基于加工后的 JSONL 文件计算安全运营指标。

指标1: 整体请求处理分布（通过率/改写率/阻断率）
指标3: 风险事件分布（标签分布/敏感词TOP/命中率）
指标4: 处理时延（avg/P50/P95/P99）
指标5: 规则与策略质量（命中分布/贡献度/零命中规则）

用法:
    python metrics_calculator.py --input ./processed/
    python metrics_calculator.py --input ./processed/ --app-id test_002
    python metrics_calculator.py --input ./processed/ --date-start 2026-01-01 --date-end 2026-01-31
    python metrics_calculator.py --input ./processed/ --sync-db --db-url "mysql+pymysql://root:xxx@127.0.0.1:38306/llm_safe_db"
"""

import argparse
import json
import logging
import sys
import uuid
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ============================================================
# 数据加载
# ============================================================

def load_records(input_dir: str, app_id: str = None,
                 date_start: str = None, date_end: str = None) -> list[dict]:
    """加载 JSONL 记录，支持按 app_id 和日期范围过滤"""
    records = []
    base = Path(input_dir)
    if not base.exists():
        logger.error(f"输入目录不存在: {input_dir}")
        return records

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


# ============================================================
# 指标计算
# ============================================================

def _percentile(sorted_list: list, pct: float) -> float:
    """计算分位数（避免依赖 numpy）"""
    if not sorted_list:
        return 0.0
    k = (len(sorted_list) - 1) * pct / 100.0
    f = int(k)
    c = f + 1
    if c >= len(sorted_list):
        return sorted_list[f]
    return sorted_list[f] + (k - f) * (sorted_list[c] - sorted_list[f])


def _pct(count: int, total: int) -> float:
    return round(count / total * 100, 2) if total else 0.0


def _extract_tag_code(rule_name: str) -> str:
    """从规则名提取标签编码: 'A.2.20-UNSAFE' -> 'A.2.20', 'A.1.9-CONTROVERSIAL' -> 'A.1.9'"""
    # 规则格式: {标签编码}-{安全等级}，标签编码是 A.x.y 格式
    parts = rule_name.rsplit("-", 1)
    return parts[0] if len(parts) == 2 else rule_name


def calculate_metrics(records: list[dict]) -> dict:
    """计算全部指标，返回结构化结果"""
    total = len(records)
    if total == 0:
        return {"total_requests": 0}

    # 指标1: 请求分布
    label_counts = Counter()
    # 指标3: 风险事件
    tag_counter = Counter()
    word_counter = Counter()
    unique_hit_words = set()
    # 指标4: 时延
    latencies = []
    # 指标5: 规则命中
    rule_hit_counter = Counter()
    # 按日期聚合（趋势数据）
    daily: dict[str, dict] = {}

    for r in records:
        label = r.get("decision_label", "unknown")
        label_counts[label] += 1

        for raw_tag in r.get("hit_tags", []):
            tag_code = _extract_tag_code(raw_tag)
            tag_counter[tag_code] += 1
            rule_hit_counter[raw_tag] += 1
        for word in r.get("hit_words", []):
            word_counter[word] += 1
            unique_hit_words.add(word)

        lat = r.get("latency_ms")
        if lat is not None:
            latencies.append(float(lat))

        # 按日期聚合
        ts = r.get("timestamp", "")
        day = ts[:10] if ts else "unknown"
        if day not in daily:
            daily[day] = {"total": 0, "pass": 0, "rewrite": 0, "block": 0, "latencies": []}
        daily[day]["total"] += 1
        if label in ("pass", "rewrite", "block"):
            daily[day][label] += 1
        if lat is not None:
            daily[day]["latencies"].append(float(lat))

    latencies.sort()

    # 构建趋势
    trend = []
    for day in sorted(daily.keys()):
        d = daily[day]
        dt = d["total"] or 1
        dl = sorted(d["latencies"])
        trend.append({
            "date": day,
            "total": d["total"],
            "passRate": _pct(d["pass"], dt),
            "rewriteRate": _pct(d["rewrite"], dt),
            "blockRate": _pct(d["block"], dt),
            "avgMs": round(sum(dl) / len(dl), 2) if dl else None,
            "p95Ms": round(_percentile(dl, 95), 2) if dl else None,
            "p99Ms": round(_percentile(dl, 99), 2) if dl else None,
        })

    # 规则贡献度
    total_rule_hits = sum(rule_hit_counter.values()) or 1
    total_word_hits = sum(word_counter.values()) or 1

    return {
        "total_requests": total,
        # 指标1
        "summary": {
            "total_requests": total,
            "pass_count": label_counts.get("pass", 0),
            "rewrite_count": label_counts.get("rewrite", 0),
            "block_count": label_counts.get("block", 0),
            "review_count": label_counts.get("review", 0),
            "error_count": label_counts.get("error", 0),
            "pass_rate": _pct(label_counts.get("pass", 0), total),
            "rewrite_rate": _pct(label_counts.get("rewrite", 0), total),
            "block_rate": _pct(label_counts.get("block", 0), total),
            "review_rate": _pct(label_counts.get("review", 0), total),
            "error_rate": _pct(label_counts.get("error", 0), total),
        },
        # 指标3
        "risk_distribution": {
            "tag_distribution": [
                {"tag": tag, "count": cnt, "percentage": _pct(cnt, total)}
                for tag, cnt in tag_counter.most_common()
            ],
            "top_hit_words": [
                {"word": w, "count": cnt}
                for w, cnt in word_counter.most_common(20)
            ],
            "unique_hit_words_count": len(unique_hit_words),
        },
        # 指标4
        "latency": {
            "avg_ms": round(sum(latencies) / len(latencies), 2) if latencies else None,
            "p50_ms": round(_percentile(latencies, 50), 2) if latencies else None,
            "p95_ms": round(_percentile(latencies, 95), 2) if latencies else None,
            "p99_ms": round(_percentile(latencies, 99), 2) if latencies else None,
            "sample_count": len(latencies),
        },
        # 指标5
        "rule_quality": {
            "rule_hit_distribution": [
                {"tag": tag, "count": cnt, "contribution_pct": round(cnt / total_rule_hits * 100, 2)}
                for tag, cnt in rule_hit_counter.most_common()
            ],
            "top_contributing_words": [
                {"word": w, "count": cnt, "contribution_pct": round(cnt / total_word_hits * 100, 2)}
                for w, cnt in word_counter.most_common(10)
            ],
        },
        "trend": trend,
    }


# ============================================================
# 数据库同步（--sync-db）
# ============================================================

def sync_to_db(metrics: dict, app_id: str, snapshot_date: str, db_url: str):
    """将指标结果写入 MySQL"""
    try:
        import pymysql
        from urllib.parse import urlparse
    except ImportError:
        logger.error("需要安装 pymysql: pip install pymysql")
        sys.exit(1)

    parsed = urlparse(db_url.replace("mysql+pymysql://", "mysql://"))
    conn = pymysql.connect(
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip("/"),
        charset="utf8mb4",
    )

    try:
        with conn.cursor() as cur:
            _ensure_tables(cur)

            s = metrics["summary"]
            lat = metrics["latency"]
            sid = str(uuid.uuid4())

            # 写入 metrics_snapshot
            cur.execute("""
                INSERT INTO metrics_snapshot
                    (id, app_id, snapshot_date, total_requests,
                     pass_count, rewrite_count, block_count, review_count, error_count,
                     avg_latency_ms, p50_latency_ms, p95_latency_ms, p99_latency_ms)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    total_requests=VALUES(total_requests),
                    pass_count=VALUES(pass_count), rewrite_count=VALUES(rewrite_count),
                    block_count=VALUES(block_count), review_count=VALUES(review_count),
                    error_count=VALUES(error_count),
                    avg_latency_ms=VALUES(avg_latency_ms), p50_latency_ms=VALUES(p50_latency_ms),
                    p95_latency_ms=VALUES(p95_latency_ms), p99_latency_ms=VALUES(p99_latency_ms)
            """, (sid, app_id, snapshot_date, s["total_requests"],
                  s["pass_count"], s["rewrite_count"], s["block_count"],
                  s["review_count"], s["error_count"],
                  lat["avg_ms"], lat["p50_ms"], lat["p95_ms"], lat["p99_ms"]))

            # 写入 metrics_tag_stats
            for item in metrics["rule_quality"]["rule_hit_distribution"]:
                cur.execute("""
                    INSERT INTO metrics_tag_stats
                        (id, app_id, snapshot_date, tag_code, hit_count, contribution_pct)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        hit_count=VALUES(hit_count), contribution_pct=VALUES(contribution_pct)
                """, (str(uuid.uuid4()), app_id, snapshot_date,
                      item["tag"], item["count"], item["contribution_pct"]))

            # 写入 metrics_word_stats
            for item in metrics["risk_distribution"]["top_hit_words"]:
                total_word_hits = sum(i["count"] for i in metrics["risk_distribution"]["top_hit_words"]) or 1
                cur.execute("""
                    INSERT INTO metrics_word_stats
                        (id, app_id, snapshot_date, keyword, hit_count, contribution_pct)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        hit_count=VALUES(hit_count), contribution_pct=VALUES(contribution_pct)
                """, (str(uuid.uuid4()), app_id, snapshot_date,
                      item["word"], item["count"],
                      round(item["count"] / total_word_hits * 100, 2)))

        conn.commit()
        logger.info(f"已同步到数据库: app_id={app_id}, date={snapshot_date}")
    finally:
        conn.close()


def _ensure_tables(cur):
    """确保指标表存在"""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics_snapshot (
            id VARCHAR(36) PRIMARY KEY,
            app_id VARCHAR(64) DEFAULT NULL,
            snapshot_date DATE NOT NULL,
            total_requests INT NOT NULL DEFAULT 0,
            pass_count INT NOT NULL DEFAULT 0,
            rewrite_count INT NOT NULL DEFAULT 0,
            block_count INT NOT NULL DEFAULT 0,
            review_count INT NOT NULL DEFAULT 0,
            error_count INT NOT NULL DEFAULT 0,
            avg_latency_ms DECIMAL(10,2) DEFAULT NULL,
            p50_latency_ms DECIMAL(10,2) DEFAULT NULL,
            p95_latency_ms DECIMAL(10,2) DEFAULT NULL,
            p99_latency_ms DECIMAL(10,2) DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uk_app_date (app_id, snapshot_date)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics_tag_stats (
            id VARCHAR(36) PRIMARY KEY,
            app_id VARCHAR(64) DEFAULT NULL,
            snapshot_date DATE NOT NULL,
            tag_code VARCHAR(128) NOT NULL,
            hit_count INT NOT NULL DEFAULT 0,
            contribution_pct DECIMAL(5,2) DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uk_app_date_tag (app_id, snapshot_date, tag_code)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics_word_stats (
            id VARCHAR(36) PRIMARY KEY,
            app_id VARCHAR(64) DEFAULT NULL,
            snapshot_date DATE NOT NULL,
            keyword VARCHAR(256) NOT NULL,
            hit_count INT NOT NULL DEFAULT 0,
            contribution_pct DECIMAL(5,2) DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_app_date (app_id, snapshot_date),
            INDEX idx_hit_count (hit_count DESC)
        )
    """)


# ============================================================
# 输出
# ============================================================

def print_report(metrics: dict):
    """打印可读的指标报告"""
    s = metrics.get("summary", {})
    lat = metrics.get("latency", {})
    risk = metrics.get("risk_distribution", {})
    rq = metrics.get("rule_quality", {})

    print("\n" + "=" * 60)
    print("  安全运营指标报告")
    print("=" * 60)

    print(f"\n【指标1】整体请求处理分布 (总请求: {s.get('total_requests', 0)})")
    print(f"  安全通过率: {s.get('pass_rate', 0)}%  ({s.get('pass_count', 0)})")
    print(f"  意图改写率: {s.get('rewrite_rate', 0)}%  ({s.get('rewrite_count', 0)})")
    print(f"  直接阻断率: {s.get('block_rate', 0)}%  ({s.get('block_count', 0)})")
    print(f"  人工审核率: {s.get('review_rate', 0)}%  ({s.get('review_count', 0)})")
    print(f"  错误率:     {s.get('error_rate', 0)}%  ({s.get('error_count', 0)})")

    print(f"\n【指标3】风险事件分布")
    print(f"  命中去重敏感词数: {risk.get('unique_hit_words_count', 0)}")
    print(f"  风险标签 TOP5:")
    for item in risk.get("tag_distribution", [])[:5]:
        print(f"    {item['tag']}: {item['count']} ({item['percentage']}%)")
    print(f"  敏感词命中 TOP10:")
    for item in risk.get("top_hit_words", [])[:10]:
        print(f"    {item['word']}: {item['count']}")

    print(f"\n【指标4】处理时延 (样本数: {lat.get('sample_count', 0)})")
    print(f"  平均: {lat.get('avg_ms')} ms")
    print(f"  P50:  {lat.get('p50_ms')} ms")
    print(f"  P95:  {lat.get('p95_ms')} ms")
    print(f"  P99:  {lat.get('p99_ms')} ms")

    print(f"\n【指标5】规则质量")
    print(f"  规则命中贡献度 TOP5:")
    for item in rq.get("rule_hit_distribution", [])[:5]:
        print(f"    {item['tag']}: {item['count']} ({item['contribution_pct']}%)")
    print(f"  敏感词贡献度 TOP5:")
    for item in rq.get("top_contributing_words", [])[:5]:
        print(f"    {item['word']}: {item['count']} ({item['contribution_pct']}%)")

    print("\n" + "=" * 60)


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="安全运营指标计算")
    parser.add_argument("--input", "-i", required=True, help="加工后的 JSONL 目录")
    parser.add_argument("--app-id", default=None, help="按场景过滤")
    parser.add_argument("--date-start", default=None, help="开始日期 yyyy-MM-dd")
    parser.add_argument("--date-end", default=None, help="结束日期 yyyy-MM-dd")
    parser.add_argument("--date", default=None,
                        help="快捷日期: yesterday / today / yyyy-MM-dd")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--sync-db", action="store_true", help="同步结果到 MySQL")
    parser.add_argument("--db-url", default=None,
                        help="数据库连接 URL (sync-db 时必填)")
    args = parser.parse_args()

    # 处理 --date 快捷参数
    if args.date:
        if args.date == "yesterday":
            d = (date.today() - timedelta(days=1)).isoformat()
        elif args.date == "today":
            d = date.today().isoformat()
        else:
            d = args.date
        args.date_start = d
        args.date_end = d

    logger.info(f"加载数据: dir={args.input}, app_id={args.app_id}, "
                f"date=[{args.date_start}, {args.date_end}]")
    records = load_records(args.input, args.app_id, args.date_start, args.date_end)
    logger.info(f"加载 {len(records)} 条记录")

    if not records:
        logger.warning("没有数据，退出")
        sys.exit(0)

    metrics = calculate_metrics(records)

    if args.json:
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
    else:
        print_report(metrics)

    if args.sync_db:
        if not args.db_url:
            logger.error("--sync-db 需要 --db-url 参数")
            sys.exit(1)
        snapshot_date = args.date_start or date.today().isoformat()
        sync_to_db(metrics, args.app_id, snapshot_date, args.db_url)


if __name__ == "__main__":
    main()
