#!/bin/bash
# 打包前端 dist 目录的脚本

set -e  # 遇到错误立即退出

echo "开始打包前端 dist 目录..."

# 1. 在工程里面创建 abc 目录，有的话就清空里面的内容
if [ -d "abc" ]; then
    echo "清空 abc 目录..."
    rm -rf abc/*
else
    echo "创建 abc 目录..."
    mkdir abc
fi

# 2. 从 frontend 里面对 dist 目录进行 zip 压缩，名称是 dist.zip
echo "压缩 frontend/dist 目录..."
cd frontend
if [ ! -d "dist" ]; then
    echo "❌ 错误：frontend/dist 目录不存在！请先构建前端。"
    exit 1
fi

zip -r dist.zip dist/
echo "✅ 压缩完成：frontend/dist.zip"

# 3. 将这个 dist.zip mv 到 abc 目录下
echo "移动 dist.zip 到 abc 目录..."
mv dist.zip ../abc/
cd ..

echo "✅ 完成！dist.zip 已保存到 abc 目录"
ls -lh abc/dist.zip
