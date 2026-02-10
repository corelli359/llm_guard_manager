# LLM Guard Manager V2 认证流程详细设计

## 版本信息
- **版本**: V2.0
- **设计日期**: 2026-02-06
- **关联文档**: V2_SYSTEM_ARCHITECTURE.md

---

## 一、认证流程总览

### 1.1 完整认证链路

```
┌─────────┐
│  用户   │
└────┬────┘
     │
     │ Step 1: 访问门户
     │ https://portal.company.com
     ▼
┌──────────────────┐
│   门户系统       │
│  (Portal)        │
└────┬─────────────┘
     │
     │ Step 2: 输入用户名/密码
     │ POST /api/auth/login
     ▼
┌──────────────────┐
│   USAP系统       │
│  (认证中心)      │
└────┬─────────────┘
     │
     │ Step 3: 验证成功，返回Session
     │ Response: {session_id: "SES_xxx", user_id: "U001", expires_in: 28800}
     ▼
┌──────────────────┐
│   门户系统       │
│  (保存Session)   │
└────┬─────────────┘
     │
     │ Step 4: 用户点击"安全管理平台"
     │ POST /api/auth/ticket {session_id, target_system}
     ▼
┌──────────────────┐
│   USAP系统       │
└────┬─────────────┘
     │
     │ Step 5: 返回Ticket
     │ Response: {ticket: "TK_xxx", expires_in: 300}
     ▼
┌──────────────────┐
│   门户系统       │
└────┬─────────────┘
     │
     │ Step 6: 重定向到安全管理平台
     │ https://llm-guard.company.com/sso/login?ticket=TK_xxx
     ▼
┌──────────────────┐
│  安全管理平台    │
│  (Frontend)      │
└────┬─────────────┘
     │
     │ Step 7: 调用后端SSO登录接口
     │ POST /api/v1/sso/login {ticket: "TK_xxx"}
     ▼
┌──────────────────┐
│  安全管理平台    │
│  (Backend)       │
└────┬─────────────┘
     │
     │ Step 8: 验证Ticket
     │ POST https://usap.company.com/api/auth/validate-ticket
     ▼
┌──────────────────┐
│   USAP系统       │
└────┬─────────────┘
     │
     │ Step 9: 返回UserID和用户信息
     │ Response: {user_id: "U001", name: "张三", ...}
     ▼
┌──────────────────┐
│  安全管理平台    │
│  (Backend)       │
└────┬─────────────┘
     │
     │ Step 10: 查询/创建本地用户记录
     │ SELECT * FROM users WHERE user_id = 'U001'
     │
     │ Step 11: 查询用户权限
     │ SELECT role, scenarios FROM users WHERE user_id = 'U001'
     │
     │ Step 12: 生成JWT Token
     │ JWT Payload: {user_id: "U001", role: "SYSTEM_ADMIN", ...}
     ▼
┌──────────────────┐
│  安全管理平台    │
│  (Frontend)      │
└────┬─────────────┘
     │
     │ Step 11: 存储Token，跳转到主页
     │ localStorage.setItem('access_token', token)
     │ navigate('/dashboard')
     ▼
┌──────────────────┐
│   主页面         │
└──────────────────┘
```

---

## 二、详细流程设计

### 2.1 门户系统登录（Step 1-3）

#### 2.1.1 用户访问门户
```
用户操作: 在浏览器输入 https://portal.company.com
门户响应: 显示登录页面
```

#### 2.1.2 用户提交登录表单
```http
POST https://portal.company.com/api/auth/login
Content-Type: application/json

{
  "username": "zhangsan",
  "password": "password123"
}
```

#### 2.1.3 门户调用USAP认证
```http
POST https://usap.company.com/api/auth/login
Content-Type: application/json
X-Client-ID: portal-system
X-Client-Secret: portal-secret-key

{
  "username": "zhangsan",
  "password": "password123",
  "client_id": "portal-system"
}
```

#### 2.1.4 USAP返回Ticket
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "ticket": "TK_a1b2c3d4e5f6g7h8i9j0",
  "expires_in": 300,
  "user_id": "U001",
  "user_name": "张三"
}
```

**Ticket格式说明**:
- 前缀: `TK_` (Ticket标识)
- 长度: 20-32字符
- 编码: Base64或十六进制
- 签名: 包含HMAC签名防篡改
- 有效期: 5分钟（300秒）
- 使用次数: 一次性

---

### 2.2 门户跳转到安全管理平台（Step 4）

#### 2.2.1 门户系统重定向
```javascript
// 门户系统前端代码
const redirectToLLMGuard = (ticket) => {
  const targetUrl = `https://llm-guard.company.com/sso/login?ticket=${ticket}`;
  window.location.href = targetUrl;
};
```

#### 2.2.2 URL参数说明
```
https://llm-guard.company.com/sso/login?ticket=TK_xxx&return_url=/dashboard

