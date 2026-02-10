# 使用 dist 挂载的灵活子路径部署方案

本方案适用于已有 dist 构建产物，通过 Volume 挂载到标准 Nginx 镜像的场景。

## 方案特点

- ✅ 使用标准 Nginx 镜像（nginx:alpine）
- ✅ dist 文件通过 Volume 挂载
- ✅ 通过 initContainer 动态生成 Nginx 配置
- ✅ 支持任意子路径，通过环境变量配置
- ✅ 无需自定义 Dockerfile

## 架构说明

```
Pod 启动
    ↓
initContainer (busybox)
    ├─ 读取环境变量 BASE_PATH
    ├─ 生成 Nginx 配置文件
    └─ 写入共享 Volume
    ↓
Nginx 容器启动
    ├─ 挂载 dist 文件（PVC/HostPath/ConfigMap）
    ├─ 挂载 Nginx 配置（从 initContainer）
    └─ 启动服务
```

## 部署步骤

### 方案 1: 使用 PVC 挂载 dist（推荐）

#### 1. 准备 dist 文件

```bash
# 本地构建
cd frontend
npm run build

# 将 dist 上传到 PVC
kubectl cp dist/ <pod-name>:/data/dist -n your-namespace
```

#### 2. 应用 K8s 配置

```bash
kubectl apply -f k8s-deployment-mount-dist.yaml
```

### 方案 2: 使用 HostPath 挂载 dist

适用于单节点或已将 dist 同步到所有节点的场景。

```bash
# 将 dist 复制到节点
scp -r dist/ user@node:/data/llm-guard/dist/

# 应用配置
kubectl apply -f k8s-deployment-mount-dist.yaml
```

### 方案 3: 使用 ConfigMap 挂载 dist（小型应用）

适用于 dist 文件较小的场景（< 1MB）。

```bash
# 创建 ConfigMap
kubectl create configmap llm-guard-dist \
  --from-file=dist/ \
  -n your-namespace

# 应用配置
kubectl apply -f k8s-deployment-mount-dist.yaml
```

## 配置说明

### 环境变量

#### BASE_PATH（必需）

子路径名称：

```yaml
env:
- name: BASE_PATH
  value: "/db_web"    # 子路径
  # value: "/admin"   # 或其他路径
  # value: "/"        # 根路径
```

#### BACKEND_SERVICE_URL（必需）

后端服务地址：

```yaml
env:
- name: BACKEND_SERVICE_URL
  value: "http://backend-svc.namespace.svc.cluster.local:9001"
```

### Volume 配置

根据你的存储方式选择：

#### PVC（推荐）

```yaml
volumes:
- name: dist-files
  persistentVolumeClaim:
    claimName: llm-guard-dist-pvc
```

#### HostPath

```yaml
volumes:
- name: dist-files
  hostPath:
    path: /data/llm-guard/dist
    type: Directory
```

#### NFS

```yaml
volumes:
- name: dist-files
  nfs:
    server: nfs-server.example.com
    path: /exports/llm-guard/dist
```

#### ConfigMap（小文件）

```yaml
volumes:
- name: dist-files
  configMap:
    name: llm-guard-dist
```

## 更新 dist 文件

### 方式 1: 直接更新 PVC

```bash
# 找到一个运行中的 Pod
POD_NAME=$(kubectl get pods -n your-namespace -l app=llm-guard-frontend -o jsonpath='{.items[0].metadata.name}')

# 上传新的 dist 文件
kubectl cp dist/ $POD_NAME:/usr/share/nginx/html -n your-namespace

# 重启 Pod 使配置生效（如果需要）
kubectl rollout restart deployment/llm-guard-frontend -n your-namespace
```

### 方式 2: 使用临时 Pod 更新

```bash
# 创建临时 Pod
kubectl run dist-updater \
  --image=busybox \
  --restart=Never \
  --overrides='
{
  "spec": {
    "containers": [{
      "name": "updater",
      "image": "busybox",
      "command": ["sleep", "3600"],
      "volumeMounts": [{
        "name": "dist",
        "mountPath": "/dist"
      }]
    }],
    "volumes": [{
      "name": "dist",
      "persistentVolumeClaim": {
        "claimName": "llm-guard-dist-pvc"
      }
    }]
  }
}' \
  -n your-namespace

# 上传文件
kubectl cp dist/ dist-updater:/dist -n your-namespace

# 删除临时 Pod
kubectl delete pod dist-updater -n your-namespace
```

