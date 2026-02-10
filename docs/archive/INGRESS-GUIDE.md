# Ingress 配置指南

本文档详细说明如何为 LLM Guard Manager 配置 Kubernetes Ingress，支持多路由匹配场景。

## 前置条件

1. **Ingress Controller 已安装**
   ```bash
   # 检查是否安装了 Ingress Controller
   kubectl get pods -n ingress-nginx

   # 如果没有，安装 nginx-ingress-controller
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
   ```

2. **DNS 配置**
   - 将域名解析到 Ingress Controller 的外部 IP
   ```bash
   # 获取 Ingress Controller 的外部 IP
   kubectl get svc -n ingress-nginx
   ```

## 配置场景

### 场景 1: 单域名 - 前端和 API 分离路径

**适用场景**: 一个域名，前端在根路径，API 在 `/api` 路径

```yaml
rules:
- host: llm-guard.example.com
  http:
    paths:
    # API 路由（优先级高，放在前面）
    - path: /api
      pathType: Prefix
      backend:
        service:
          name: llm-guard-backend-svc
          port:
            number: 9001

    # 前端路由（优先级低，放在后面）
    - path: /
      pathType: Prefix
      backend:
        service:
          name: llm-guard-frontend-svc
          port:
            number: 80
```

**访问方式**:
- 前端: `https://llm-guard.example.com/`
- API: `https://llm-guard.example.com/api/v1/tags`

**注意**:
- 前端的 Nginx 配置中，API 代理路径需要保持为 `/api`
- 不需要修改前端代码，因为前端请求的是相对路径 `/api/v1/*`

### 场景 2: 单域名 - 多服务共享（带路径前缀）

**适用场景**: 多个服务共享一个域名，每个服务有独立的路径前缀

```yaml
annotations:
  nginx.ingress.kubernetes.io/rewrite-target: /$2

rules:
- host: platform.example.com
  http:
    paths:
    # LLM Guard API: /llm-guard/api/* -> /api/*
    - path: /llm-guard/api(/|$)(.*)
      pathType: ImplementationSpecific
      backend:
        service:
          name: llm-guard-backend-svc
          port:
            number: 9001

    # LLM Guard 前端: /llm-guard/* -> /*
    - path: /llm-guard(/|$)(.*)
      pathType: ImplementationSpecific
      backend:
        service:
          name: llm-guard-frontend-svc
          port:
            number: 80

    # 其他服务
    - path: /other-service(/|$)(.*)
      pathType: ImplementationSpecific
      backend:
        service:
          name: other-service
          port:
            number: 8080
```

**访问方式**:
- LLM Guard 前端: `https://platform.example.com/llm-guard/`
- LLM Guard API: `https://platform.example.com/llm-guard/api/v1/tags`
- 其他服务: `https://platform.example.com/other-service/`

**前端需要修改**:

修改 `frontend/vite.config.ts`:
```typescript
export default defineConfig({
  base: '/llm-guard/',  // 添加这行
  // ...
})
```

修改 `frontend/src/api.ts`:
```typescript
const api = axios.create({
  baseURL: '/llm-guard/api/v1',  // 修改为带前缀的路径
});
```

### 场景 3: 多域名 - 前端和 API 分离

**适用场景**: 前端和 API 使用不同的域名

```yaml
rules:
# 前端域名
- host: llm-guard.example.com
  http:
    paths:
    - path: /
      pathType: Prefix
      backend:
        service:
          name: llm-guard-frontend-svc
          port:
            number: 80

# API 域名
- host: api.llm-guard.example.com
  http:
    paths:
    - path: /
      pathType: Prefix
      backend:
        service:
          name: llm-guard-backend-svc
          port:
            number: 9001
```

**访问方式**:
- 前端: `https://llm-guard.example.com/`
- API: `https://api.llm-guard.example.com/api/v1/tags`

**前端需要修改**:

修改 `frontend/src/api.ts`:
```typescript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'https://api.llm-guard.example.com/api/v1',
});
```

修改 `frontend/.env.production`:
```
VITE_API_BASE_URL=https://api.llm-guard.example.com/api/v1
```

**注意**: 需要配置 CORS，在后端 `backend/app/main.py` 中:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://llm-guard.example.com"],  # 前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 场景 4: 精确路径匹配

**适用场景**: 需要对特定路径做特殊处理

```yaml
rules:
- host: example.com
  http:
    paths:
    # 精确匹配（优先级最高）
    - path: /api/v1/health
      pathType: Exact
      backend:
        service:
          name: health-check-service
          port:
            number: 8080

    # 前缀匹配
    - path: /api
      pathType: Prefix
      backend:
        service:
          name: llm-guard-backend-svc
          port:
            number: 9001

    # 默认路由
    - path: /
      pathType: Prefix
      backend:
        service:
          name: llm-guard-frontend-svc
          port:
            number: 80
```

## PathType 说明

Kubernetes Ingress 支持三种路径类型：

### 1. Prefix（前缀匹配）
- 最常用的类型
- 匹配以指定路径开头的所有请求
- 示例: `path: /api` 匹配 `/api`, `/api/v1`, `/api/v1/tags` 等

### 2. Exact（精确匹配）
- 只匹配完全相同的路径
- 示例: `path: /api` 只匹配 `/api`，不匹配 `/api/v1`

### 3. ImplementationSpecific（实现特定）
- 由 Ingress Controller 决定匹配规则
- 通常用于正则表达式匹配
- 示例: `path: /api(/|$)(.*)` 支持路径重写

## 路径优先级

Ingress 路径匹配遵循以下优先级（从高到低）：

