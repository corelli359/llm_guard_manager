# 灵活子路径部署指南

本方案支持通过环境变量配置任意子路径，无需修改代码或重新构建镜像。

## 核心特性

- ✅ **任意子路径**: 通过环境变量 `BASE_PATH` 配置，支持 `/db_web`, `/admin`, `/app` 等任意路径
- ✅ **根路径支持**: 设置 `BASE_PATH=/` 即可部署在根路径
- ✅ **无需重新构建**: 同一个镜像可以部署在不同的子路径
- ✅ **动态配置**: 容器启动时自动生成 Nginx 配置

## 快速开始

### 1. 构建镜像（一次构建，到处使用）

```bash
cd frontend

# 使用新的 Dockerfile
docker build -f Dockerfile.flexible -t your-registry/llm-guard-frontend:flexible .

# 推送镜像
docker push your-registry/llm-guard-frontend:flexible
```

### 2. 部署到不同的子路径

#### 场景 A: 部署在 /db_web

```yaml
env:
- name: BASE_PATH
  value: "/db_web"
```

```yaml
# Ingress
paths:
- path: /db_web
  pathType: Prefix
```

访问: `https://domain.com/db_web/`

#### 场景 B: 部署在 /admin

```yaml
env:
- name: BASE_PATH
  value: "/admin"
```

```yaml
# Ingress
paths:
- path: /admin
  pathType: Prefix
```

访问: `https://domain.com/admin/`

#### 场景 C: 部署在根路径

```yaml
env:
- name: BASE_PATH
  value: "/"
```

```yaml
# Ingress
paths:
- path: /
  pathType: Prefix
```

访问: `https://domain.com/`

### 3. 部署

```bash
# 修改 k8s-deployment-flexible.yaml
# 1. 设置 BASE_PATH 环境变量
# 2. 修改 Ingress path 以匹配 BASE_PATH

kubectl apply -f k8s-deployment-flexible.yaml
```

## 配置说明

### 环境变量

#### BASE_PATH（必需）

子路径名称，支持以下格式：

```yaml
# 子路径（推荐格式：以 / 开头，不以 / 结尾）
BASE_PATH: "/db_web"
BASE_PATH: "/admin"
BASE_PATH: "/llm-guard"

# 根路径
BASE_PATH: "/"

# 也支持以下格式（会自动处理）
BASE_PATH: "/db_web/"  # 自动去掉尾部斜杠
BASE_PATH: "db_web"    # 自动添加前导斜杠
```

#### BACKEND_SERVICE_URL（必需）

后端服务地址：

```yaml
# Kubernetes 内部服务
BACKEND_SERVICE_URL: "http://backend-svc.namespace.svc.cluster.local:9001"

# 外部服务
BACKEND_SERVICE_URL: "https://api.example.com"
```

### Ingress 配置

Ingress 的 path 必须与 BASE_PATH 匹配：

```yaml
# 如果 BASE_PATH=/db_web
paths:
- path: /db_web
  pathType: Prefix

# 如果 BASE_PATH=/admin
paths:
- path: /admin
  pathType: Prefix

# 如果 BASE_PATH=/
paths:
- path: /
  pathType: Prefix
```

## 工作原理

### 1. 容器启动流程

```
容器启动
    ↓
执行 docker-entrypoint.sh
    ↓
读取环境变量 BASE_PATH
    ↓
动态生成 Nginx 配置
    ↓
启动 Nginx
```

### 2. Nginx 配置生成

**子路径部署** (BASE_PATH=/db_web):

```nginx
# 替换 HTML 中的路径
sub_filter '"/assets/' '"/db_web/assets/';

# 静态资源映射
location ~ ^/db_web/assets/(.*)$ {
    alias /usr/share/nginx/html/assets/$1;
}

# API 代理
location /db_web/api/ {
    rewrite ^/db_web(/api/.*)$ $1 break;
    proxy_pass http://backend:9001;
}

# 前端路由
location /db_web/ {
    rewrite ^/db_web/(.*)$ /$1 break;
    try_files $uri $uri/ /index.html;
}
```

**根路径部署** (BASE_PATH=/):

```nginx
# 不需要路径替换
sub_filter '"/assets/' '"/assets/';

# API 代理
location /api/ {
    proxy_pass http://backend:9001;
}

# 前端路由
location / {
    try_files $uri $uri/ /index.html;
}
```

## 多环境部署示例

### 示例 1: 同一集群，不同子路径

```yaml
# 开发环境
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-guard-dev
spec:
  template:
    spec:
      containers:
      - name: frontend
        env:
        - name: BASE_PATH
          value: "/dev"
---
# Ingress
paths:
- path: /dev
  backend:
    service:
      name: llm-guard-dev-svc

# 测试环境
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-guard-test
spec:
  template:
    spec:
      containers:
      - name: frontend
        env:
        - name: BASE_PATH
          value: "/test"
---
# Ingress
paths:
- path: /test
  backend:
    service:
      name: llm-guard-test-svc

# 生产环境（根路径）
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-guard-prod
spec:
  template:
    spec:
      containers:
      - name: frontend
        env:
        - name: BASE_PATH
          value: "/"
---
# Ingress
paths:
- path: /
  backend:
    service:
      name: llm-guard-prod-svc
```

