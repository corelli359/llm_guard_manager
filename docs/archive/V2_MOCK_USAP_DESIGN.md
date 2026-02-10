# Mock USAP 服务设计文档

## 版本信息
- **版本**: V1.0
- **设计日期**: 2026-02-06
- **用途**: 开发和测试环境模拟USAP认证系统

---

## 一、概述

### 1.1 目的
创建一个独立的Mock服务，模拟企业USAP（统一认证平台）的核心功能，用于：
- V2版本开发阶段的联调测试
- 验证SSO认证流程
- 模拟各种异常场景

### 1.2 项目结构
```
mock-usap/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── config.py            # 配置
│   ├── models.py            # 数据模型
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证相关接口
│   │   └── users.py         # 用户信息接口
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ticket_service.py    # Ticket管理
│   │   └── user_service.py      # 用户管理
│   └── data/
│       └── mock_users.json      # Mock用户数据
├── tests/
│   └── test_api.py
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 二、API接口设计

### 2.1 认证接口

#### 2.1.1 用户登录（建立会话）
```
POST /api/auth/login
```

**说明**: 用户在门户系统输入用户名密码，门户调用此接口验证身份并建立会话。

**请求**:
```json
{
  "username": "zhangsan",
  "password": "123456"
}
```

**成功响应** (200):
```json
{
  "success": true,
  "session_id": "SES_a1b2c3d4e5f6g7h8",
  "user_id": "U001",
  "user_name": "张三",
  "expires_in": 28800
}
```

**失败响应** (401):
```json
{
  "success": false,
  "error": "用户名或密码错误"
}
```

#### 2.1.2 获取Ticket（跳转时调用）
```
POST /api/auth/ticket
```

**说明**: 用户点击跳转到目标系统时，门户调用此接口获取一次性Ticket。

**请求**:
```json
{
  "session_id": "SES_a1b2c3d4e5f6g7h8",
  "target_system": "llm-guard-manager"
}
```

**成功响应** (200):
```json
{
  "success": true,
  "ticket": "TK_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "expires_in": 300,
  "target_system": "llm-guard-manager"
}
```

**失败响应 - Session无效** (401):
```json
{
  "success": false,
  "error": "Session无效或已过期"
}
```

#### 2.1.3 验证Ticket（目标系统调用）
```
POST /api/auth/validate-ticket
```

**请求头**:
```
X-Client-ID: llm-guard-manager
X-Client-Secret: mock-secret-key
```

**请求**:
```json
{
  "ticket": "TK_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
}
```

**成功响应** (200):
```json
{
  "valid": true,
  "user_id": "U001",
  "user_name": "张三",
  "email": "zhangsan@company.com",
  "department": "技术部",
  "phone": "13800138001"
}
```

**失败响应 - Ticket无效** (401):
```json
{
  "valid": false,
  "error": "Ticket无效"
}
```

**失败响应 - Ticket过期** (401):
```json
{
  "valid": false,
  "error": "Ticket已过期"
}
```

**失败响应 - Ticket已使用** (401):
```json
{
  "valid": false,
  "error": "Ticket已被使用"
}
```

---

### 2.2 用户信息接口

#### 2.2.1 获取单个用户信息
```
GET /api/users/{user_id}
```

**请求头**:
```
X-Client-ID: llm-guard-manager
X-Client-Secret: mock-secret-key
```

**成功响应** (200):
```json
{
  "user_id": "U001",
  "user_name": "张三",
  "email": "zhangsan@company.com",
  "department": "技术部",
  "phone": "13800138001",
  "status": "active"
}
```

**失败响应** (404):
```json
{
  "error": "用户不存在"
}
```

#### 2.2.2 批量获取用户信息
```
POST /api/users/batch
```

**请求头**:
```
X-Client-ID: llm-guard-manager
X-Client-Secret: mock-secret-key
```

**请求**:
```json
{
  "user_ids": ["U001", "U002", "U003"]
}
```

**响应** (200):
```json
{
  "users": [
    {
      "user_id": "U001",
      "user_name": "张三",
      "email": "zhangsan@company.com",
      "department": "技术部"
    },
    {
      "user_id": "U002",
      "user_name": "李四",
      "email": "lisi@company.com",
      "department": "产品部"
    }
  ],
  "not_found": ["U003"]
}
```

---

### 2.3 健康检查接口

#### 2.3.1 健康检查
```
GET /api/health
```

**响应** (200):
```json
{
  "status": "healthy",
  "service": "mock-usap",
  "version": "1.0.0"
}
```


---

## 三、Mock数据设计

### 3.1 用户数据
```json
{
  "users": [
    {
      "user_id": "U001",
      "username": "zhangsan",
      "password": "123456",
      "user_name": "张三",
      "email": "zhangsan@company.com",
      "department": "技术部",
      "phone": "13800138001",
      "status": "active"
    },
    {
      "user_id": "U002",
      "username": "lisi",
      "password": "123456",
      "user_name": "李四",
      "email": "lisi@company.com",
      "department": "产品部",
      "phone": "13800138002",
      "status": "active"
    },
    {
      "user_id": "U003",
      "username": "wangwu",
      "password": "123456",
      "user_name": "王五",
      "email": "wangwu@company.com",
      "department": "运营部",
      "phone": "13800138003",
      "status": "active"
    },
    {
      "user_id": "U004",
      "username": "zhaoliu",
      "password": "123456",
      "user_name": "赵六",
      "email": "zhaoliu@company.com",
      "department": "技术部",
      "phone": "13800138004",
      "status": "active"
    },
    {
      "user_id": "U005",
      "username": "sunqi",
      "password": "123456",
      "user_name": "孙七",
      "email": "sunqi@company.com",
      "department": "安全部",
      "phone": "13800138005",
      "status": "active"
    },
    {
      "user_id": "U006",
      "username": "zhouba",
      "password": "123456",
      "user_name": "周八",
      "email": "zhouba@company.com",
      "department": "技术部",
      "phone": "13800138006",
      "status": "inactive"
    },
    {
      "user_id": "U007",
      "username": "wujiu",
      "password": "123456",
      "user_name": "吴九",
      "email": "wujiu@company.com",
      "department": "产品部",
      "phone": "13800138007",
      "status": "active"
    },
    {
      "user_id": "U008",
      "username": "zhengshi",
      "password": "123456",
      "user_name": "郑十",
      "email": "zhengshi@company.com",
      "department": "运营部",
      "phone": "13800138008",
      "status": "active"
    },
    {
      "user_id": "U009",
      "username": "admin",
      "password": "admin123",
      "user_name": "系统管理员",
      "email": "admin@company.com",
      "department": "IT部",
      "phone": "13800138009",
      "status": "active"
    },
    {
      "user_id": "U010",
      "username": "test",
      "password": "test123",
      "user_name": "测试用户",
      "email": "test@company.com",
      "department": "测试部",
      "phone": "13800138010",
      "status": "active"
    }
  ]
}
```

### 3.2 用户角色映射建议

| 用户 | user_id | 建议角色 | 说明 |
|------|---------|---------|------|
| 系统管理员 | U009 | SYSTEM_ADMIN | 系统管理员，拥有所有权限 |
| 张三 | U001 | SCENARIO_ADMIN | 场景管理员，管理技术部场景 |
| 李四 | U002 | SCENARIO_ADMIN | 场景管理员，管理产品部场景 |
| 王五 | U003 | ANNOTATOR | 标注员 |
| 赵六 | U004 | ANNOTATOR | 标注员 |
| 孙七 | U005 | AUDITOR | 审计员 |
| 周八 | U006 | - | 已禁用用户 |
| 吴九 | U007 | ANNOTATOR | 标注员 |
| 郑十 | U008 | ANNOTATOR | 标注员 |
| 测试用户 | U010 | ANNOTATOR | 测试用户 |

---

## 四、Session和Ticket管理

### 4.1 Session管理

#### 4.1.1 Session生成规则
```python
import secrets
import time

