# LLM Guard Manager V2 部署架构设计

## 版本信息
- **版本**: V2.0
- **设计日期**: 2026-02-06
- **关联文档**: V2_SYSTEM_ARCHITECTURE.md, V2_AUTHENTICATION_FLOW.md

---

## 一、部署架构总览

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                          企业内网环境                                 │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Kubernetes Cluster                         │  │
│  │                                                                │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  Namespace: llmsafe                                     │  │  │
│  │  │                                                          │  │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │  │  │
│  │  │  │  Frontend   │  │  Backend    │  │  Redis      │    │  │  │
│  │  │  │  Deployment │  │  Deployment │  │  StatefulSet│    │  │  │
│  │  │  │  (3 pods)   │  │  (3 pods)   │  │  (1 pod)    │    │  │  │
│  │  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │  │  │
│  │  │         │                 │                 │           │  │  │
│  │  │         │                 │                 │           │  │  │
│  │  │  ┌──────┴─────────────────┴─────────────────┴──────┐  │  │  │
│  │  │  │              Service Layer                       │  │  │  │
│  │  │  │  - frontend-svc (ClusterIP)                      │  │  │  │
│  │  │  │  - backend-svc (ClusterIP)                       │  │  │  │
│  │  │  │  - redis-svc (ClusterIP)                         │  │  │  │
│  │  │  └──────────────────┬───────────────────────────────┘  │  │  │
│  │  │                     │                                   │  │  │
│  │  │  ┌──────────────────┴───────────────────────────────┐  │  │  │
│  │  │  │              Ingress Controller                   │  │  │  │
│  │  │  │  - Host: llm-guard.company.com                    │  │  │  │
│  │  │  │  - TLS: enabled                                   │  │  │  │
│  │  │  │  - Paths:                                         │  │  │  │
│  │  │  │    /web-manager/* -> frontend-svc                 │  │  │  │
│  │  │  │    /dbmanage/api/* -> backend-svc                 │  │  │  │
│  │  │  └───────────────────────────────────────────────────┘  │  │  │
│  │  │                                                          │  │  │
│  │  └──────────────────────────────────────────────────────────┘  │  │
│  │                                                                │  │
│  └────────────────────────────────┬───────────────────────────────┘  │
│                                   │                                   │
│                                   │ HTTPS                             │
│                                   ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    外部系统（企业内网）                       │    │
│  │                                                               │    │
│  │  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐ │    │
│  │  │  门户系统   │      │  USAP系统   │      │  MySQL DB   │ │    │
│  │  │  (Portal)   │      │  (认证中心)  │      │  (外部)     │ │    │
│  │  └─────────────┘      └─────────────┘      └─────────────┘ │    │
│  │                                                               │    │
│  └───────────────────────────────────────────────────────────────┘    │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 二、Kubernetes资源配置

### 2.1 Namespace配置

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: llmsafe
  labels:
    name: llmsafe
    environment: production
```

### 2.2 ConfigMap配置

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: llmsafe-config
  namespace: llmsafe
data:
  # 前端配置
  VITE_BASE_PATH: "/web-manager/"
  VITE_API_BASE_URL: "/dbmanage/api/v1"

  # 后端配置
  API_V1_PREFIX: "/api/v1"
  PROJECT_NAME: "LLM Guard Manager"

  # USAP配置
  USAP_BASE_URL: "https://usap.company.com"
  USAP_CLIENT_ID: "llm-guard-manager"

  # Redis配置
  REDIS_HOST: "redis-svc"
  REDIS_PORT: "6379"
  REDIS_DB: "0"

  # 缓存配置
  USER_INFO_CACHE_TTL: "3600"  # 1小时

  # Token配置
  ACCESS_TOKEN_EXPIRE_HOURS: "8"
  REFRESH_TOKEN_EXPIRE_DAYS: "7"
```

### 2.3 Secret配置

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: llmsafe-secrets
  namespace: llmsafe
type: Opaque
stringData:
  # 数据库配置
  DATABASE_URL: "mysql+aiomysql://user:password@mysql-host:3306/llm_safe_db?charset=utf8mb4"

  # JWT密钥
  SECRET_KEY: "your-secret-key-here-change-in-production"

  # USAP密钥
  USAP_CLIENT_SECRET: "usap-client-secret-here"

  # Redis密码（如果需要）
  REDIS_PASSWORD: ""
```

---

## 三、服务部署配置

### 3.1 Frontend Deployment

```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llmsafe-frontend
  namespace: llmsafe
  labels:
    app: llmsafe-frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: llmsafe-frontend
  template:
    metadata:
      labels:
        app: llmsafe-frontend
    spec:
      containers:
      - name: frontend
        image: llmsafe-frontend:v2.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
          name: http
        env:
        - name: VITE_BASE_PATH
          valueFrom:
            configMapKeyRef:
              name: llmsafe-config
              key: VITE_BASE_PATH
        - name: VITE_API_BASE_URL
          valueFrom:
            configMapKeyRef:
              name: llmsafe-config
              key: VITE_API_BASE_URL
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /web-manager/
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /web-manager/
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-svc
  namespace: llmsafe
spec:
  selector:
    app: llmsafe-frontend
  ports:
  - port: 80
    targetPort: 80
    name: http
  type: ClusterIP
```

### 3.2 Backend Deployment

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llmsafe-backend
  namespace: llmsafe
  labels:
    app: llmsafe-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: llmsafe-backend
  template:
    metadata:
      labels:
        app: llmsafe-backend
    spec:
      containers:
      - name: backend
        image: llmsafe-backend:v2.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 9001
          name: http
        env:
        # 从ConfigMap读取
        - name: API_V1_PREFIX
          valueFrom:
            configMapKeyRef:
              name: llmsafe-config
              key: API_V1_PREFIX
        - name: USAP_BASE_URL
          valueFrom:
            configMapKeyRef:
              name: llmsafe-config
              key: USAP_BASE_URL
        - name: USAP_CLIENT_ID
          valueFrom:
            configMapKeyRef:
              name: llmsafe-config
              key: USAP_CLIENT_ID
        - name: REDIS_HOST
          valueFrom:
            configMapKeyRef:
              name: llmsafe-config
              key: REDIS_HOST
        - name: REDIS_PORT
          valueFrom:
            configMapKeyRef:
              name: llmsafe-config
              key: REDIS_PORT

        # 从Secret读取
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: llmsafe-secrets
              key: DATABASE_URL
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: llmsafe-secrets
              key: SECRET_KEY
        - name: USAP_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: llmsafe-secrets
              key: USAP_CLIENT_SECRET

        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"

        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 9001
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 9001
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
---
apiVersion: v1
kind: Service
metadata:
  name: backend-svc
  namespace: llmsafe
spec:
  selector:
    app: llmsafe-backend
  ports:
  - port: 9001
    targetPort: 9001
    name: http
  type: ClusterIP
```

### 3.3 Redis StatefulSet

```yaml
# k8s/redis-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
  namespace: llmsafe
spec:
  serviceName: redis-svc
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
          name: redis
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
        volumeMounts:
        - name: redis-data
          mountPath: /data
        livenessProbe:
          tcpSocket:
            port: 6379
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: redis-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: redis-svc
  namespace: llmsafe
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
    name: redis
  clusterIP: None  # Headless service for StatefulSet
```

### 3.4 Ingress配置

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: llmsafe-ingress
  namespace: llmsafe
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - llm-guard.company.com
    secretName: llmsafe-tls-secret
  rules:
  - host: llm-guard.company.com
    http:
      paths:
      # 前端路由
      - path: /web-manager(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: frontend-svc
            port:
              number: 80

      # 后端API路由
      - path: /dbmanage/api(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: backend-svc
            port:
              number: 9001
```

---

## 四、Docker镜像构建

### 4.1 Frontend Dockerfile

```dockerfile
# frontend/Dockerfile.v2
FROM node:18-alpine AS builder

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建参数
ARG VITE_BASE_PATH=/web-manager/
ARG VITE_API_BASE_URL=/dbmanage/api/v1

# 构建
RUN npm run build

# 生产镜像
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html/web-manager

# 复制Nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 4.2 Backend Dockerfile

```dockerfile
# backend/Dockerfile.v2
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 9001

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9001"]
```

### 4.3 构建脚本

```bash
#!/bin/bash
# build_images.sh

set -e

VERSION="v2.0"

echo "Building Frontend Image..."
cd frontend
docker build -f Dockerfile.v2 -t llmsafe-frontend:${VERSION} .
cd ..

echo "Building Backend Image..."
cd backend
docker build -f Dockerfile.v2 -t llmsafe-backend:${VERSION} .
cd ..

echo "Images built successfully!"
docker images | grep llmsafe
```

---

## 五、部署脚本

### 5.1 完整部署脚本

```bash
#!/bin/bash
# deploy_v2.sh

set -e

NAMESPACE="llmsafe"
VERSION="v2.0"

echo "=========================================="
echo "LLM Guard Manager V2 部署脚本"
echo "=========================================="

# 1. 创建Namespace
echo "[1/7] 创建Namespace..."
kubectl apply -f k8s/namespace.yaml

# 2. 创建ConfigMap
echo "[2/7] 创建ConfigMap..."
kubectl apply -f k8s/configmap.yaml

# 3. 创建Secret
echo "[3/7] 创建Secret..."
kubectl apply -f k8s/secrets.yaml

# 4. 部署Redis
echo "[4/7] 部署Redis..."
kubectl apply -f k8s/redis-statefulset.yaml

# 等待Redis就绪
echo "等待Redis就绪..."
kubectl wait --for=condition=ready pod -l app=redis -n ${NAMESPACE} --timeout=120s

# 5. 部署Backend
echo "[5/7] 部署Backend..."
kubectl apply -f k8s/backend-deployment.yaml

# 等待Backend就绪
echo "等待Backend就绪..."
kubectl wait --for=condition=ready pod -l app=llmsafe-backend -n ${NAMESPACE} --timeout=120s

# 6. 部署Frontend
echo "[6/7] 部署Frontend..."
kubectl apply -f k8s/frontend-deployment.yaml

# 等待Frontend就绪
echo "等待Frontend就绪..."
kubectl wait --for=condition=ready pod -l app=llmsafe-frontend -n ${NAMESPACE} --timeout=120s

# 7. 创建Ingress
echo "[7/7] 创建Ingress..."
kubectl apply -f k8s/ingress.yaml

echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""

# 显示部署状态
echo "Pod状态:"
kubectl get pods -n ${NAMESPACE}

echo ""
echo "Service状态:"
kubectl get svc -n ${NAMESPACE}

echo ""
echo "Ingress状态:"
kubectl get ingress -n ${NAMESPACE}

echo ""
echo "访问地址: https://llm-guard.company.com/web-manager/"
echo "=========================================="
```

### 5.2 更新部署脚本

```bash
#!/bin/bash
# update_v2.sh

set -e

NAMESPACE="llmsafe"
COMPONENT=$1  # frontend, backend, or all

if [ -z "$COMPONENT" ]; then
    echo "用法: ./update_v2.sh [frontend|backend|all]"
    exit 1
fi

update_frontend() {
    echo "更新Frontend..."
    kubectl rollout restart deployment/llmsafe-frontend -n ${NAMESPACE}
    kubectl rollout status deployment/llmsafe-frontend -n ${NAMESPACE}
}

update_backend() {
    echo "更新Backend..."
    kubectl rollout restart deployment/llmsafe-backend -n ${NAMESPACE}
    kubectl rollout status deployment/llmsafe-backend -n ${NAMESPACE}
}

case $COMPONENT in
    frontend)
        update_frontend
        ;;
    backend)
        update_backend
        ;;
    all)
        update_backend
        update_frontend
        ;;
    *)
        echo "无效的组件: $COMPONENT"
        exit 1
        ;;
esac

echo "更新完成！"
```

---

## 六、监控和日志

### 6.1 健康检查端点

```python
# backend/app/api/v1/endpoints/health.py
from fastapi import APIRouter, Depends
from app.clients.usap_client import USAPClient
from app.core.db import get_db

router = APIRouter()

@router.get("/health")
async def health_check():
    """基础健康检查"""
    return {
        "status": "healthy",
        "service": "llm-guard-manager",
        "version": "v2.0"
    }

@router.get("/health/ready")
async def readiness_check(
    db = Depends(get_db),
    usap_client: USAPClient = Depends()
):
    """就绪检查（检查依赖服务）"""
    checks = {
        "database": False,
        "usap": False,
        "redis": False
    }

    # 检查数据库
    try:
        await db.execute("SELECT 1")
        checks["database"] = True
    except:
        pass

    # 检查USAP（可选）
    try:
        await usap_client.ping()
        checks["usap"] = True
    except:
        pass

    # 检查Redis
    try:
        await redis_client.ping()
        checks["redis"] = True
    except:
        pass

    all_healthy = all(checks.values())

    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks
    }
```

### 6.2 日志配置

```yaml
# k8s/logging-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: logging-config
  namespace: llmsafe
data:
  logging.conf: |
    [loggers]
    keys=root,app

    [handlers]
    keys=console,file

    [formatters]
    keys=json

    [logger_root]
    level=INFO
    handlers=console

    [logger_app]
    level=INFO
    handlers=console,file
    qualname=app
    propagate=0

    [handler_console]
    class=StreamHandler
    level=INFO
    formatter=json
    args=(sys.stdout,)

    [handler_file]
    class=handlers.RotatingFileHandler
    level=INFO
    formatter=json
    args=('/var/log/app/app.log', 'a', 10485760, 5)

    [formatter_json]
    format={"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}
```

### 6.3 Prometheus监控（可选）

```yaml
# k8s/servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: llmsafe-backend
  namespace: llmsafe
spec:
  selector:
    matchLabels:
      app: llmsafe-backend
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

---

## 七、高可用设计

### 7.1 副本配置
- **Frontend**: 3个副本，支持滚动更新
- **Backend**: 3个副本，支持滚动更新
- **Redis**: 1个副本（可升级为主从或集群）

### 7.2 资源限制
```yaml
resources:
  requests:  # 最小保证资源
    memory: "512Mi"
    cpu: "500m"
  limits:    # 最大使用资源
    memory: "1Gi"
    cpu: "1000m"
```

### 7.3 Pod反亲和性（可选）
```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - llmsafe-backend
        topologyKey: kubernetes.io/hostname
```

---

## 八、网络策略

### 8.1 NetworkPolicy配置

```yaml
# k8s/networkpolicy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: llmsafe-network-policy
  namespace: llmsafe
spec:
  podSelector:
    matchLabels:
      app: llmsafe-backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # 允许来自Frontend的流量
  - from:
    - podSelector:
        matchLabels:
          app: llmsafe-frontend
    ports:
    - protocol: TCP
      port: 9001
  # 允许来自Ingress Controller的流量
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 9001
  egress:
  # 允许访问Redis
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  # 允许访问外部MySQL
  - to:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 3306
  # 允许访问USAP（外部）
  - to:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 443
  # 允许DNS查询
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: UDP
      port: 53
```

---

## 九、备份和恢复

### 9.1 数据备份策略
```bash
#!/bin/bash
# backup.sh

# 备份MySQL数据库
mysqldump -h mysql-host -u user -p llm_safe_db > backup_$(date +%Y%m%d).sql

# 备份Redis数据（如果需要）
kubectl exec -n llmsafe redis-0 -- redis-cli BGSAVE
kubectl cp llmsafe/redis-0:/data/dump.rdb ./redis_backup_$(date +%Y%m%d).rdb
```

### 9.2 配置备份
```bash
# 导出所有K8s配置
kubectl get all,configmap,secret,ingress -n llmsafe -o yaml > k8s_backup_$(date +%Y%m%d).yaml
```

---

## 十、总结

### 10.1 部署清单
- ✅ Namespace配置
- ✅ ConfigMap和Secret
- ✅ Frontend Deployment (3副本)
- ✅ Backend Deployment (3副本)
- ✅ Redis StatefulSet (1副本)
- ✅ Service配置
- ✅ Ingress配置
- ✅ 健康检查
- ✅ 资源限制
- ✅ 日志配置

### 10.2 关键配置
| 配置项 | 值 |
|--------|-----|
| Namespace | llmsafe |
| Frontend副本数 | 3 |
| Backend副本数 | 3 |
| Redis副本数 | 1 |
| 域名 | llm-guard.company.com |
| 前端路径 | /web-manager/ |
| 后端路径 | /dbmanage/api/v1 |

---

**下一步**: 请查看 `V2_REQUIREMENTS.md` 了解完整需求文档
