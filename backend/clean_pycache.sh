#!/bin/bash

# 清理 Python 缓存文件脚本
# 删除所有 __pycache__ 目录和 .pyc 文件

set -e

# 获取脚本所在目录（backend 目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Python 缓存清理脚本 ==="
echo "目标目录: $SCRIPT_DIR"
echo ""

# 统计要删除的文件数量
PYCACHE_COUNT=$(find "$SCRIPT_DIR" -type d -name "__pycache__" | wc -l)
PYC_COUNT=$(find "$SCRIPT_DIR" -type f -name "*.pyc" | wc -l)
PYO_COUNT=$(find "$SCRIPT_DIR" -type f -name "*.pyo" | wc -l)

echo "发现的缓存文件："
echo "  - __pycache__ 目录: $PYCACHE_COUNT 个"
echo "  - .pyc 文件: $PYC_COUNT 个"
echo "  - .pyo 文件: $PYO_COUNT 个"
echo ""

if [ "$PYCACHE_COUNT" -eq 0 ] && [ "$PYC_COUNT" -eq 0 ] && [ "$PYO_COUNT" -eq 0 ]; then
    echo "✅ 没有发现缓存文件，目录已经很干净了！"
    exit 0
fi

# 删除 __pycache__ 目录
echo "正在删除 __pycache__ 目录..."
find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 删除 .pyc 文件
echo "正在删除 .pyc 文件..."
find "$SCRIPT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true

# 删除 .pyo 文件
echo "正在删除 .pyo 文件..."
find "$SCRIPT_DIR" -type f -name "*.pyo" -delete 2>/dev/null || true

echo ""
echo "✅ 清理完成！"
echo ""

# 验证清理结果
REMAINING_PYCACHE=$(find "$SCRIPT_DIR" -type d -name "__pycache__" | wc -l)
REMAINING_PYC=$(find "$SCRIPT_DIR" -type f -name "*.pyc" | wc -l)
REMAINING_PYO=$(find "$SCRIPT_DIR" -type f -name "*.pyo" | wc -l)

if [ "$REMAINING_PYCACHE" -eq 0 ] && [ "$REMAINING_PYC" -eq 0 ] && [ "$REMAINING_PYO" -eq 0 ]; then
    echo "✅ 验证通过：所有缓存文件已清理干净"
else
    echo "⚠️  警告：仍有部分缓存文件未清理"
    echo "  - 剩余 __pycache__: $REMAINING_PYCACHE 个"
    echo "  - 剩余 .pyc: $REMAINING_PYC 个"
    echo "  - 剩余 .pyo: $REMAINING_PYO 个"
fi
