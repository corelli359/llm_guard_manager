# 子路径部署指南

本文档说明如何将 LLM Guard Manager 部署在子路径下（如 `/db_web/`）。

## 问题说明

当应用部署在子路径下时，会遇到以下问题：

1. **静态资源 404**: JS/CSS 文件从根路径加载，导致 404
   - 期望: `https://domain.com/db_web/assets/index.js`
   - 实际: `https://domain.com/assets/index.js` ❌

2. **API 请求路径错误**: API 请求路径不包含子路径前缀
   - 期望: `https://domain.com/db_web/api/v1/tags`
   - 实际: `https://domain.com/api/v1/tags` ❌

3. **前端路由失效**: React Router 路由不匹配

## 解决方案

### 方案 1: 构建时指定 base path（推荐）

#### 1. 构建镜像时指定子路径

```bash
cd frontend

# 使用构建脚本
./build-subpath.sh /db_web/ v1.0

# 或直接使用 docker build
docker build \
  --build-arg VITE_BASE_PATH=/db_web/ \
  -t your-registry/llm-guard-frontend:v1.0 \
  .
```

#### 2. 配置 Ingress（不需要 rewrite）

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: llm-guard-ingress
  namespace: your-namespace
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  rules:
  - host: your-domain.com
    http:
      paths:
      # API 路由
      - path: /db_web/api
        pathType: Prefix
        backend:
          service:
            name: llm-guard-backend-svc
            port:
              number: 9001

      # 前端路由
      - path: /db_web
        pathType: Prefix
        backend:
          service:
            name: llm-guard-frontend-svc
            port:
              number: 80
```

#### 3. 部署

```bash
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-ingress-subpath.yaml
```

#### 4. 访问

- 前端: `https://your-domain.com/db_web/`
- API: `https://your-domain.com/db_web/api/v1/tags`

### 方案 2: 使用 Ingress rewrite（你当前的方案）

如果你想继续使用 rewrite，需要确保前端构建时指定了正确的 base path。

#### 1. 构建镜像（指定 base path）

```bash
docker build \
  --build-arg VITE_BASE_PATH=/db_web/ \
  -t your-registry/llm-guard-frontend:v1.0 \
  .
```

#### 2. 配置 Ingress（使用 rewrite）

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: llm-guard-ingress
  namespace: your-namespace
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/use-regex: "true"
spec:
  rules:
  - host: your-domain.com
    http:
      paths:
      # API 路由
      - path: /db_web/api(/|$)(.*)
        pathType: ImplementationSpecific
        backend:
          service:
            name: llm-guard-backend-svc
            port:
              number: 9001

      # 前端路由
      - path: /db_web(/|$)(.*)
        pathType: ImplementationSpecific
        backend:
          service:
            name: llm-guard-frontend-svc
            port:
              number: 80
```

**注意**: 使用 rewrite 时，后端收到的请求路径会被重写：
- 外部请求: `/db_web/api/v1/tags`
- 后端收到: `/api/v1/tags`

### 方案 3: 使用环境变量文件

如果你有多个部署环境，可以使用不同的 `.env` 文件：

```bash
# 根路径部署
npm run build

# 子路径部署
npm run build -- --mode production.subpath
```

创建 `.env.production.subpath`:
```
VITE_BASE_PATH=/db_web/
```

## 验证部署

### 1. 检查静态资源路径

访问前端页面，查看 HTML 源码：

```html
<!-- 正确：包含子路径 -->
<script type="module" src="/db_web/assets/index-abc123.js"></script>
<link rel="stylesheet" href="/db_web/assets/index-def456.css">

<!-- 错误：缺少子路径 -->
<script type="module" src="/assets/index-abc123.js"></script>
```

### 2. 检查 API 请求路径

打开浏览器开发者工具 Network 面板，查看 API 请求：

```
✓ 正确: https://domain.com/db_web/api/v1/tags
✗ 错误: https://domain.com/api/v1/tags
```

### 3. 检查前端路由

访问以下 URL，确保路由正常：
- `https://domain.com/db_web/` - 首页
- `https://domain.com/db_web/apps` - 应用列表
- `https://domain.com/db_web/playground` - 测试页面

刷新页面时不应该出现 404。

## 常见问题

### 1. JS/CSS 文件 404

**原因**: 构建时未指定 base path

**解决**:
```bash
# 重新构建镜像，指定 base path
docker build --build-arg VITE_BASE_PATH=/db_web/ -t your-image .
```

### 2. API 请求 404

**原因**: API 请求路径不正确

**排查**:
```bash
# 查看前端容器日志
kubectl logs <frontend-pod> -n your-namespace

# 查看 Ingress 日志
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx | grep db_web
```

**解决**: 确保 Ingress 配置正确，API 路径包含子路径前缀。

### 3. 前端路由刷新 404

**原因**: Nginx 配置不正确

**解决**: 确保 Nginx 配置包含 SPA 路由支持：
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### 4. 后端收到的路径不正确

**原因**: Ingress rewrite 配置问题

**示例**:
```yaml
# 如果使用 rewrite-target: /$2
# 外部: /db_web/api/v1/tags
# 后端收到: /api/v1/tags ✓

# 如果使用 rewrite-target: /
# 外部: /db_web/api/v1/tags
# 后端收到: / ✗
```

## 本地开发

本地开发时不需要子路径：

```bash
cd frontend
npm run dev
# 访问 http://localhost:5173
```

如果需要测试子路径部署：

```bash
# 1. 构建生产版本
VITE_BASE_PATH=/db_web/ npm run build

# 2. 使用 serve 测试
npx serve -s dist -l 8080

# 3. 配置本地 Nginx 代理
# 将 /db_web/ 代理到 http://localhost:8080/db_web/
```

## 多环境配置

### 开发环境（根路径）
```bash
npm run dev
# base: '/'
```

### 测试环境（子路径）
```bash
VITE_BASE_PATH=/db_web/ npm run build
# base: '/db_web/'
```

### 生产环境（根路径）
```bash
npm run build
# base: '/'
```

## 最佳实践

1. **推荐使用方案 1**（构建时指定 base path，Ingress 不使用 rewrite）
   - 配置简单
   - 路径清晰
   - 易于调试

2. **使用构建参数**而不是环境变量文件
   - 更灵活
   - 避免维护多个 .env 文件

3. **在 CI/CD 中配置**
   ```yaml
   # GitLab CI 示例
   build:
     script:
       - docker build --build-arg VITE_BASE_PATH=/db_web/ -t $IMAGE .
   ```

4. **文档化部署路径**
   - 在 README 中说明当前部署的子路径
   - 提供不同环境的构建命令

## 总结

**关键点**:
1. 构建时必须指定 `VITE_BASE_PATH`
2. Ingress 路径配置要与 base path 匹配
3. API 请求会自动包含 base path 前缀
4. 前端路由会自动适配 base path

**构建命令**:
```bash
# 子路径部署
docker build --build-arg VITE_BASE_PATH=/db_web/ -t your-image .

# 根路径部署
docker build -t your-image .
```
