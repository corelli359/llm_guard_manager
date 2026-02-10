# K8s部署配置示例

## 前端Deployment

```yaml
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
        - containerPort: 80
        env:
        - name: VITE_BASE_PATH
          value: "/web-manager/"
        - name: VITE_API_BASE_URL
          value: "/dbmanage/api/v1"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /web-manager/
            port: 80
          initialDelaySeconds: 30
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
  name: llm-guard-frontend-service
  namespace: your-namespace
spec:
  selector:
    app: llm-guard-frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: ClusterIP
```

## 后端Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-guard-backend
  namespace: your-namespace
spec:
  replicas: 3
  selector:
    matchLabels:
      app: llm-guard-backend
  template:
    metadata:
      labels:
        app: llm-guard-backend
    spec:
      containers:
      - name: backend
        image: your-registry/llm-guard-backend:latest
        ports:
        - containerPort: 9001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: llm-guard-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: llm-guard-secrets
              key: secret-key
        - name: CORS_ORIGINS
          value: "*"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 9001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 9001
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: llm-guard-backend-service
  namespace: your-namespace
spec:
  selector:
    app: llm-guard-backend
  ports:
  - protocol: TCP
    port: 9001
    targetPort: 9001
  type: ClusterIP
```

## Ingress配置

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: llm-guard-ingress
  namespace: your-namespace
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
spec:
  ingressClassName: nginx
  rules:
  - host: your-domain.com
    http:
      paths:
      # 前端路由
      - path: /web-manager(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: llm-guard-frontend-service
            port:
              number: 80
      # 后端API路由
      - path: /dbmanage/api/v1(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: llm-guard-backend-service
            port:
              number: 9001
  tls:
  - hosts:
    - your-domain.com
    secretName: your-tls-secret
```

## ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: llm-guard-config
  namespace: your-namespace
data:
  frontend.env: |
    VITE_BASE_PATH=/web-manager/
    VITE_API_BASE_URL=/dbmanage/api/v1
  backend.env: |
    CORS_ORIGINS=*
    LOG_LEVEL=INFO
```

## Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: llm-guard-secrets
  namespace: your-namespace
type: Opaque
stringData:
  database-url: "mysql+aiomysql://user:password@mysql-service:3306/llm_safe_db?charset=utf8mb4"
  secret-key: "your-secret-key-here"
```

## 部署命令

```bash
# 1. 创建namespace
kubectl create namespace your-namespace

# 2. 创建secrets
kubectl apply -f k8s/secrets.yaml

# 3. 创建configmap
kubectl apply -f k8s/configmap.yaml

# 4. 部署后端
kubectl apply -f k8s/backend-deployment.yaml

# 5. 部署前端
kubectl apply -f k8s/frontend-deployment.yaml

# 6. 配置Ingress
kubectl apply -f k8s/ingress.yaml

# 7. 检查部署状态
kubectl get pods -n your-namespace
kubectl get services -n your-namespace
kubectl get ingress -n your-namespace

# 8. 查看日志
kubectl logs -f deployment/llm-guard-backend -n your-namespace
kubectl logs -f deployment/llm-guard-frontend -n your-namespace
```

## 验证部署

```bash
# 1. 检查Pod状态
kubectl get pods -n your-namespace

# 2. 检查Service
kubectl get svc -n your-namespace

# 3. 检查Ingress
kubectl get ingress -n your-namespace

# 4. 运行测试脚本
export K8S_SERVICE=https://your-domain.com
./k8s_deployment_test.sh
```

## 滚动更新

```bash
# 更新镜像
kubectl set image deployment/llm-guard-backend backend=your-registry/llm-guard-backend:v2 -n your-namespace
kubectl set image deployment/llm-guard-frontend frontend=your-registry/llm-guard-frontend:v2 -n your-namespace

# 查看更新状态
kubectl rollout status deployment/llm-guard-backend -n your-namespace
kubectl rollout status deployment/llm-guard-frontend -n your-namespace

# 回滚
kubectl rollout undo deployment/llm-guard-backend -n your-namespace
kubectl rollout undo deployment/llm-guard-frontend -n your-namespace
```

## 扩缩容

```bash
# 扩容
kubectl scale deployment/llm-guard-backend --replicas=5 -n your-namespace

# 缩容
kubectl scale deployment/llm-guard-backend --replicas=2 -n your-namespace

# 自动扩缩容
kubectl autoscale deployment/llm-guard-backend --min=2 --max=10 --cpu-percent=80 -n your-namespace
```

## 监控和日志

```bash
# 查看Pod日志
kubectl logs -f <pod-name> -n your-namespace

# 查看最近的日志
kubectl logs --tail=100 <pod-name> -n your-namespace

# 查看所有容器日志
kubectl logs -f deployment/llm-guard-backend --all-containers=true -n your-namespace

# 进入容器
kubectl exec -it <pod-name> -n your-namespace -- /bin/bash

# 查看资源使用
kubectl top pods -n your-namespace
kubectl top nodes
```

## 故障排查

```bash
# 查看Pod详情
kubectl describe pod <pod-name> -n your-namespace

# 查看事件
kubectl get events -n your-namespace --sort-by='.lastTimestamp'

# 查看Service端点
kubectl get endpoints -n your-namespace

# 测试Service连通性
kubectl run -it --rm debug --image=busybox --restart=Never -n your-namespace -- sh
# 在容器内执行
wget -O- http://llm-guard-backend-service:9001/api/v1/health
```
