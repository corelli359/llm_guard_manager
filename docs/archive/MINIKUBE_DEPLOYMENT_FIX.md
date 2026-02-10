# Minikube部署问题解决报告

## 问题描述
用户无法访问minikube部署的应用

## 问题原因
1. **minikube mount未运行** - 导致Pod无法挂载代码目录
2. **前端未构建** - dist目录不存在
3. **Pod处于ContainerCreating状态** - 17小时无法启动

## 解决步骤

### 1. 启动minikube mount
```bash
cd /Users/weipeng/Desktop/PY_WORK_SPACE/llm_guard_manager
nohup minikube mount $(pwd):/host > /tmp/minikube-mount.log 2>&1 &
```

### 2. 构建前端
```bash
cd frontend
VITE_BASE_PATH=/web-manager/ VITE_API_BASE_URL=/dbmanage/api/v1 npm run build
```

### 3. 重启Pod
```bash
kubectl delete pod -n llmsafe -l app=llmsafe-backend
kubectl delete pod -n llmsafe -l app=llmsafe-frontend
```

## 当前状态

### ✅ 已解决
- minikube mount正常运行
- 前端构建完成
- Pod状态: Running
- 前端访问: ✅ HTTP 200
- 后端API: ✅ 正常响应
- 登录功能: ✅ 正常

### ⚠️ 已知问题
**权限API返回"User not found"**

**原因**:
- 硬编码用户`llm_guard`不在数据库中
- 权限API需要从数据库查询完整用户信息

**解决方案**:
1. 在数据库中创建`llm_guard`用户
2. 或使用数据库中已存在的用户登录

## 访问信息

### 访问地址
- **前端**: http://llmsafe-dev.aisp.test.abc/web-manager/
- **后端API**: http://llmsafe-dev.aisp.test.abc/dbmanage/api/v1

### Hosts配置
```bash
# /etc/hosts
192.168.64.3 llmsafe-dev.aisp.test.abc
```

### 测试命令
```bash
# 测试前端
curl http://llmsafe-dev.aisp.test.abc/web-manager/

# 测试后端API
curl http://llmsafe-dev.aisp.test.abc/dbmanage/api/v1/tags/

# 登录
curl -X POST http://llmsafe-dev.aisp.test.abc/dbmanage/api/v1/login/access-token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=llm_guard&password=68-8CtBhug"
```

## 部署状态

```bash
kubectl get pods -n llmsafe
# NAME                                READY   STATUS    RESTARTS   AGE
# llmsafe-backend-7c6f859956-l97xf    1/1     Running   0          7m
# llmsafe-frontend-5dd5dd6c4d-4gcqr   1/1     Running   0          7m
```

## 重要提醒

### minikube mount必须保持运行
minikube mount进程必须一直运行，否则Pod无法访问代码：

```bash
# 检查mount进程
pgrep -f "minikube mount"

# 如果没有运行，重新启动
cd /Users/weipeng/Desktop/PY_WORK_SPACE/llm_guard_manager
nohup minikube mount $(pwd):/host > /tmp/minikube-mount.log 2>&1 &
```

### 前端修改后需要重新构建
每次修改前端代码后，需要重新构建：

```bash
cd frontend
VITE_BASE_PATH=/web-manager/ VITE_API_BASE_URL=/dbmanage/api/v1 npm run build
```

### 使用部署脚本
建议使用现有的部署脚本：

```bash
cd k8s
./deploy.sh
```

## 下一步操作

### 1. 创建数据库用户（推荐）
```bash
# 进入后端Pod
kubectl exec -it -n llmsafe deployment/llmsafe-backend -- python

# 在Python中执行
from app.models.db_meta import User
from app.core.security import get_password_hash
from app.core.db import get_db
import uuid
import asyncio

async def create_admin():
    async for db in get_db():
        admin = User(
            id=str(uuid.uuid4()),
            username="llm_guard",
            hashed_password=get_password_hash("68-8CtBhug"),
            role="SYSTEM_ADMIN",
            display_name="系统管理员",
            is_active=True
        )
        db.add(admin)
        await db.commit()
        print("Admin user created!")
        break

asyncio.run(create_admin())
```

### 2. 或使用数据库中已有用户
检查数据库中已有的用户并使用其登录。

## 总结

✅ **部署问题已解决**
- minikube mount正常运行
- Pod状态正常
- 前端和后端API可访问
- 登录功能正常

⚠️ **需要创建数据库用户**
- 权限API需要数据库中的用户记录
- 建议创建`llm_guard`用户或使用已有用户

🎉 **应用已可以正常访问**: http://llmsafe-dev.aisp.test.abc/web-manager/