访问:
- 开发: `https://platform.com/dev/`
- 测试: `https://platform.com/test/`
- 生产: `https://platform.com/`

### 示例 2: 多服务共存

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: platform-ingress
spec:
  rules:
  - host: platform.example.com
    http:
      paths:
      # LLM Guard
      - path: /llm-guard
        pathType: Prefix
        backend:
          service:
            name: llm-guard-svc
            port:
              number: 80

      # 用户管理
      - path: /user-admin
        pathType: Prefix
        backend:
          service:
            name: user-admin-svc
            port:
              number: 80

      # 监控面板
      - path: /monitoring
        pathType: Prefix
        backend:
          service:
            name: monitoring-svc
            port:
              number: 80

      # 默认服务
      - path: /
        pathType: Prefix
        backend:
          service:
            name: default-svc
            port:
              number: 80
```

## 验证部署

### 1. 检查环境变量

```bash
kubectl exec -it <frontend-pod> -n your-namespace -- env | grep BASE_PATH
```

### 2. 查看生成的 Nginx 配置

```bash
kubectl exec -it <frontend-pod> -n your-namespace -- cat /etc/nginx/conf.d/default.conf
```

### 3. 查看容器日志

```bash
kubectl logs <frontend-pod> -n your-namespace

# 应该看到类似输出：
# ==========================================
# Nginx 配置初始化
# BASE_PATH: /db_web
# BACKEND_SERVICE_URL: http://backend-svc:9001
# ==========================================
# 部署在子路径: /db_web
# Nginx 配置生成完成
```

### 4. 测试访问

```bash
# 测试前端
curl https://your-domain.com/db_web/

# 测试静态资源
curl https://your-domain.com/db_web/assets/index.js

# 测试 API
curl https://your-domain.com/db_web/api/v1/docs
```

## 本地测试

```bash
# 构建镜像
docker build -f Dockerfile.flexible -t llm-guard-frontend:test .

# 测试子路径部署
docker run -d -p 8080:8080 \
  -e BASE_PATH=/db_web \
  -e BACKEND_SERVICE_URL=http://host.docker.internal:9001 \
  llm-guard-frontend:test

# 访问（注意：本地测试时需要通过子路径访问）
curl http://localhost:8080/db_web/

# 测试根路径部署
docker run -d -p 8081:8080 \
  -e BASE_PATH=/ \
  -e BACKEND_SERVICE_URL=http://host.docker.internal:9001 \
  llm-guard-frontend:test

# 访问
curl http://localhost:8081/
```

## 常见问题

### 1. 修改 BASE_PATH 后不生效

**原因**: Pod 没有重启

**解决**:
```bash
kubectl rollout restart deployment/llm-guard-frontend -n your-namespace
```

### 2. 静态资源 404

**原因**: Ingress path 与 BASE_PATH 不匹配

**检查**:
```bash
# 查看环境变量
kubectl exec <pod> -n your-namespace -- env | grep BASE_PATH

# 查看 Ingress 配置
kubectl get ingress -n your-namespace -o yaml | grep path
```

**解决**: 确保 Ingress path 与 BASE_PATH 一致。

### 3. API 请求失败

**原因**: BACKEND_SERVICE_URL 配置错误

**检查**:
```bash
# 进入容器测试后端连接
kubectl exec -it <pod> -n your-namespace -- sh
wget -O- http://backend-svc.namespace.svc.cluster.local:9001/api/v1/docs
```

**解决**: 修正 BACKEND_SERVICE_URL。

## 最佳实践

### 1. 使用 ConfigMap 管理配置

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: llm-guard-config
data:
  BASE_PATH: "/db_web"
  BACKEND_SERVICE_URL: "http://backend-svc:9001"
---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: frontend
        envFrom:
        - configMapRef:
            name: llm-guard-config
```

### 2. 使用 Kustomize 管理多环境

```bash
# base/kustomization.yaml
resources:
- deployment.yaml
- service.yaml
- ingress.yaml

# overlays/dev/kustomization.yaml
bases:
- ../../base
patchesStrategicMerge:
- deployment-patch.yaml

# overlays/dev/deployment-patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-guard-frontend
spec:
  template:
    spec:
      containers:
      - name: frontend
        env:
        - name: BASE_PATH
          value: "/dev"
```

### 3. 在 CI/CD 中使用

```yaml
# GitLab CI 示例
deploy:
  script:
    - kubectl set env deployment/llm-guard-frontend BASE_PATH=/db_web -n $NAMESPACE
    - kubectl rollout restart deployment/llm-guard-frontend -n $NAMESPACE
```

## 总结

**优势**:
- 一次构建，多处部署
- 灵活配置子路径
- 无需修改代码
- 支持多环境部署

**使用场景**:
- 多服务共享域名
- 多环境部署（dev/test/prod）
- 需要频繁更改子路径
- 微前端架构

**关键配置**:
1. 构建时使用 `Dockerfile.flexible`
2. 部署时设置 `BASE_PATH` 环境变量
3. Ingress path 与 BASE_PATH 保持一致
