# LLM Guard Manager V2 — 架构与部署文档

## 版本信息
- **版本**: V2.2
- **更新时间**: 2026-02-10

---

## 一、技术栈

| 层次 | V1（已废弃） | V2（当前） |
|------|-------------|-----------|
| 前端 | React + Ant Design | **Vue 3 + Element Plus** |
| 后端 | Python FastAPI | **Java Spring Boot 3** |
| 认证 | 直接 JWT 登录 | **SSO 门户 + Ticket + JWT** |
| 部署 | Docker 容器 | **K8s (Minikube) + hostPath 挂载** |

---

## 二、系统架构

### 2.1 组件拓扑

```
互联网
  │
  │ HTTPS (llmsafe.kkrrc-359.top)
  ▼
┌──────────────────────────────────────────────┐
│  宿主机 Nginx (/etc/nginx/conf.d/llmsafe.conf)│
│  SSL 终止 → proxy_pass http://192.168.49.2:30860
└──────────────────┬───────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│  Minikube (K8s) — Namespace: llmsafe          │
│                                                │
│  Ingress Controller (NodePort 30860)           │
│  ├─ /web-manager/*  → vue-frontend-svc:80     │
│  ├─ /dbmanage/*     → java-backend-svc:9001   │
│  └─ /portal/*       → portal-svc:8080         │
│                                                │
│  ┌────────────────┐  ┌────────────────┐       │
│  │ Vue Frontend   │  │ Java Backend   │       │
│  │ nginx:alpine   │  │ temurin:21-jre │       │
│  │ Port: 80       │  │ Port: 9002     │       │
│  └────────────────┘  └───────┬────────┘       │
│                               │                │
│  ┌────────────────┐  ┌───────┴────────┐       │
│  │ Portal         │  │ Mock-USAP      │       │
│  │ python:3.12    │  │ python:3.12    │       │
│  │ Port: 8080     │  │ Port: 8080     │       │
│  └────────────────┘  └────────────────┘       │
└──────────────────────────────────────────────┘
                   │
                   ▼
          MySQL (外部: 49.233.46.126:38306)
```

### 2.2 Service 与端口映射

| Service | Type | Port | Target Port | 说明 |
|---------|------|------|-------------|------|
| `vue-frontend-svc` | ClusterIP | 80 | 80 | Vue 前端 nginx |
| `java-backend-svc` | ClusterIP | 9001 | 9002 | Java 后端（Spring Boot 监听 9002） |
| `mock-usap-svc` | ClusterIP | 8080 | 8080 | Mock 认证中心 |
| `portal-svc` | ClusterIP | 8080 | 8080 | 门户系统 |

### 2.3 Ingress 路由

| Ingress | 路径 | 目标 | Rewrite |
|---------|------|------|---------|
| `llmsafe-frontend-ingress` | `/web-manager` (Prefix) | `vue-frontend-svc:80` | 无（透传） |
| `llmsafe-backend-ingress` | `/dbmanage(/\|$)(.*)` | `java-backend-svc:9001` | `/$2` |
| `llmsafe-portal-ingress` | `/portal(/\|$)(.*)` | `portal-svc:8080` | `/$2` |

**说明**：
- 前端 ingress **不做 rewrite**，因为 Vue nginx 自己处理 `/web-manager/` 路径
- 后端 ingress rewrite `/dbmanage/api/v1/xxx` → `/api/v1/xxx`，匹配 Java context-path
- Portal ingress rewrite `/portal/xxx` → `/xxx`

---

## 三、K8s 资源配置

### 3.1 资源限制

| Pod | Image | CPU req/limit | Mem req/limit |
|-----|-------|---------------|---------------|
| java-backend | eclipse-temurin:21-jre-alpine | 50m / 500m | 128Mi / 384Mi |
| vue-frontend | nginx:alpine | 10m / 100m | 16Mi / 64Mi |
| mock-usap | python:3.12-slim | 100m / 200m | 64Mi / 128Mi |
| portal | python:3.12-slim | 100m / 200m | 64Mi / 128Mi |

> mock-usap 和 portal 的 128Mi limit 是下限，pip install 阶段内存峰值需要，不可再缩。

### 3.2 YAML 文件清单

| 文件 | 内容 | V2 是否使用 |
|------|------|------------|
| `k8s/namespace.yaml` | llmsafe namespace | ✅ |
| `k8s/java-vue-mount.yaml` | Java 后端 + Vue 前端 Deployment/Service | ✅ |
| `k8s/vue-nginx-config.yaml` | Vue 前端 nginx ConfigMap | ✅ |
| `k8s/mock-usap.yaml` | Mock-USAP Deployment/Service | ✅ |
| `k8s/portal.yaml` | Portal Deployment/Service | ✅ |
| `k8s/ingress.yaml` | 3 个 Ingress 资源 | ✅ |
| `k8s/backend-deployment.yaml` | Python 后端（V1） | ❌ |
| `k8s/frontend-deployment.yaml` | React 前端（V1） | ❌ |
| `k8s/frontend-configmap.yaml` | React nginx config（V1） | ❌ |

### 3.3 Volume 挂载（hostPath）

使用 `docker cp` 将宿主机文件复制到 minikube 容器内的 `/host/` 目录。

| Pod | minikube 路径 | 容器挂载路径 |
|-----|--------------|-------------|
| java-backend | `/host/backend-java/target` | `/app` |
| vue-frontend | `/host/frontend-vue/dist` | `/usr/share/nginx/html/web-manager` |
| mock-usap | `/host/mock-usap` | `/app` |
| portal | `/host/portal` | `/app` |

### 3.4 Java 后端配置

