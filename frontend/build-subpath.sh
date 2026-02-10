#!/bin/bash

# 前端镜像构建脚本 - 支持子路径部署
# 使用方法:
#   ./build-subpath.sh /db_web/ v1.0

set -e

# 配置变量
BASE_PATH="${1:-/}"  # 第一个参数：子路径，默认为根路径
VERSION="${2:-latest}"  # 第二个参数：版本号，默认为 latest
REGISTRY="your-registry"  # 替换为你的镜像仓库地址
IMAGE_NAME="llm-guard-frontend"

echo "=========================================="
echo "构建前端镜像（子路径部署）"
echo "Base Path: ${BASE_PATH}"
echo "镜像: ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
echo "=========================================="

# 进入前端目录
cd "$(dirname "$0")"

# 设置环境变量并构建
echo "开始构建镜像..."
docker build \
  --build-arg VITE_BASE_PATH="${BASE_PATH}" \
  -t ${REGISTRY}/${IMAGE_NAME}:${VERSION} \
  .

echo "构建完成！"
echo ""
echo "镜像信息:"
docker images | grep ${IMAGE_NAME}

echo ""
echo "=========================================="
echo "本地测试"
echo "=========================================="
echo "运行以下命令进行本地测试:"
echo "docker run -d -p 8080:8080 \\"
echo "  -e BACKEND_SERVICE_URL=http://host.docker.internal:9001 \\"
echo "  ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
echo ""
echo "访问: http://localhost:8080${BASE_PATH}"
echo ""
echo "注意: 本地测试时需要配置 Nginx 反向代理来模拟子路径访问"