def generate_session_id() -> str:
    """
    生成Session ID
    格式: SES_{随机字符串16位}
    """
    random_part = secrets.token_hex(8)  # 16位十六进制
    return f"SES_{random_part}"
```

#### 4.1.2 Session存储结构
```python
# 内存存储
sessions = {
    "SES_xxx": {
        "user_id": "U001",
        "created_at": 1738848000,
        "expires_at": 1738876800,  # 8小时后
    }
}
```

### 4.2 Ticket管理

#### 4.2.1 Ticket生成规则
```python
def generate_ticket() -> str:
    """
    生成Ticket
    格式: TK_{随机字符串32位}
    """
    random_part = secrets.token_hex(16)  # 32位十六进制
    return f"TK_{random_part}"
```

#### 4.2.2 Ticket存储结构
```python
# 内存存储
tickets = {
    "TK_xxx": {
        "user_id": "U001",
        "target_system": "llm-guard-manager",
        "created_at": 1738848000,
        "expires_at": 1738848300,  # 5分钟后
        "used": False
    }
}
```

### 4.3 完整流程逻辑

```python
# 1. 登录 - 创建Session
def login(username: str, password: str) -> dict:
    user = authenticate(username, password)
    if not user:
        return {"success": False, "error": "用户名或密码错误"}

    session_id = generate_session_id()
    sessions[session_id] = {
        "user_id": user["user_id"],
        "created_at": time.time(),
        "expires_at": time.time() + 28800  # 8小时
    }

    return {
        "success": True,
        "session_id": session_id,
        "user_id": user["user_id"],
        "user_name": user["user_name"],
        "expires_in": 28800
    }

