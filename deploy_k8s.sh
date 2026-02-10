#!/bin/bash

# K8s部署脚本
set -e

echo "=========================================="
echo "LLM Guard Manager K8s部署脚本"
echo "=========================================="

# 配置
NAMESPACE="llm-guard"
REGISTRY="${DOCKER_REGISTRY:-your-registry}"
VERSION="${VERSION:-latest}"

# 1. 创建namespace
echo -e "\n[步骤1] 创建namespace..."
kubectl apply -f k8s/namespace.yaml

# 2. 创建secrets
echo -e "\n[步骤2] 创建secrets..."
echo "⚠️  请确保已修改 k8s/secrets.yaml 中的敏感信息！"
read -p "是否继续? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "部署已取消"
    exit 1
fi
kubectl apply -f k8s/secrets.yaml

# 3. 创建configmap
echo -e "\n[步骤3] 创建configmap..."
kubectl apply -f k8s/configmap.yaml

# 4. 构建并推送镜像
echo -e "\n[步骤4] 构建并推送镜像..."
read -p "是否需要构建镜像? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 构建后端镜像
    echo "构建后端镜像..."
    cd backend
    docker build -f Dockerfile.k8s -t ${REGISTRY}/llm-guard-backend:${VERSION} .
    docker push ${REGISTRY}/llm-guard-backend:${VERSION}
    cd ..

    # 构建前端镜像
    echo "构建前端镜像..."
    cd frontend
    docker build -f Dockerfile.k8s -t ${REGISTRY}/llm-guard-frontend:${VERSION} \
        --build-arg VITE_BASE_PATH=/web-manager/ \
        --build-arg VITE_API_BASE_URL=/dbmanage/api/v1 .
    docker push ${REGISTRY}/llm-guard-frontend:${VERSION}
    cd ..
fi

# 5. 更新deployment配置中的镜像地址
echo -e "\n[步骤5] 更新deployment配置..."
sed -i.bak "s|your-registry|${REGISTRY}|g" k8s/backend-deployment.yaml
sed -i.bak "s|your-registry|${REGISTRY}|g" k8s/frontend-deployment.yaml

# 6. 部署后端
echo -e "\n[步骤6] 部署后端..."
kubectl apply -f k8s/backend-deployment.yaml

# 7. 部署前端
echo -e "\n[步骤7] 部署前端..."
kubectl apply -f k8s/frontend-deployment.yaml

# 8. 配置Ingress
echo -e "\n[步骤8] 配置Ingress..."
echo "⚠️  请确保已修改 k8s/ingress.yaml 中的域名！"
kubectl apply -f k8s/ingress.yaml

# 9. 等待部署完成
echo -e "\n[步骤9] 等待部署完成..."
kubectl wait --for=condition=available --timeout=300s \
    deployment/llm-guard-backend -n ${NAMESPACE}
kubectl wait --for=condition=available --timeout=300s \
    deployment/llm-guard-frontend -n ${NAMESPACE}

# 10. 检查部署状态
echo -e "\n[步骤10] 检查部署状态..."
echo -e "\n=== Pods ==="
kubectl get pods -n ${NAMESPACE}

echo -e "\n=== Services ==="
kubectl get svc -n ${NAMESPACE}

echo -e "\n=== Ingress ==="
kubectl get ingress -n ${NAMESPACE}

echo -e "\n=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo "前端访问地址: https://your-domain.com/web-manager/"
echo "后端API地址: https://your-domain.com/dbmanage/api/v1"
echo ""
echo "运行测试: ./k8s_deployment_test.sh"
echo "=========================================="
