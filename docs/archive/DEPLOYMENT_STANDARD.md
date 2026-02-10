# LLM Guard Manager 部署规范文档

## 📋 部署标准

每次部署必须严格遵守以下标准：

1. ✅ **按照云上方式部署**：部署的前缀、挂载路径必须明确写入配置
2. ✅ **部署后必须测试**：确保所有功能正常工作后才算部署完成

---

## 🔧 部署配置（K8s 环境）

### 路径配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **前端访问路径** | `/web-manager/` | 通过 ingress 访问前端的 URL 前缀 |
| **后端 API 路径** | `/dbmanage/api/v1` | 前端调用后端 API 的完整路径 |
| **Minikube 挂载** | 宿主机 `/Users/weipeng/Desktop/PY_WORK_SPACE/llm_guard_manager` → Minikube `/host` | 代码挂载路径 |
| **前端 Pod 挂载** | Minikube `/host/frontend/dist` → Pod `/usr/share/nginx/html` | 前端静态文件挂载 |
| **后端 Pod 挂载** | Minikube `/host/backend` → Pod `/app` | 后端代码挂载 |

### 访问地址

- **前端**: http://llmsafe-dev.aisp.test.abc/web-manager/
- **后端 API**: http://llmsafe-dev.aisp.test.abc/dbmanage/api/v1/

---

## 📦 部署步骤

### 前置检查

在开始部署前，必须确认以下条件：

```bash
# 1. 检查 minikube mount 是否运行
ps aux | grep "minikube mount" | grep -v grep
# 应该看到: minikube mount /Users/weipeng/Desktop/PY_WORK_SPACE/llm_guard_manager:/host

# 2. 检查 K8s pods 状态
kubectl get pods -n llmsafe
# 应该看到 backend 和 frontend 都是 Running

# 3. 检查 ingress 状态
kubectl get ingress -n llmsafe
# 应该看到 llmsafe-ingress 已分配 IP
```

如果 minikube mount 没有运行，启动它：
```bash
cd /Users/weipeng/Desktop/PY_WORK_SPACE/llm_guard_manager
nohup minikube mount $(pwd):/host > /tmp/minikube-mount.log 2>&1 &
```

---

### 步骤 1: 构建前端

**⚠️ 重要：必须使用正确的环境变量！**

```bash
cd /Users/weipeng/Desktop/PY_WORK_SPACE/llm_guard_manager/frontend

# 方式一：使用部署脚本（推荐）
./build-for-k8s.sh

# 方式二：手动构建
rm -rf dist
VITE_BASE_PATH=/web-manager/ VITE_API_BASE_URL=/dbmanage/api/v1 npm run build
```

**构建后验证**：
```bash
# 检查 index.html 中的资源路径
cat dist/index.html | grep "/web-manager/"
# 应该看到: <script type="module" crossorigin src="/web-manager/assets/...

# 检查 JS 文件中的 API baseURL
grep -o 'dbmanage' dist/assets/*.js | head -1
# 应该看到: dbmanage
```

---

### 步骤 2: 部署前端

```bash
# 重启前端 Pod（会自动加载新的 dist 文件）
kubectl delete pod -l app=llmsafe-frontend -n llmsafe

# 等待 Pod 启动
sleep 15
kubectl get pods -n llmsafe
# 确认 llmsafe-frontend 状态为 Running
```

**部署后验证**：
```bash
# 检查 Pod 内的文件
kubectl exec -n llmsafe $(kubectl get pods -n llmsafe -l app=llmsafe-frontend -o jsonpath='{.items[0].metadata.name}') -- ls -la /usr/share/nginx/html/
# 应该看到 index.html 和 assets 目录

# 检查 index.html 内容
kubectl exec -n llmsafe $(kubectl get pods -n llmsafe -l app=llmsafe-frontend -o jsonpath='{.items[0].metadata.name}') -- cat /usr/share/nginx/html/index.html | grep "/web-manager/"
# 应该看到正确的资源路径
```

---

### 步骤 3: 部署后端（如有修改）

```bash
# 后端代码通过 minikube mount 自动同步，只需重启 Pod
kubectl delete pod -l app=llmsafe-backend -n llmsafe

# 等待 Pod 启动（首次启动会安装依赖，可能需要几分钟）
sleep 30
kubectl get pods -n llmsafe
# 确认 llmsafe-backend 状态为 Running
```