# 2. 获取Ticket - 基于Session生成Ticket
def create_ticket(session_id: str, target_system: str) -> dict:
    if session_id not in sessions:
        return {"success": False, "error": "Session无效"}

    session = sessions[session_id]
    if time.time() > session["expires_at"]:
        return {"success": False, "error": "Session已过期"}

    ticket = generate_ticket()
    tickets[ticket] = {
        "user_id": session["user_id"],
        "target_system": target_system,
        "created_at": time.time(),
        "expires_at": time.time() + 300,  # 5分钟
        "used": False
    }

    return {
        "success": True,
        "ticket": ticket,
        "expires_in": 300,
        "target_system": target_system
    }

# 3. 验证Ticket - 目标系统调用
def validate_ticket(ticket: str) -> dict:
    if ticket not in tickets:
        return {"valid": False, "error": "Ticket无效"}

    ticket_data = tickets[ticket]

    if time.time() > ticket_data["expires_at"]:
        return {"valid": False, "error": "Ticket已过期"}

    if ticket_data["used"]:
        return {"valid": False, "error": "Ticket已被使用"}

    # 标记为已使用
    ticket_data["used"] = True

    # 获取用户信息
    user = get_user_by_id(ticket_data["user_id"])

    return {
        "valid": True,
        "user_id": user["user_id"],
        "user_name": user["user_name"],
        "email": user["email"],
        "department": user["department"],
        "phone": user["phone"]
    }
```

---

## 五、核心代码实现

### 5.1 main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, users

app = FastAPI(
    title="Mock USAP Service",
    description="模拟USAP统一认证平台",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "mock-usap",
        "version": "1.0.0"
    }
```