参数说明:
- ticket: USAP颁发的Ticket（必需）
- return_url: 登录成功后跳转的页面（可选，默认/dashboard）
```

---

### 2.3 安全管理平台SSO登录（Step 5-10）

#### 2.3.1 前端接收Ticket
```typescript
// frontend/src/pages/SSOLogin.tsx
import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ssoApi } from '../api';

const SSOLogin: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const ticket = searchParams.get('ticket');
    const returnUrl = searchParams.get('return_url') || '/dashboard';

    if (!ticket) {
      message.error('缺少Ticket参数');
      navigate('/login');
      return;
    }

    // 调用后端SSO登录接口
    ssoApi.loginWithTicket(ticket)
      .then(response => {
        // 存储Token
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('user_id', response.data.user_id);

        // 跳转到目标页面
        navigate(returnUrl);
      })
      .catch(error => {
        message.error('SSO登录失败: ' + error.message);
        navigate('/login');
      });
  }, []);

  return <Spin tip="正在登录..." />;
};
```

#### 2.3.2 后端SSO登录接口
```python
# backend/app/api/v1/endpoints/sso.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.sso import SSOLoginRequest, SSOLoginResponse
from app.services.sso_service import SSOService

router = APIRouter()

@router.post("/login", response_model=SSOLoginResponse)
async def sso_login(
    request: SSOLoginRequest,
    sso_service: SSOService = Depends()
):
    """
    SSO单点登录

    流程:
    1. 验证Ticket
    2. 获取UserID
    3. 同步/创建本地用户
    4. 查询用户权限
    5. 生成JWT Token
    """
    try:
        # Step 1: 验证Ticket
        validation_result = await sso_service.validate_ticket(request.ticket)

        if not validation_result.valid:
            raise HTTPException(
                status_code=401,
                detail="Ticket验证失败: " + validation_result.error
            )

        # Step 2: 获取UserID
        user_id = validation_result.user_id

        # Step 3: 同步/创建本地用户
        user = await sso_service.sync_user_from_usap(user_id)

        # Step 4: 查询用户权限
        permissions = await sso_service.get_user_permissions(user_id)

        # Step 5: 生成JWT Token
        token = await sso_service.create_access_token(
            user_id=user_id,
            role=user.role,
            scenarios=permissions.scenarios
        )

        return SSOLoginResponse(
            access_token=token,
            token_type="bearer",
            user_id=user_id,
            role=user.role,
            expires_in=28800  # 8小时
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2.3.3 Ticket验证服务
```python
# backend/app/services/sso_service.py
from app.clients.usap_client import USAPClient
from app.schemas.sso import TicketValidationResult

class SSOService:
    def __init__(self, usap_client: USAPClient):
        self.usap_client = usap_client

    async def validate_ticket(self, ticket: str) -> TicketValidationResult:
        """
        验证Ticket

        调用USAP接口验证Ticket的有效性
        """
        try:
            # 调用USAP验证接口
            response = await self.usap_client.validate_ticket(ticket)

            return TicketValidationResult(
                valid=True,
                user_id=response.user_id,
                user_name=response.user_name,
                email=response.email,
                department=response.department
            )

        except USAPAPIError as e:
            return TicketValidationResult(
                valid=False,
                error=str(e)
            )
```

#### 2.3.4 USAP客户端实现
```python
# backend/app/clients/usap_client.py
import httpx
from app.core.config import settings
from app.schemas.usap import USAPValidateTicketResponse

class USAPClient:
    def __init__(self):
        self.base_url = settings.USAP_BASE_URL
        self.client_id = settings.USAP_CLIENT_ID
        self.client_secret = settings.USAP_CLIENT_SECRET

    async def validate_ticket(self, ticket: str) -> USAPValidateTicketResponse:
        """
        调用USAP验证Ticket

        接口: POST /api/auth/validate-ticket
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/auth/validate-ticket",
                json={"ticket": ticket},
                headers={
                    "X-Client-ID": self.client_id,
                    "X-Client-Secret": self.client_secret
                },
                timeout=5.0
            )

            if response.status_code != 200:
                raise USAPAPIError(f"USAP API错误: {response.status_code}")

            data = response.json()

            if not data.get("valid"):
                raise USAPAPIError(data.get("error", "Ticket无效"))

            return USAPValidateTicketResponse(
                valid=True,
                user_id=data["user_id"],
                user_name=data.get("user_name"),
                email=data.get("email"),
                department=data.get("department")
            )
```

---

### 2.4 用户信息同步（Step 8）

#### 2.4.1 同步策略
```python
async def sync_user_from_usap(self, user_id: str) -> User:
    """
    从USAP同步用户信息

    策略:
    1. 查询本地是否存在该用户
    2. 如果不存在，创建新用户（默认角色: ANNOTATOR）
    3. 如果存在，更新最后登录时间
    4. 缓存用户基本信息
    """
    # 查询本地用户
    user = await self.user_repo.get_by_user_id(user_id)

    if not user:
        # 首次登录，创建用户
        user = await self.user_repo.create(User(
            id=str(uuid.uuid4()),
            user_id=user_id,
            role="ANNOTATOR",  # 默认角色
            is_active=True,
            created_at=datetime.utcnow()
        ))
    else:
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        await self.user_repo.update(user)

    # 从USAP获取用户信息并缓存
    user_info = await self.usap_client.get_user_info(user_id)
    await self.cache_service.set_user_info(user_id, user_info)

    return user
```

#### 2.4.2 用户信息缓存
```python
# backend/app/services/user_cache_service.py
from typing import Optional
from datetime import datetime, timedelta
from app.schemas.usap import UserInfo

class UserCacheService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 3600  # 1小时

    async def get_user_info(self, user_id: str) -> Optional[UserInfo]:
        """从缓存获取用户信息"""
        key = f"user_info:{user_id}"
        data = await self.redis.get(key)

        if data:
            return UserInfo.parse_raw(data)
        return None

    async def set_user_info(self, user_id: str, user_info: UserInfo):
        """设置用户信息缓存"""
        key = f"user_info:{user_id}"
        await self.redis.setex(
            key,
            self.ttl,
            user_info.json()
        )
```

---

### 2.5 JWT Token生成（Step 10）

#### 2.5.1 Token Payload设计
```python
{
    "exp": 1738876800,           # 过期时间（8小时后）
    "iat": 1738848000,           # 签发时间
    "sub": "U001",               # UserID（主体）
    "role": "SYSTEM_ADMIN",      # 用户角色
    "scenarios": [               # 用户场景权限
        {
            "scenario_id": "test_001",
            "role": "SCENARIO_ADMIN",
            "permissions": {
                "scenario_basic_info": true,
                "scenario_keywords": true,
                "scenario_policies": true,
                "playground": true,
                "performance_test": true
            }
        }
    ]
}
```

#### 2.5.2 Token生成代码
```python
# backend/app/services/sso_service.py
from datetime import datetime, timedelta
import jwt
from app.core.config import settings

async def create_access_token(
    self,
    user_id: str,
    role: str,
    scenarios: List[dict]
) -> str:
    """
    生成JWT Access Token
    """
    now = datetime.utcnow()
    expire = now + timedelta(hours=8)

    payload = {
        "exp": expire,
        "iat": now,
        "sub": user_id,
        "role": role,
        "scenarios": scenarios
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token
```

---

## 三、后续API调用流程

### 3.1 携带Token访问API

```http
GET /api/v1/scenarios/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3.2 Token验证
```python
# backend/app/api/v1/deps.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt
from app.core.config import settings

security = HTTPBearer()

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    从JWT Token中提取UserID
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 3.3 获取用户完整信息
```python
@router.get("/sso/user-info")
async def get_current_user_info(
    user_id: str = Depends(get_current_user_id),
    cache_service: UserCacheService = Depends(),
    usap_client: USAPClient = Depends()
):
    """
    获取当前用户完整信息

    优先从缓存获取，缓存未命中则从USAP获取
    """
    # 尝试从缓存获取
    user_info = await cache_service.get_user_info(user_id)

    if user_info:
        return user_info

    # 缓存未命中，从USAP获取
    user_info = await usap_client.get_user_info(user_id)

    # 更新缓存
    await cache_service.set_user_info(user_id, user_info)

    return user_info
```

---

## 四、异常处理

### 4.1 Ticket验证失败

| 错误场景 | HTTP状态码 | 错误信息 | 处理方式 |
|---------|-----------|---------|---------|
| Ticket不存在 | 401 | Ticket invalid | 重定向到门户登录 |
| Ticket已过期 | 401 | Ticket expired | 重定向到门户登录 |
| Ticket已使用 | 401 | Ticket already used | 重定向到门户登录 |
| USAP服务不可用 | 503 | USAP service unavailable | 显示错误页面，稍后重试 |

### 4.2 JWT Token验证失败

| 错误场景 | HTTP状态码 | 错误信息 | 处理方式 |
|---------|-----------|---------|---------|
| Token不存在 | 401 | Not authenticated | 重定向到SSO登录 |
| Token已过期 | 401 | Token expired | 尝试刷新Token |
| Token无效 | 401 | Invalid token | 清除本地Token，重定向到SSO登录 |
| 用户被禁用 | 403 | User disabled | 显示禁用提示 |

### 4.3 前端错误处理
```typescript
// frontend/src/api.ts
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const errorDetail = error.response?.data?.detail;

      if (errorDetail === 'Token expired') {
        // 尝试刷新Token
        return refreshTokenAndRetry(error.config);
      } else {
        // 其他401错误，重定向到SSO登录
        localStorage.removeItem('access_token');
        window.location.href = '/sso/login';
      }
    }

    return Promise.reject(error);
  }
);
```

---

## 五、Token刷新机制

### 5.1 Refresh Token设计
```python
# 登录时同时返回Access Token和Refresh Token
{
    "access_token": "eyJhbGci...",   # 8小时有效
    "refresh_token": "eyJhbGci...",  # 7天有效
    "token_type": "bearer",
    "expires_in": 28800
}
```

### 5.2 刷新接口
```python
@router.post("/sso/refresh")
async def refresh_token(
    refresh_token: str,
    sso_service: SSOService = Depends()
):
    """
    刷新Access Token
    """
    try:
        # 验证Refresh Token
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")

        # 重新查询用户权限
        user = await sso_service.get_user(user_id)
        permissions = await sso_service.get_user_permissions(user_id)

        # 生成新的Access Token
        new_token = await sso_service.create_access_token(
            user_id=user_id,
            role=user.role,
            scenarios=permissions.scenarios
        )

        return {
            "access_token": new_token,
            "token_type": "bearer",
            "expires_in": 28800
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
```

---

## 六、登出流程

### 6.1 本地登出
```typescript
// 前端登出
const logout = () => {
  // 清除本地Token
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user_id');

  // 重定向到门户登出
  window.location.href = 'https://portal.company.com/logout';
};
```

### 6.2 全局登出（可选）
```python
@router.post("/sso/logout")
async def sso_logout(
    user_id: str = Depends(get_current_user_id),
    token: str = Depends(get_current_token)
):
    """
    SSO登出

    1. 将Token加入黑名单
    2. 通知USAP系统登出（可选）
    """
    # 将Token加入黑名单（Redis）
    await redis_client.setex(
        f"token_blacklist:{token}",
        28800,  # 8小时
        "1"
    )

    # 可选：通知USAP系统登出
    # await usap_client.logout(user_id)

    return {"message": "Logged out successfully"}
```

---

## 七、时序图

### 7.1 完整认证时序图
```
用户      门户      USAP      安全管理平台(前端)    安全管理平台(后端)
 │         │         │              │                    │
 │─登录───>│         │              │                    │
 │         │─认证───>│              │                    │
 │         │<─Ticket─│              │                    │
 │         │─重定向─────────────────>│                    │
 │         │         │              │─验证Ticket────────>│
 │         │         │              │                    │─验证Ticket─>USAP
 │         │         │              │                    │<─UserID────
 │         │         │              │                    │─查询权限─>DB
 │         │         │              │                    │<─权限信息─
 │         │         │              │<─JWT Token─────────│
 │<────────────────────────显示主页─│                    │
 │         │         │              │                    │
```

---

## 八、安全考虑

### 8.1 Ticket安全
- ✅ 一次性使用，防止重放攻击
- ✅ 短期有效（5分钟），减少窗口期
- ✅ HTTPS传输，防止中间人攻击
- ✅ 签名验证，防止篡改

### 8.2 JWT安全
- ✅ 签名验证，防止篡改
- ✅ 定期刷新，减少泄露风险
- ✅ 黑名单机制，支持强制登出
- ✅ Payload最小化，避免敏感信息泄露

### 8.3 通信安全
- ✅ 所有通信使用HTTPS
- ✅ API调用需要Client ID和Secret
- ✅ 限流和防暴力破解
- ✅ 审计日志记录所有认证操作

---

## 九、总结

### 9.1 认证流程特点
1. ✅ **标准SSO流程**: 符合企业级SSO标准
2. ✅ **双Token机制**: Ticket + JWT，安全可靠
3. ✅ **用户信息分离**: UserID为核心，信息从USAP获取
4. ✅ **缓存优化**: 减少USAP调用，提升性能

### 9.2 关键接口清单

| 系统 | 接口 | 说明 |
|------|------|------|
| USAP | POST /api/auth/login | 用户登录 |
| USAP | POST /api/auth/validate-ticket | 验证Ticket |
| USAP | GET /api/users/{userId} | 获取用户信息 |
| 安全管理平台 | POST /api/v1/sso/login | SSO登录 |
| 安全管理平台 | POST /api/v1/sso/refresh | 刷新Token |
| 安全管理平台 | POST /api/v1/sso/logout | 登出 |
| 安全管理平台 | GET /api/v1/sso/user-info | 获取用户信息 |

---

**下一步**: 请查看 `V2_DEPLOYMENT_ARCHITECTURE.md` 了解部署架构设计
