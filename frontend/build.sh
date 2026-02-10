#!/bin/bash

# 前端镜像构建脚本
# 使用非特权端口 8080

set -e

# 配置变量
REGISTRY="your-registry"  # 替换为你的镜像仓库地址
IMAGE_NAME="llm-guard-frontend"
VERSION="${1:-latest}"  # 默认使用 latest，可通过参数指定版本

echo "=========================================="
echo "构建前端镜像"
echo "镜像: ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
echo "=========================================="

# 进入前端目录
cd "$(dirname "$0")"

# 构建镜像
echo "开始构建镜像..."
docker build -t ${REGISTRY}/${IMAGE_NAME}:${VERSION} .

# 打标签
if [ "$VERSION" != "latest" ]; then
    echo "打标签: latest"
    docker tag ${REGISTRY}/${IMAGE_NAME}:${VERSION} ${REGISTRY}/${IMAGE_NAME}:latest
fi

echo "构建完成！"
echo ""
echo "镜像信息:"
docker images | grep ${IMAGE_NAME}

echo ""
echo "=========================================="
echo "推送镜像到仓库"
echo "=========================================="
read -p "是否推送镜像到仓库? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "推送镜像: ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}

    if [ "$VERSION" != "latest" ]; then
        echo "推送镜像: ${REGISTRY}/${IMAGE_NAME}:latest"
        docker push ${REGISTRY}/${IMAGE_NAME}:latest
    fi

    echo "推送完成！"
else
    echo "跳过推送"
fi

echo ""
echo "=========================================="
echo "本地测试"
echo "=========================================="
echo "运行以下命令进行本地测试:"
echo "docker run -d -p 8080:8080 -e BACKEND_SERVICE_URL=http://host.docker.internal:9001 ${REGISTRY}/${IMAGE_NAME}:${VERSION}"
echo "访问: http://localhost:8080"