### 5.2 routes/auth.py
```python
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from app.services.session_service import SessionService
from app.services.ticket_service import TicketService
from app.services.user_service import UserService

router = APIRouter()
session_service = SessionService()
ticket_service = TicketService()
user_service = UserService()

class LoginRequest(BaseModel):
    username: str
    password: str

class TicketRequest(BaseModel):
    session_id: str
    target_system: str

class ValidateTicketRequest(BaseModel):
    ticket: str

@router.post("/login")
async def login(request: LoginRequest):
    """用户登录，建立Session"""
    user = user_service.authenticate(request.username, request.password)

    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if user.get("status") != "active":
        raise HTTPException(status_code=403, detail="用户已被禁用")

    session = session_service.create_session(user["user_id"])

    return {
        "success": True,
        "session_id": session["session_id"],
        "user_id": user["user_id"],
        "user_name": user["user_name"],
        "expires_in": session["expires_in"]
    }

@router.post("/ticket")
async def get_ticket(request: TicketRequest):
    """获取Ticket（跳转时调用）"""
    result = ticket_service.create_ticket(
        session_id=request.session_id,
        target_system=request.target_system
    )

    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])

    return result

@router.post("/validate-ticket")
async def validate_ticket(
    request: ValidateTicketRequest,
    x_client_id: str = Header(...),
    x_client_secret: str = Header(...)
):
    """验证Ticket（目标系统调用）"""
    # 简单的客户端验证
    if x_client_id != "llm-guard-manager":
        raise HTTPException(status_code=401, detail="无效的Client ID")

    result = ticket_service.validate_ticket(request.ticket)

    if not result["valid"]:
        raise HTTPException(status_code=401, detail=result["error"])

    return result
```

### 5.3 routes/users.py
```python
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List
from app.services.user_service import UserService

router = APIRouter()
user_service = UserService()

class BatchUsersRequest(BaseModel):
    user_ids: List[str]

@router.get("/{user_id}")
async def get_user(
    user_id: str,
    x_client_id: str = Header(...),
    x_client_secret: str = Header(...)
):
    """获取单个用户信息"""
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "user_id": user["user_id"],
        "user_name": user["user_name"],
        "email": user["email"],
        "department": user["department"],
        "phone": user["phone"],
        "status": user["status"]
    }

@router.post("/batch")
async def get_users_batch(
    request: BatchUsersRequest,
    x_client_id: str = Header(...),
    x_client_secret: str = Header(...)
):
    """批量获取用户信息"""
    users = []
    not_found = []
    
    for user_id in request.user_ids:
        user = user_service.get_user_by_id(user_id)
        if user:
            users.append({
                "user_id": user["user_id"],
                "user_name": user["user_name"],
                "email": user["email"],
                "department": user["department"]
            })
        else:
            not_found.append(user_id)
    
    return {
        "users": users,
        "not_found": not_found
    }
```


---

## 六、部署配置

### 6.1 Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 6.2 requirements.txt
```
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
```

### 6.3 K8s部署配置
```yaml
# k8s/mock-usap-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mock-usap
  namespace: llmsafe
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mock-usap
  template:
    metadata:
      labels:
        app: mock-usap
    spec:
      containers:
      - name: mock-usap
        image: mock-usap:v1.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: mock-usap-svc
  namespace: llmsafe
spec:
  selector:
    app: mock-usap
  ports:
  - port: 8080
    targetPort: 8080
  type: ClusterIP
```

### 6.4 本地运行
```bash
cd mock-usap
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

---

## 七、测试场景

### 7.1 正常流程测试
```bash
# 1. 登录建立Session
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "zhangsan", "password": "123456"}'

# 响应:
# {"success":true,"session_id":"SES_xxx","user_id":"U001","user_name":"张三","expires_in":28800}

# 2. 获取Ticket（跳转时调用）
curl -X POST http://localhost:8080/api/auth/ticket \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SES_xxx", "target_system": "llm-guard-manager"}'

# 响应:
# {"success":true,"ticket":"TK_xxx","expires_in":300,"target_system":"llm-guard-manager"}

# 3. 验证Ticket（安全管理平台调用）
curl -X POST http://localhost:8080/api/auth/validate-ticket \
  -H "Content-Type: application/json" \
  -H "X-Client-ID: llm-guard-manager" \
  -H "X-Client-Secret: mock-secret" \
  -d '{"ticket": "TK_xxx"}'

