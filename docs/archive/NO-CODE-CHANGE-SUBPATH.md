# 不修改代码的子路径部署方案

本方案通过纯 Nginx 配置解决子路径部署问题，**不需要修改前端代码或重新构建**。

## 方案原理

使用 Nginx 的以下功能：
1. **sub_filter**: 动态替换 HTML 中的静态资源路径
2. **location + alias**: 映射静态资源路径
3. **rewrite**: 处理 API 和前端路由

## 实施步骤

### 步骤 1: 替换 Nginx 配置

使用 ConfigMap 挂载新的 Nginx 配置：

```yaml
---
# ConfigMap: Nginx 配置
apiVersion: v1
kind: ConfigMap
metadata:
  name: llm-guard-frontend-nginx-config
  namespace: your-namespace
data:
  default.conf: |
    server {
        listen 8080;
        server_name _;

        root /usr/share/nginx/html;
        index index.html;

        # 动态替换 HTML 中的路径
        sub_filter_once off;
        sub_filter_types text/html;
        sub_filter '"/assets/' '"/db_web/assets/';
        sub_filter "'/assets/" "'/db_web/assets/";
        sub_filter 'src="/assets/' 'src="/db_web/assets/';
        sub_filter 'href="/assets/' 'href="/db_web/assets/';

        # 静态资源路径映射
        location ~ ^/db_web/assets/(.*)$ {
            alias /usr/share/nginx/html/assets/$1;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # API 代理
        location /db_web/api/ {
            rewrite ^/db_web(/api/.*)$ $1 break;
            proxy_pass http://llm-guard-backend-svc.your-namespace.svc.cluster.local:9001;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 前端路由
        location /db_web/ {
            rewrite ^/db_web/(.*)$ /$1 break;
            try_files $uri $uri/ /index.html;
        }

        # 根路径（可选）
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Gzip 压缩
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript;
    }

---
# Deployment: 挂载 ConfigMap
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-guard-frontend
  namespace: your-namespace
spec:
  replicas: 2
  selector:
    matchLabels:
      app: llm-guard-frontend
  template:
    metadata:
      labels:
        app: llm-guard-frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/llm-guard-frontend:latest
        ports:
        - containerPort: 8080
        volumeMounts:
        # 挂载 Nginx 配置
        - name: nginx-config
          mountPath: /etc/nginx/conf.d/default.conf
          subPath: default.conf
      volumes:
      - name: nginx-config
        configMap:
          name: llm-guard-frontend-nginx-config
```

### 步骤 2: 配置 Ingress

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
      # 前端（包含 API 和静态资源）
      - path: /db_web
        pathType: Prefix
        backend:
          service:
            name: llm-guard-frontend-svc
            port:
              number: 80
```

### 步骤 3: 应用配置

```bash
# 应用配置
kubectl apply -f k8s-deployment-with-configmap.yaml

# 重启 Pod 使配置生效
kubectl rollout restart deployment/llm-guard-frontend -n your-namespace

# 查看状态
kubectl get pods -n your-namespace
```

## 工作原理

### 1. 静态资源加载

**原始 HTML**:
```html
<script src="/assets/index-abc123.js"></script>
```

**Nginx sub_filter 处理后**:
```html
<script src="/db_web/assets/index-abc123.js"></script>
```

**请求流程**:
```
浏览器请求: /db_web/assets/index-abc123.js
    ↓
Nginx location 匹配: ^/db_web/assets/(.*)$
    ↓
alias 映射: /usr/share/nginx/html/assets/index-abc123.js
    ↓
返回文件 ✓
```

### 2. API 请求

**前端代码**:
```javascript
axios.get('/api/v1/tags')
```

**浏览器实际请求**:
```
/api/v1/tags (相对路径，基于当前页面 /db_web/)
→ /db_web/api/v1/tags
```

**Nginx 处理**:
```
location /db_web/api/
    ↓
rewrite: /db_web/api/v1/tags → /api/v1/tags
    ↓
proxy_pass 到后端 ✓
```

### 3. 前端路由

**用户访问**: `https://domain.com/db_web/apps`

**Nginx 处理**:
```
location /db_web/
    ↓
rewrite: /db_web/apps → /apps
    ↓
try_files: /apps → /apps/ → /index.html
    ↓
返回 index.html ✓
```