1. **Exact** 精确匹配
2. **Prefix** 最长前缀匹配
3. **ImplementationSpecific** 按定义顺序

**最佳实践**:
- 将更具体的路径放在前面
- 将通配路径（如 `/`）放在最后
- 使用 Exact 类型处理特殊端点

## 常用 Annotations

### CORS 配置
```yaml
annotations:
  nginx.ingress.kubernetes.io/enable-cors: "true"
  nginx.ingress.kubernetes.io/cors-allow-origin: "*"
  nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, DELETE, OPTIONS"
  nginx.ingress.kubernetes.io/cors-allow-headers: "Authorization,Content-Type"
```

### 路径重写
```yaml
annotations:
  # 去除路径前缀
  nginx.ingress.kubernetes.io/rewrite-target: /$2
  # 配合使用: path: /prefix(/|$)(.*)
```

### 请求限制
```yaml
annotations:
  # 请求体大小限制
  nginx.ingress.kubernetes.io/proxy-body-size: "10m"

  # 超时设置
  nginx.ingress.kubernetes.io/proxy-connect-timeout: "60"
  nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
  nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
```

### SSL/TLS
```yaml
annotations:
  # 强制 HTTPS 重定向
  nginx.ingress.kubernetes.io/ssl-redirect: "true"

  # 使用 cert-manager 自动签发证书
  cert-manager.io/cluster-issuer: "letsencrypt-prod"
```

### 限流
```yaml
annotations:
  # 每秒请求数限制
  nginx.ingress.kubernetes.io/limit-rps: "10"

  # 每个 IP 的连接数限制
  nginx.ingress.kubernetes.io/limit-connections: "5"
```

### 白名单
```yaml
annotations:
  # IP 白名单
  nginx.ingress.kubernetes.io/whitelist-source-range: "10.0.0.0/8,192.168.0.0/16"
```

## HTTPS 配置

### 方式 1: 使用已有证书

```bash
# 创建 TLS Secret
kubectl create secret tls llm-guard-tls \
  --cert=path/to/cert.crt \
  --key=path/to/cert.key \
  -n your-namespace
```

```yaml
spec:
  tls:
  - hosts:
    - llm-guard.example.com
    secretName: llm-guard-tls
```

### 方式 2: 使用 cert-manager 自动签发

```bash
# 安装 cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# 创建 ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

```yaml
metadata:
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - llm-guard.example.com
    secretName: llm-guard-tls-auto  # cert-manager 会自动创建
```

## 部署和验证

### 1. 应用配置

```bash
# 应用 Ingress 配置
kubectl apply -f k8s-ingress-example.yaml

# 查看 Ingress 状态
kubectl get ingress -n your-namespace

# 查看详细信息
kubectl describe ingress llm-guard-ingress -n your-namespace
```

### 2. 验证路由

```bash
# 获取 Ingress IP
INGRESS_IP=$(kubectl get ingress llm-guard-ingress -n your-namespace -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# 测试前端
curl -H "Host: llm-guard.example.com" http://$INGRESS_IP/

# 测试 API
curl -H "Host: llm-guard.example.com" http://$INGRESS_IP/api/v1/docs
```

### 3. 查看日志

```bash
# 查看 Ingress Controller 日志
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx -f

# 查看特定请求的路由
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx | grep "llm-guard"
```

## 常见问题

### 1. 404 Not Found

**原因**: 路径匹配不正确

**排查**:
```bash
# 检查 Ingress 配置
kubectl describe ingress llm-guard-ingress -n your-namespace

# 查看 Ingress Controller 日志
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx --tail=100
```

**解决**:
- 确认路径类型（Prefix/Exact）
- 检查路径顺序（更具体的在前）
- 验证 Service 名称和端口

### 2. 502 Bad Gateway

**原因**: 后端服务不可达

**排查**:
```bash
# 检查 Service
kubectl get svc llm-guard-backend-svc -n your-namespace

# 检查 Endpoints
kubectl get endpoints llm-guard-backend-svc -n your-namespace

# 检查 Pod
kubectl get pods -l app=llm-guard-backend -n your-namespace
```

### 3. CORS 错误

**原因**: 跨域配置不正确

**解决**:
```yaml
annotations:
  nginx.ingress.kubernetes.io/enable-cors: "true"
  nginx.ingress.kubernetes.io/cors-allow-origin: "https://your-frontend-domain.com"
  nginx.ingress.kubernetes.io/cors-allow-credentials: "true"
```

### 4. 路径重写不生效

**原因**: rewrite-target 配置错误

**示例**:
```yaml
# 错误
path: /api
rewrite-target: /

# 正确
path: /api(/|$)(.*)
rewrite-target: /$2
```

## 推荐配置

### 生产环境推荐配置

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: llm-guard-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://llm-guard.example.com"
    nginx.ingress.kubernetes.io/limit-rps: "100"
spec:
  tls:
  - hosts:
    - llm-guard.example.com
    secretName: llm-guard-tls
  rules:
  - host: llm-guard.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: llm-guard-backend-svc
            port:
              number: 9001
      - path: /
        pathType: Prefix
        backend:
          service:
            name: llm-guard-frontend-svc
            port:
              number: 80
```

## 监控和调试

### 查看 Ingress 配置

```bash
# 查看 Ingress 生成的 Nginx 配置
kubectl exec -n ingress-nginx <ingress-controller-pod> -- cat /etc/nginx/nginx.conf | grep -A 20 "llm-guard"
```

### 实时监控请求

```bash
# 实时查看访问日志
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx -f | grep "llm-guard"
```

### 性能测试

```bash
# 使用 ab 进行压力测试
ab -n 1000 -c 10 https://llm-guard.example.com/api/v1/tags
```
