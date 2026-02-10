#!/bin/bash
# 上传 dist 文件到 Kubernetes PVC

set -e

NAMESPACE="${1:-default}"
PVC_NAME="${2:-llm-guard-dist-pvc}"
DIST_PATH="${3:-./dist}"

echo "=========================================="
echo "上传 dist 文件到 Kubernetes PVC"
echo "Namespace: ${NAMESPACE}"
echo "PVC: ${PVC_NAME}"
echo "Dist Path: ${DIST_PATH}"
echo "=========================================="

# 检查 dist 目录是否存在
if [ ! -d "$DIST_PATH" ]; then
    echo "错误: dist 目录不存在: $DIST_PATH"
    echo "请先构建前端: cd frontend && npm run build"
    exit 1
fi

# 创建临时 Pod
echo "创建临时 Pod..."
kubectl run dist-uploader \
  --image=busybox \
  --restart=Never \
  --overrides="{
    \"spec\": {
      \"containers\": [{
        \"name\": \"uploader\",
        \"image\": \"busybox\",
        \"command\": [\"sleep\", \"3600\"],
        \"volumeMounts\": [{
          \"name\": \"dist\",
          \"mountPath\": \"/dist\"
        }]
      }],
      \"volumes\": [{
        \"name\": \"dist\",
        \"persistentVolumeClaim\": {
          \"claimName\": \"${PVC_NAME}\"
        }
      }]
    }
  }" \
  -n ${NAMESPACE}

# 等待 Pod 就绪
echo "等待 Pod 就绪..."
kubectl wait --for=condition=Ready pod/dist-uploader -n ${NAMESPACE} --timeout=60s

# 清空目标目录
echo "清空目标目录..."
kubectl exec dist-uploader -n ${NAMESPACE} -- sh -c "rm -rf /dist/*"

# 上传文件
echo "上传 dist 文件..."
kubectl cp ${DIST_PATH}/. dist-uploader:/dist -n ${NAMESPACE}

# 验证上传
echo "验证上传..."
kubectl exec dist-uploader -n ${NAMESPACE} -- ls -la /dist

# 删除临时 Pod
echo "删除临时 Pod..."
kubectl delete pod dist-uploader -n ${NAMESPACE}

echo "=========================================="
echo "上传完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 确认 Deployment 配置正确"
echo "2. 应用配置: kubectl apply -f k8s-deployment-mount-dist.yaml"
echo "3. 或重启现有 Deployment: kubectl rollout restart deployment/llm-guard-frontend -n ${NAMESPACE}"