## 验证

### 1. 检查 ConfigMap

```bash
kubectl get configmap llm-guard-frontend-nginx-config -n your-namespace -o yaml
```

### 2. 检查 Nginx 配置

```bash
kubectl exec -it <frontend-pod> -n your-namespace -- cat /etc/nginx/conf.d/default.conf
```

### 3. 测试静态资源

```bash
# 进入 Pod
kubectl exec -it <frontend-pod> -n your-namespace -- sh

# 测试路径映射
curl http://localhost:8080/db_web/assets/index.js
```

### 4. 测试 API

```bash
# 测试 API 代理
curl http://localhost:8080/db_web/api/v1/docs
```

### 5. 浏览器测试

访问 `https://your-domain.com/db_web/`，打开开发者工具：

1. **Network 面板**: 检查所有资源是否正常加载
2. **Console 面板**: 检查是否有 404 错误
3. **查看 HTML 源码**: 确认路径已被替换

## 优势

1. **无需重新构建**: 使用现有的镜像
2. **配置灵活**: 通过 ConfigMap 管理，易于修改
3. **快速部署**: 只需更新 ConfigMap 和重启 Pod
4. **零代码改动**: 前端代码完全不需要修改

## 注意事项

### 1. sub_filter 的限制

- 只能替换文本内容（HTML、CSS、JS）
- 不能替换二进制文件
- 可能影响性能（需要解析 HTML）

### 2. 缓存问题

如果启用了 Nginx 缓存，sub_filter 可能不生效：

```nginx
# 禁用缓存（开发环境）
add_header Cache-Control "no-cache, no-store, must-revalidate";

# 或者配置缓存时排除 HTML
location ~ \.html$ {
    add_header Cache-Control "no-cache";
}
```

### 3. API 路径问题

如果前端代码中使用了绝对路径（如 `http://domain.com/api/v1/tags`），sub_filter 无法处理。

确保前端使用相对路径：
```javascript
// ✓ 正确：相对路径
axios.get('/api/v1/tags')

// ✗ 错误：绝对路径
axios.get('http://domain.com/api/v1/tags')
```

## 故障排查

### 问题 1: 静态资源仍然 404

**排查**:
```bash
# 检查 sub_filter 是否生效
kubectl exec -it <frontend-pod> -n your-namespace -- sh
curl http://localhost:8080/db_web/ | grep assets

# 应该看到 /db_web/assets/ 而不是 /assets/
```

**解决**: 确认 ConfigMap 已正确挂载，重启 Pod。

### 问题 2: API 请求失败

**排查**:
```bash
# 查看 Nginx 日志
kubectl logs <frontend-pod> -n your-namespace

# 测试 API 代理
kubectl exec -it <frontend-pod> -n your-namespace -- sh
curl http://localhost:8080/db_web/api/v1/docs
```

**解决**: 检查后端服务地址是否正确。

### 问题 3: 前端路由刷新 404

**排查**:
```bash
# 测试路由
curl http://localhost:8080/db_web/apps
# 应该返回 index.html 的内容
```

**解决**: 确认 `try_files` 配置正确。

## 性能优化

### 1. 只对 HTML 使用 sub_filter

```nginx
sub_filter_types text/html;  # 只处理 HTML
```

### 2. 静态资源缓存

```nginx
location ~ ^/db_web/assets/(.*)$ {
    alias /usr/share/nginx/html/assets/$1;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. Gzip 压缩

```nginx
gzip on;
gzip_types text/plain text/css application/javascript application/json;
gzip_min_length 1024;
```

## 回滚方案

如果出现问题，快速回滚：

```bash
# 删除 ConfigMap
kubectl delete configmap llm-guard-frontend-nginx-config -n your-namespace

# 重启 Pod（使用镜像内置的 Nginx 配置）
kubectl rollout restart deployment/llm-guard-frontend -n your-namespace
```

## 总结

这个方案的核心是：
1. **sub_filter** 动态替换 HTML 中的路径
2. **location + alias** 映射静态资源
3. **rewrite** 处理 API 和路由

**优点**: 不需要修改代码，不需要重新构建
**缺点**: 依赖 Nginx 配置，略微增加复杂度

如果你的应用需要频繁更新或有多个部署环境，建议还是使用构建时指定 base path 的方案（方案 1）。