```yaml
# backend-java/src/main/resources/application.yml
server:
  port: 9002
  servlet:
    context-path: /api/v1

spring:
  datasource:
    url: jdbc:mysql://49.233.46.126:38306/llm_safe_db
    username: root
    password: "Platform#2026"

app:
  security:
    jwt:
      secret: "903dc0b0b9ca74459abf456fa2cd17eb47348a5056c599f6e52a53ae944b9c1a"
      expiration: 691200  # 8 days
  usap:
    base-url: "http://mock-usap-svc:8080"
```

### 3.5 Vue 前端 Nginx 配置

```nginx
# k8s/vue-nginx-config.yaml → ConfigMap: vue-nginx-config
server {
    listen 80;
    location /web-manager/ {
        alias /usr/share/nginx/html/web-manager/;
        try_files $uri $uri/ /web-manager/index.html;
    }
    location /dbmanage/api/v1/ {
        proxy_pass http://java-backend-svc:9001/dbmanage/api/v1/;
    }
    location /health {
        return 200 "ok";
    }
}
```

### 3.6 宿主机 Nginx 配置

```nginx
# /etc/nginx/conf.d/llmsafe.conf
server {
    listen 443 ssl;
    server_name llmsafe.kkrrc-359.top;
    ssl_certificate /etc/letsencrypt/live/llmsafe.kkrrc-359.top/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/llmsafe.kkrrc-359.top/privkey.pem;

    location / {
        proxy_pass http://192.168.49.2:30860;
        proxy_set_header Host $host;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
```

---

## 四、部署步骤

### 4.1 前置条件

- minikube 已启动（docker driver，1800MB 内存）
- ingress addon 已启用
- ingress-nginx NodePort 为 30860
- 宿主机 nginx 已配置 SSL 转发

### 4.2 部署命令

```bash
# 1. 创建 namespace
kubectl apply -f k8s/namespace.yaml

# 2. 在 minikube 容器内创建目录
docker exec minikube mkdir -p /host/frontend-vue /host/backend-java/target /host/mock-usap /host/portal

# 3. 复制文件到 minikube
docker cp frontend-vue/dist minikube:/host/frontend-vue/dist
docker cp backend-java/target/manager-0.0.1-SNAPSHOT.jar minikube:/host/backend-java/target/
docker cp mock-usap/. minikube:/host/mock-usap/
docker cp portal/. minikube:/host/portal/

# 4. 部署所有服务
kubectl apply -f k8s/vue-nginx-config.yaml
kubectl apply -f k8s/java-vue-mount.yaml
kubectl apply -f k8s/mock-usap.yaml
kubectl apply -f k8s/portal.yaml
kubectl apply -f k8s/ingress.yaml

# 5. 确认 ingress NodePort
kubectl patch svc ingress-nginx-controller -n ingress-nginx \
  --type='json' -p='[{"op":"replace","path":"/spec/ports/0/nodePort","value":30860}]'

# 6. 等待所有 Pod Ready
kubectl get pods -n llmsafe -w
```

### 4.3 验证

```bash
# Portal 健康检查
curl -s http://192.168.49.2:30860/portal/api/health
# 期望: {"status":"healthy","service":"portal"}

# Vue 前端
curl -s -o /dev/null -w "%{http_code}" http://192.168.49.2:30860/web-manager/
# 期望: 200

# Java 后端健康检查
curl -s http://192.168.49.2:30860/dbmanage/api/v1/actuator/health
# 期望: 200

# SSO 登录全流程测试
# Step 1: Portal 登录
curl -s -X POST http://192.168.49.2:30860/portal/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Gn1yo0jY"}'
# 期望: {"success":true,"session_id":"SES_xxx",...}
```

### 4.4 更新部署

```bash
# 更新 Vue 前端
cd frontend-vue
VITE_BASE_PATH=/web-manager/ VITE_API_BASE_URL=/dbmanage/api/v1 npm run build
docker cp dist minikube:/host/frontend-vue/dist
kubectl delete pod -l app=llmsafe-vue-frontend -n llmsafe

# 更新 Java 后端（重新编译后）
docker cp backend-java/target/manager-0.0.1-SNAPSHOT.jar minikube:/host/backend-java/target/
kubectl delete pod -l app=llmsafe-java-backend -n llmsafe

# 更新 mock-usap / portal（代码修改后）
docker cp mock-usap/. minikube:/host/mock-usap/
kubectl delete pod -l app=mock-usap -n llmsafe
```

---

## 五、健康检查端点

| 服务 | 端点 | 期望响应 |
|------|------|---------|
| Java 后端 | `/api/v1/actuator/health` | `{"status":"UP"}` |
| Mock-USAP | `/api/health` | `{"status":"healthy"}` |
| Portal | `/api/health` | `{"status":"healthy","service":"portal"}` |
| Vue 前端 nginx | `/health` | `ok` |

---

## 六、日志查看

```bash
kubectl logs -n llmsafe -l app=llmsafe-java-backend --tail=50
kubectl logs -n llmsafe -l app=llmsafe-vue-frontend --tail=50
kubectl logs -n llmsafe -l app=mock-usap --tail=50
kubectl logs -n llmsafe -l app=portal --tail=50
```

---

## 七、V1 组件说明

以下组件仍保留在代码仓库中，但 V2 部署**不使用**：

| 目录 | 说明 | 状态 |
|------|------|------|
| `backend/` | Python FastAPI 后端 | 保留，不部署 |
| `frontend/` | React + Ant Design 前端 | 保留，不部署 |
| `k8s/backend-deployment.yaml` | Python 后端 K8s 配置 | 保留，不使用 |
| `k8s/frontend-deployment.yaml` | React 前端 K8s 配置 | 保留，不使用 |
| `k8s/frontend-configmap.yaml` | React nginx ConfigMap | 保留，不使用 |