# 响应:
# {"valid":true,"user_id":"U001","user_name":"张三","email":"zhangsan@company.com",...}

# 4. 获取用户信息
curl http://localhost:8080/api/users/U001 \
  -H "X-Client-ID: llm-guard-manager" \
  -H "X-Client-Secret: mock-secret"

# 响应:
# {"user_id":"U001","user_name":"张三",...}
```

### 7.2 异常场景测试

#### 7.2.1 登录失败
```bash
# 密码错误
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "zhangsan", "password": "wrong"}'

# 响应: 401 {"detail": "用户名或密码错误"}
```

#### 7.2.2 用户被禁用
```bash
# 使用被禁用的用户
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "zhouba", "password": "123456"}'

# 响应: 403 {"detail": "用户已被禁用"}
```

#### 7.2.3 Session无效
```bash
# 使用无效的Session获取Ticket
curl -X POST http://localhost:8080/api/auth/ticket \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SES_invalid", "target_system": "llm-guard-manager"}'

# 响应: 401 {"detail": "Session无效"}
```

#### 7.2.4 Ticket过期
```bash
# 等待5分钟后验证Ticket
# 响应: 401 {"detail": "Ticket已过期"}
```

#### 7.2.5 Ticket重复使用
```bash
# 第二次使用同一个Ticket
# 响应: 401 {"detail": "Ticket已被使用"}
```

#### 7.2.6 用户不存在
```bash
curl http://localhost:8080/api/users/U999 \
  -H "X-Client-ID: llm-guard-manager" \
  -H "X-Client-Secret: mock-secret"

# 响应: 404 {"detail": "用户不存在"}
```

---

## 八、与安全管理平台集成

### 8.1 配置安全管理平台
在安全管理平台的配置中设置USAP地址：

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # USAP配置
    USAP_BASE_URL: str = "http://mock-usap-svc:8080"  # K8s内部地址
    USAP_CLIENT_ID: str = "llm-guard-manager"
    USAP_CLIENT_SECRET: str = "mock-secret"
```

### 8.2 K8s环境变量
```yaml
# 在backend deployment中添加
env:
- name: USAP_BASE_URL
  value: "http://mock-usap-svc:8080"
- name: USAP_CLIENT_ID
  value: "llm-guard-manager"
- name: USAP_CLIENT_SECRET
  value: "mock-secret"
```

### 8.3 本地开发环境
```bash
# 启动Mock USAP
cd mock-usap && uvicorn app.main:app --port 8080 &

# 启动安全管理平台后端
cd backend
export USAP_BASE_URL=http://localhost:8080
python run.py
```

---

## 九、总结

### 9.1 Mock USAP功能清单
- ✅ 用户登录（建立Session，8小时有效期）
- ✅ 获取Ticket（基于Session，5分钟有效期）
- ✅ Ticket验证（一次性使用）
- ✅ 获取单个用户信息
- ✅ 批量获取用户信息
- ✅ 健康检查
- ✅ 异常场景模拟

### 9.2 接口清单
| 接口 | 方法 | 说明 |
|------|------|------|
| /api/auth/login | POST | 用户登录，建立Session |
| /api/auth/ticket | POST | 获取Ticket（跳转时调用） |
| /api/auth/validate-ticket | POST | 验证Ticket（目标系统调用） |
| /api/users/{user_id} | GET | 获取单个用户信息 |
| /api/users/batch | POST | 批量获取用户信息 |
| /api/health | GET | 健康检查 |

### 9.3 Mock数据
- ✅ 10个测试用户
- ✅ 包含不同部门
- ✅ 包含禁用用户
- ✅ 包含管理员和测试用户

### 9.4 部署方式
- ✅ 本地运行
- ✅ Docker镜像
- ✅ K8s部署

---

**文档版本**: V1.0
**最后更新**: 2026-02-06
**状态**: ✅ 完成
