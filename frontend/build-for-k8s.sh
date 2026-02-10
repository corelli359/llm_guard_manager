#!/bin/bash
# 为 K8s 部署构建前端
# 使用正确的环境变量配置前端和后端路径

echo "开始构建前端（K8s 部署）..."
echo "前端路径: /web-manager/"
echo "后端 API: /dbmanage/api/v1"

# 清理旧的构建产物
rm -rf dist

# 使用正确的环境变量构建
VITE_BASE_PATH=/web-manager/ VITE_API_BASE_URL=/dbmanage/api/v1 npm run build

if [ $? -eq 0 ]; then
    echo "✅ 构建成功！"
    echo ""
    echo "下一步："
    echo "1. 重启前端 Pod: kubectl delete pod -l app=llmsafe-frontend -n llmsafe"
    echo "2. 访问: http://llmsafe-dev.aisp.test.abc/web-manager/"
else
    echo "❌ 构建失败！"
    exit 1
fi