### 方式 3: 使用 Job 自动构建和更新

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: build-and-deploy-frontend
spec:
  template:
    spec:
      containers:
      - name: builder
        image: node:18-alpine
        command:
        - sh
        - -c
        - |
          cd /workspace
          npm ci
          npm run build
          cp -r dist/* /output/
        volumeMounts:
        - name: source
          mountPath: /workspace
        - name: dist
          mountPath: /output
      volumes:
      - name: source
        gitRepo:
          repository: "https://github.com/your/repo.git"
          revision: "main"
      - name: dist
        persistentVolumeClaim:
          claimName: llm-guard-dist-pvc
      restartPolicy: Never
```

## 修改子路径

只需修改环境变量，无需重新构建：

```bash
# 方式 1: 使用 kubectl set env
kubectl set env deployment/llm-guard-frontend \
  BASE_PATH=/new-path \
  -n your-namespace

# 方式 2: 使用 kubectl edit
kubectl edit deployment llm-guard-frontend -n your-namespace
# 修改 env.BASE_PATH 的值

# 方式 3: 使用 kubectl patch
kubectl patch deployment llm-guard-frontend -n your-namespace \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/env/0/value", "value": "/new-path"}]'
```

修改后 Pod 会自动重启，新配置生效。

## 验证部署

### 1. 检查 Pod 状态

```bash
kubectl get pods -n your-namespace -l app=llm-guard-frontend
```

### 2. 查看 initContainer 日志

```bash
kubectl logs <pod-name> -c init-nginx-config -n your-namespace

# 应该看到：
# Generating Nginx config...
# BASE_PATH: /db_web
# BACKEND_SERVICE_URL: http://backend-svc:9001
# Config generated successfully
```

### 3. 查看生成的 Nginx 配置

```bash
kubectl exec <pod-name> -n your-namespace -- cat /etc/nginx/conf.d/default.conf
```

### 4. 检查 dist 文件

```bash
kubectl exec <pod-name> -n your-namespace -- ls -la /usr/share/nginx/html
```

### 5. 测试访问

```bash
# 端口转发
kubectl port-forward svc/llm-guard-frontend-svc 8080:80 -n your-namespace

# 测试
curl http://localhost:8080/db_web/
```

## 常见问题

### 1. dist 文件未挂载

**症状**: 访问返回 404 或 403

**排查**:
```bash
kubectl exec <pod-name> -n your-namespace -- ls -la /usr/share/nginx/html
```

**解决**: 检查 Volume 配置和挂载路径。

### 2. Nginx 配置未生成

**症状**: Nginx 启动失败

**排查**:
```bash
kubectl logs <pod-name> -c init-nginx-config -n your-namespace
kubectl describe pod <pod-name> -n your-namespace
```

**解决**: 检查 initContainer 是否成功执行。

### 3. 修改 BASE_PATH 后不生效

**原因**: Pod 未重启

**解决**:
```bash
kubectl rollout restart deployment/llm-guard-frontend -n your-namespace
```

### 4. PVC 权限问题

**症状**: initContainer 或 Nginx 无法读写文件

**解决**:
```yaml
spec:
  securityContext:
    fsGroup: 101  # nginx 用户组
```

## 性能优化

### 1. 使用本地 PV

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: llm-guard-dist-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
  - ReadOnlyMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-storage
  local:
    path: /data/llm-guard/dist
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - node1
          - node2
```

### 2. 使用 ReadOnlyMany

```yaml
volumeMounts:
- name: dist-files
  mountPath: /usr/share/nginx/html
  readOnly: true  # 只读挂载，提高性能
```

### 3. 缓存静态资源

Nginx 配置已包含缓存设置：

```nginx
location ~ ^/db_web/assets/(.*)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## CI/CD 集成

### GitLab CI 示例

```yaml
stages:
  - build
  - deploy

build:
  stage: build
  image: node:18-alpine
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/

deploy:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    # 上传 dist 到 PVC
    - kubectl run dist-updater --image=busybox --restart=Never --overrides="..." -n $NAMESPACE
    - kubectl cp dist/ dist-updater:/dist -n $NAMESPACE
    - kubectl delete pod dist-updater -n $NAMESPACE

    # 更新环境变量（如果需要）
    - kubectl set env deployment/llm-guard-frontend BASE_PATH=$BASE_PATH -n $NAMESPACE

    # 重启 Pod
    - kubectl rollout restart deployment/llm-guard-frontend -n $NAMESPACE
```

## 总结

**优势**:
- 使用标准 Nginx 镜像
- dist 文件独立管理
- 配置灵活，易于更新
- 支持多种存储方式

**适用场景**:
- 已有 CI/CD 构建流程
- dist 文件需要独立管理
- 多环境共享 dist 文件
- 不想维护自定义镜像

**关键配置**:
1. initContainer 生成 Nginx 配置
2. Volume 挂载 dist 文件
3. 环境变量配置子路径