---

## ✅ 测试检查清单

部署完成后，**必须**按照以下清单逐项测试：

### 1. 基础连通性测试

**⚠️ 重要：所有测试必须返回 HTTP 200 才算成功！**

```bash
# 测试前端页面
curl -I http://llmsafe-dev.aisp.test.abc/web-manager/
# 期望: HTTP/1.1 200 OK

# 测试前端资源文件（需要先查看实际的文件名）
ls frontend/dist/assets/index-*.js
# 然后测试该文件
curl -I http://llmsafe-dev.aisp.test.abc/web-manager/assets/index-[实际文件名].js
# 期望: HTTP/1.1 200 OK

# 测试后端 API 文档
curl -I http://llmsafe-dev.aisp.test.abc/dbmanage/docs
# 期望: HTTP/1.1 200 OK

# 测试后端登录接口（使用正确的账号密码）
# 注意：必须使用数据库中实际存在的账号！
curl -s -X POST http://llmsafe-dev.aisp.test.abc/dbmanage/api/v1/login/access-token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=[实际用户名]&password=[实际密码]" \
  -w "\nHTTP Status: %{http_code}\n"
# 期望: HTTP Status: 200
# 期望返回: {"access_token":"...", "token_type":"bearer", "role":"..."}
```

**如何获取测试账号**：
```bash
# 查询数据库中的活跃用户
kubectl exec -n llmsafe $(kubectl get pods -n llmsafe -l app=llmsafe-backend -o jsonpath='{.items[0].metadata.name}') -- python -c "
import asyncio
from app.core.database import get_db
from app.models.db_meta import User
from sqlalchemy import select

async def list_users():
    async for db in get_db():
        result = await db.execute(select(User.username, User.role, User.is_active).where(User.is_active == True))
        users = result.all()
        print('可用的测试账号:')
        for user in users:
            print(f'  用户名: {user[0]}, 角色: {user[1]}')
        break

asyncio.run(list_users())
"
```
```

### 2. 前端功能测试

在浏览器中打开: http://llmsafe-dev.aisp.test.abc/web-manager/

#### 2.1 登录功能
- [ ] 页面能正常加载（无 404 错误）
- [ ] 页面样式正常（CSS 加载成功）
- [ ] 能看到登录表单
- [ ] 输入错误账号密码，显示"登录失败"提示
- [ ] 输入正确账号密码，能成功登录并跳转

#### 2.2 智能标注功能（重点测试）
- [ ] 能进入"智能标注"页面
- [ ] 能看到任务总览统计（总任务数、待认领、已认领等）
- [ ] 点击"领取新任务"按钮，能成功领取任务
- [ ] 能看到当前批次进度和倒计时
- [ ] **关键：页面不会无限刷新（CPU 不会飙升）**
- [ ] **关键：能修改"人工修正"列的标签和风险等级**
- [ ] 修改后点击"确认"按钮，能成功提交
- [ ] 点击"忽略"按钮，能成功忽略任务

#### 2.3 其他功能（管理员）
- [ ] 标签管理页面正常
- [ ] 全局敏感词页面正常
- [ ] 应用管理页面正常
- [ ] 用户管理页面正常

### 3. 后端日志检查

```bash
# 查看后端日志，确认没有错误
kubectl logs -n llmsafe -l app=llmsafe-backend --tail=50
# 检查是否有 ERROR 或 Exception
```

### 4. 性能检查

```bash
# 在浏览器中打开智能标注页面，观察 Network 面板
# 确认：
# - API 请求不会无限循环
# - 每个 API 请求都能正常返回
# - 没有 404 或 500 错误
```

---

## 🚨 常见问题排查

### 问题 1: 前端页面 404

**症状**：访问 http://llmsafe-dev.aisp.test.abc/web-manager/ 返回 404

**排查步骤**：
```bash
# 1. 检查 ingress 配置
kubectl describe ingress llmsafe-ingress -n llmsafe
# 确认 path 配置为 /web-manager(/|$)(.*)

# 2. 检查前端 Pod 内的文件
kubectl exec -n llmsafe $(kubectl get pods -n llmsafe -l app=llmsafe-frontend -o jsonpath='{.items[0].metadata.name}') -- ls -la /usr/share/nginx/html/
# 确认 index.html 存在

