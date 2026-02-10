# K8s部署测试验证脚本

## 测试环境
- K8s集群
- 前端路径: `/web-manager/`
- 后端API路径: `/dbmanage/api/v1`

## 测试步骤

### 1. 前端构建验证
```bash
cd frontend
VITE_BASE_PATH=/web-manager/ VITE_API_BASE_URL=/dbmanage/api/v1 npm run build
```

**预期结果**:
- ✅ 构建成功
- ✅ dist目录生成
- ✅ index.html中包含正确的base路径

### 2. 后端健康检查
```bash
curl http://<k8s-service>/dbmanage/api/v1/health
```

**预期结果**:
- ✅ HTTP 200
- ✅ 返回健康状态

### 3. 前端访问测试
```bash
curl http://<k8s-service>/web-manager/
```

**预期结果**:
- ✅ HTTP 200
- ✅ 返回HTML页面

### 4. API访问测试
```bash
# 登录测试
curl -X POST http://<k8s-service>/dbmanage/api/v1/login/access-token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=llm_guard&password=68-8CtBhug"
```

**预期结果**:
- ✅ HTTP 200
- ✅ 返回access_token

### 5. 权限API测试
```bash
# 获取当前用户权限
curl http://<k8s-service>/dbmanage/api/v1/permissions/me \
  -H "Authorization: Bearer <token>"
```

**预期结果**:
- ✅ HTTP 200
- ✅ 返回用户权限信息

### 6. 审计日志API测试
```bash
# 查询审计日志
curl http://<k8s-service>/dbmanage/api/v1/audit-logs/ \
  -H "Authorization: Bearer <token>"
```

**预期结果**:
- ✅ HTTP 200
- ✅ 返回审计日志列表

### 7. 用户场景API测试
```bash
# 获取用户场景
curl http://<k8s-service>/dbmanage/api/v1/users/<user_id>/scenarios \
  -H "Authorization: Bearer <token>"
```

**预期结果**:
- ✅ HTTP 200
- ✅ 返回场景列表

## 完整测试脚本

```bash
#!/bin/bash

# K8s部署测试脚本
set -e

K8S_SERVICE="http://your-k8s-service"
BASE_PATH="/web-manager/"
API_PATH="/dbmanage/api/v1"

echo "=========================================="
echo "K8s部署测试开始"
echo "=========================================="

# 1. 前端访问测试
echo -e "\n[测试1] 前端访问测试..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${K8S_SERVICE}${BASE_PATH})
if [ "$RESPONSE" = "200" ]; then
    echo "✅ 前端访问成功 (HTTP $RESPONSE)"
else
    echo "❌ 前端访问失败 (HTTP $RESPONSE)"
    exit 1
fi

# 2. 后端健康检查
echo -e "\n[测试2] 后端健康检查..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${K8S_SERVICE}${API_PATH}/health)
if [ "$RESPONSE" = "200" ]; then
    echo "✅ 后端健康检查通过 (HTTP $RESPONSE)"
else
    echo "❌ 后端健康检查失败 (HTTP $RESPONSE)"
    exit 1
fi

# 3. 登录测试
echo -e "\n[测试3] 登录测试..."
LOGIN_RESPONSE=$(curl -s -X POST ${K8S_SERVICE}${API_PATH}/login/access-token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=llm_guard&password=68-8CtBhug")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo "✅ 登录成功，获取到token"
else
    echo "❌ 登录失败"
    exit 1
fi

# 4. 权限API测试
echo -e "\n[测试4] 权限API测试..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${K8S_SERVICE}${API_PATH}/permissions/me \
  -H "Authorization: Bearer $TOKEN")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ 权限API测试通过 (HTTP $RESPONSE)"
else
    echo "❌ 权限API测试失败 (HTTP $RESPONSE)"
    exit 1
fi

# 5. 审计日志API测试
echo -e "\n[测试5] 审计日志API测试..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${K8S_SERVICE}${API_PATH}/audit-logs/ \
  -H "Authorization: Bearer $TOKEN")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ 审计日志API测试通过 (HTTP $RESPONSE)"
else
    echo "❌ 审计日志API测试失败 (HTTP $RESPONSE)"
    exit 1
fi

# 6. 用户管理API测试
echo -e "\n[测试6] 用户管理API测试..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" ${K8S_SERVICE}${API_PATH}/users/ \
  -H "Authorization: Bearer $TOKEN")
if [ "$RESPONSE" = "200" ]; then
    echo "✅ 用户管理API测试通过 (HTTP $RESPONSE)"
else
    echo "❌ 用户管理API测试失败 (HTTP $RESPONSE)"
    exit 1
fi

echo -e "\n=========================================="
echo "✅ 所有K8s部署测试通过！"
echo "=========================================="
```

## 测试检查表

### 部署前检查
- [ ] 前端环境变量配置正确
  - `VITE_BASE_PATH=/web-manager/`
  - `VITE_API_BASE_URL=/dbmanage/api/v1`
- [ ] 后端配置正确
  - 数据库连接正常
  - CORS配置正确
- [ ] K8s配置文件准备完成
  - Deployment
  - Service
  - Ingress

### 部署后检查
- [ ] Pod状态正常 (Running)
- [ ] Service可访问
- [ ] Ingress规则生效
- [ ] 前端页面可访问
- [ ] 后端API可访问
- [ ] 数据库连接正常

### 功能测试
- [ ] 登录功能正常
- [ ] 权限系统正常
- [ ] 审计日志正常
- [ ] 用户管理正常
- [ ] 场景分配正常
- [ ] 权限配置正常

### 性能测试
- [ ] 前端加载速度正常
- [ ] API响应时间正常
- [ ] 数据库查询性能正常

## 常见问题排查

### 1. 前端404错误
**原因**: base路径配置错误
**解决**: 检查VITE_BASE_PATH是否正确

### 2. API 404错误
**原因**: API路径配置错误
**解决**: 检查VITE_API_BASE_URL是否正确

### 3. CORS错误
**原因**: 后端CORS配置不正确
**解决**: 检查后端allow_origins配置

### 4. 401错误
**原因**: Token过期或无效
**解决**: 重新登录获取新token

### 5. 403错误
**原因**: 权限不足
**解决**: 检查用户角色和权限配置

## 回滚方案

如果部署失败，执行以下步骤回滚：

```bash
# 1. 回滚到上一个版本
kubectl rollout undo deployment/llm-guard-frontend
kubectl rollout undo deployment/llm-guard-backend

# 2. 检查回滚状态
kubectl rollout status deployment/llm-guard-frontend
kubectl rollout status deployment/llm-guard-backend

# 3. 验证服务正常
curl http://<k8s-service>/web-manager/
curl http://<k8s-service>/dbmanage/api/v1/health
```