# 3. 检查 minikube mount
ps aux | grep "minikube mount"
# 确认进程存在
```

### 问题 2: 前端能访问，但 API 请求 404

**症状**：前端页面能打开，但登录时提示网络错误

**排查步骤**：
```bash
# 1. 检查浏览器 Network 面板，查看实际请求的 URL
# 应该是: http://llmsafe-dev.aisp.test.abc/dbmanage/api/v1/...

# 2. 检查构建时的环境变量
grep -o 'dbmanage' frontend/dist/assets/*.js | head -1
# 应该能找到 dbmanage

# 3. 如果没有 dbmanage，说明构建时环境变量没有设置
# 重新构建：
cd frontend
VITE_BASE_PATH=/web-manager/ VITE_API_BASE_URL=/dbmanage/api/v1 npm run build
kubectl delete pod -l app=llmsafe-frontend -n llmsafe
```

### 问题 3: 页面无限刷新，CPU 占满

**症状**：打开智能标注页面后，浏览器疯狂发送请求，CPU 占用很高

**原因**：useEffect 依赖配置错误，导致无限循环

**解决**：
- 检查 `SmartLabeling.tsx` 中倒计时 useEffect 的依赖是否为 `[myTasksStats?.expires_at]`
- 确认超时后不会调用 `fetchData()` 和 `fetchMyTasksStats()`

### 问题 4: Select 不能修改

**症状**：修改"人工修正"列的标签后，值又变回原来的

**原因**：Select 使用了 `value` 而不是 `defaultValue`，或者 `onChange` 立即调用 API 导致数据刷新

**解决**：
- 确认 Select 使用 `defaultValue` 而不是 `value`
- 确认 `onChange` 只更新 record 对象，不调用 API
- 只有点击"确认"按钮时才调用 API

### 问题 5: 后端 Pod 启动失败

**症状**：`kubectl get pods -n llmsafe` 显示 backend Pod 状态为 CrashLoopBackOff

**排查步骤**：
```bash
# 查看 Pod 日志
kubectl logs -n llmsafe -l app=llmsafe-backend --tail=100

# 常见原因：
# 1. 数据库连接失败 - 检查 backend/app/core/config.py 中的数据库配置
# 2. 依赖安装失败 - 检查 requirements.txt
# 3. 代码语法错误 - 检查最近的代码修改
```

---

## 📝 部署检查表

每次部署完成后，填写此检查表：

```
部署日期: ___________
部署人员: ___________

前置检查:
[ ] minikube mount 运行中
[ ] K8s pods 状态正常
[ ] ingress 已分配 IP

构建验证:
[ ] 前端构建成功
[ ] index.html 包含 /web-manager/ 前缀
[ ] JS 文件包含 dbmanage 字符串

部署验证:
[ ] 前端 Pod 重启成功
[ ] 后端 Pod 运行正常（如有修改）
[ ] Pod 内文件挂载正确

功能测试:
[ ] 前端页面能访问（200 OK）
[ ] 前端资源文件能加载（JS/CSS）
[ ] 后端 API 能访问（401/200）
[ ] 登录功能正常
[ ] 智能标注页面不会无限刷新
[ ] 能修改标签和风险等级
[ ] 确认按钮能正常提交
[ ] 后端日志无错误

性能检查:
[ ] CPU 占用正常（无飙升）
[ ] API 请求无循环
[ ] 页面响应流畅

部署结果: [ ] 成功  [ ] 失败

备注: ___________________________________________
```

---

## 🔄 回滚步骤

如果部署后发现问题，立即回滚：

```bash
# 1. 前端回滚
cd /Users/weipeng/Desktop/PY_WORK_SPACE/llm_guard_manager
git checkout frontend/src/  # 恢复前端代码
cd frontend
./build-for-k8s.sh
kubectl delete pod -l app=llmsafe-frontend -n llmsafe

# 2. 后端回滚
git checkout backend/  # 恢复后端代码
kubectl delete pod -l app=llmsafe-backend -n llmsafe

# 3. 验证回滚成功
# 按照"测试检查清单"重新测试
```

---

## 📞 联系方式

如有问题，请联系：
- 开发负责人: [填写联系方式]
- 运维负责人: [填写联系方式]

---

**最后更新**: 2026-01-29
**文档版本**: v1.0
