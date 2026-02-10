# LLM Guard Manager V2 完整需求与设计文档

## 版本信息
- **版本**: V2.1（审校版）
- **设计日期**: 2026-02-06
- **审校日期**: 2026-02-09
- **文档性质**: 合并文档（整合架构、认证、Mock USAP、Portal、RBAC、需求等设计）

---

## 一、项目概述

### 1.1 项目背景
LLM Guard Manager V1版本采用独立认证方式，用户信息完全存储在本地数据库。为了适应企业内网环境，需要升级到V2版本，集成企业统一认证系统（USAP），实现单点登录（SSO），并将用户信息管理外部化。

### 1.2 核心目标
1. **集成企业SSO**: 接入USAP统一认证系统
2. **用户信息外部化**: 用户基本信息从USAP获取，本地仅存储UserID和权限
3. **门户系统集成**: 通过门户系统跳转，使用Ticket机制认证
4. **保持业务功能**: 所有现有业务功能保持不变
5. **渐进式迁移**: 支持V1和V2共存，平滑迁移

### 1.3 涉及系统

| 系统 | 角色 | 职责 | 实现状态 |
|------|------|------|---------|
| USAP系统 | 认证中心 | 用户认证、用户信息管理、Ticket颁发 | Mock已实现 (`mock-usap/`) |
| 门户系统 | 统一入口 | 用户登录、系统导航、跳转分发 | 已实现 (`portal/`) |
| 安全管理平台 | 业务系统 | LLM安全策略管理、权限控制 | 已实现 (`backend/` + `frontend/`) |
| MySQL数据库 | 数据存储 | 业务数据、权限配置 | 已实现 |
| Redis | 缓存 | 用户信息缓存、会话管理（⚠️ 待实现） | ⚠️ 待实现 |

### 1.4 V1 vs V2 对比

| 维度 | V1（当前版本） | V2（目标版本） |
|------|---------------|---------------|
| 认证方式 | 独立认证（JWT） | SSO单点登录（Ticket） |
| 用户管理 | 本地用户表（完整信息） | 仅存储UserID（引用USAP） |
| 登录入口 | 直接登录 | 门户系统跳转 |
| 用户信息 | 本地存储 | 实时从USAP获取 |
| 会话管理 | JWT Token | Ticket + JWT |
| 适用场景 | 独立部署 | 企业内网集成 |

---

## 二、系统架构设计

### 2.1 系统拓扑

```
┌─────────────────────────────────────────────────────────────┐
│                        企业内网环境                           │
│                                                               │
│  ┌──────────┐      ┌──────────┐      ┌──────────────────┐  │
│  │  用户    │─────>│  门户系统 │─────>│  安全管理平台    │  │
│  │ (Browser)│      │ (Portal) │      │ (LLM Guard Mgr)  │  │
│  └──────────┘      └─────┬────┘      └────────┬─────────┘  │
│                           │                     │             │
│                           │                     │             │
│                           ▼                     ▼             │
│                    ┌─────────────┐      ┌─────────────┐     │
│                    │  USAP系统   │      │  MySQL DB   │     │
│                    │ (认证中心)   │      │ (业务数据)   │     │
│                    └─────────────┘      └─────────────┘     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 系统角色

#### 2.2.1 USAP系统（User Authentication Platform）
- **职责**: 统一认证中心
- **功能**: 用户身份认证、用户信息管理、Ticket生成与验证、用户权限基础信息
- **接口**:
  - `POST /api/auth/login` - 用户登录
  - `POST /api/auth/validate-ticket` - Ticket验证
  - `GET /api/users/{userId}` - 获取用户信息
  - `POST /api/users/batch` - 批量获取用户信息

#### 2.2.2 门户系统（Portal）
- **职责**: 统一入口和导航
- **功能**: 用户登录界面、系统导航菜单、跳转到各子系统（携带Ticket）、会话管理
- **跳转URL**: `https://llm-guard.company.com/sso/login?ticket={ticket}`

#### 2.2.3 安全管理平台（LLM Guard Manager）
- **职责**: LLM安全策略管理
- **认证流程**:
  1. 接收Portal传递的Ticket
  2. 调用USAP验证Ticket
  3. 获取UserID
  4. 查询本地权限配置
  5. 建立本地会话（JWT）

### 2.3 会话架构（双Token机制）

```
┌─────────────────────────────────────────┐
│  Ticket (USAP颁发)                      │
│  - 用途: 单次认证                        │
│  - 有效期: 5分钟                         │
│  - 使用次数: 一次性                      │
│  - 验证方: 安全管理平台调用USAP验证      │
└─────────────────────────────────────────┘
                    ↓
         验证成功后转换为
                    ↓
┌─────────────────────────────────────────┐
│  JWT Token (安全管理平台颁发)            │
│  - 用途: 后续API调用                     │
│  - 有效期: 8天 (ACCESS_TOKEN_EXPIRE_MINUTES) │
│  - 刷新机制: ⚠️ 待实现 (Refresh Token)   │
│  - Payload: {exp, sub(user_id), role}    │
└─────────────────────────────────────────┘
```

**会话生命周期**:
1. **Ticket阶段** (0-5分钟): 用户从门户跳转，携带Ticket，安全管理平台验证Ticket，一次性使用
2. **JWT阶段** (5分钟-8天): Ticket验证成功后颁发JWT，所有API调用使用JWT
3. **刷新阶段** (8天后): JWT过期，需重新从门户登录（⚠️ Refresh Token机制待实现）

### 2.4 技术栈

| 层次 | V1 | V2 | 变化说明 |
|------|----|----|---------|
| 前端 | React + TypeScript | React + TypeScript | 无变化 |
| 后端 | FastAPI | FastAPI | 无变化 |
| 认证 | JWT | Ticket + JWT | 新增Ticket验证 |
| 用户管理 | 本地数据库 | USAP API | 新增外部调用 |
| 会话 | JWT | JWT | 无变化 |
| 缓存 | 无 | ⚠️ Redis（待实现） | 计划新增用户信息缓存 |

### 2.5 新增组件

```python
# app/clients/usap_client.py（已实现）
class USAPClient:
    """USAP系统客户端"""
    async def validate_ticket(self, ticket: str) -> TicketValidationResult: ...
    async def get_user_info(self, user_id: str) -> UserInfo: ...
    async def get_users_batch(self, user_ids: List[str]) -> tuple[List[UserInfo], List[str]]: ...
    async def health_check(self) -> bool: ...

# app/services/sso_service.py（已实现）
class SSOService:
    """SSO单点登录服务"""
    async def login_with_ticket(self, ticket: str, db: AsyncSession) -> SSOLoginResponse: ...
    async def _sync_user_from_usap(self, user_id: str, validation_result, db) -> User: ...
    def _create_access_token(self, user_id: str, role: str) -> str: ...
    async def get_user_info(self, user_id: str, db: AsyncSession) -> Optional[SSOUserInfoResponse]: ...

# ⚠️ 待实现: app/services/user_cache_service.py
# class UserCacheService:
#     """用户信息缓存服务（需要Redis）"""
#     async def get_user_info(self, user_id: str) -> UserInfo: ...
#     async def refresh_cache(self, user_id: str) -> None: ...
```

---

## 三、认证流程设计

### 3.1 完整认证链路

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
     │ Step 11: 查询用户权限
     │ Step 12: 生成JWT Token
     ▼
┌──────────────────┐
│  安全管理平台    │
│  (Frontend)      │
└──────────────────┘
     │ 存储Token，跳转到主页
     ▼
┌──────────────────┐
│   主页面         │
└──────────────────┘
```

### 3.2 SSO登录实现

#### 3.2.1 前端接收Ticket
```typescript
// frontend/src/pages/SSOLogin.tsx（已实现）
import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Spin, Result, Button } from 'antd';
import { ssoApi } from '../api';
import { usePermission } from '../hooks/usePermission';

const SSOLogin: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { refreshPermissions } = usePermission();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState<string>('');

  useEffect(() => {
    const ticket = searchParams.get('ticket');
    const returnUrl = searchParams.get('return_url') || '/';

    if (!ticket) {
      setStatus('error');
      setErrorMessage('缺少Ticket参数，请从门户系统登录');
      return;
    }

    const doLogin = async () => {
      try {
        const response = await ssoApi.login(ticket);
        const { access_token, role, user_id } = response.data;

        localStorage.setItem('access_token', access_token);
        localStorage.setItem('user_role', role);
        localStorage.setItem('user_id', user_id);

        await refreshPermissions();
        setStatus('success');
        setTimeout(() => {
          navigate(returnUrl, { replace: true });
        }, 500);
      } catch (error: any) {
        setStatus('error');
        const detail = error.response?.data?.detail || '登录失败，请重试';
        setErrorMessage(detail);
      }
    };

    doLogin();
  }, [searchParams, navigate]);

  // 渲染: loading状态显示Spin, error状态显示Result(error), success状态显示Result(success)
};
```

#### 3.2.2 后端SSO登录接口
```python
# backend/app/api/v1/endpoints/sso.py（已实现）
@router.post("/login", response_model=SSOLoginResponse)
async def sso_login(
    request: SSOLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    SSO单点登录流程:
    1. 验证Ticket  2. 获取UserID  3. 同步/创建本地用户  4. 生成JWT Token
    """
    try:
        result = await sso_service.login_with_ticket(request.ticket, db)
        return result
    except SSOServiceError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")
```

#### 3.2.3 USAP客户端 validate_ticket
```python
# backend/app/clients/usap_client.py（已实现）
class USAPClient:
    def __init__(self):
        self.base_url = settings.USAP_BASE_URL
        self.client_id = settings.USAP_CLIENT_ID
        self.client_secret = settings.USAP_CLIENT_SECRET
        self.timeout = 5.0

    async def validate_ticket(self, ticket: str) -> TicketValidationResult:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/auth/validate-ticket",
                    json={"ticket": ticket},
                    headers={
                        "Content-Type": "application/json",
                        "X-Client-ID": self.client_id,
                        "X-Client-Secret": self.client_secret
                    }
                )
                if response.status_code == 401:
                    data = response.json()
                    return TicketValidationResult(
                        valid=False,
                        error=data.get("detail", "Ticket验证失败")
                    )
                if response.status_code != 200:
                    return TicketValidationResult(
                        valid=False,
                        error=f"USAP服务错误: {response.status_code}"
                    )
                data = response.json()
                return TicketValidationResult(
                    valid=True, user_id=data.get("user_id"),
                    user_name=data.get("user_name"),
                    email=data.get("email"),
                    department=data.get("department"),
                    phone=data.get("phone")
                )
        except httpx.TimeoutException:
            return TicketValidationResult(valid=False, error="USAP服务超时")
        except Exception as e:
            return TicketValidationResult(valid=False, error=f"USAP服务异常: {str(e)}")
```

### 3.3 用户信息同步

```python
# backend/app/services/sso_service.py（已实现）
async def _sync_user_from_usap(
    self,
    user_id: str,
    validation_result: TicketValidationResult,
    db: AsyncSession
) -> User:
    """
    策略:
    1. 查询本地是否存在该用户（通过user_id字段）
    2. 如果不存在，创建新用户（默认角色: ANNOTATOR）
       - 兼容V1: 使用user_id作为username，hashed_password设为空字符串
    3. 如果存在，更新updated_at和display_name
    注意: 当前未实现缓存服务
    """
    query = select(User).where(User.user_id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        user = User(
            id=str(uuid.uuid4()),
            user_id=user_id,
            username=user_id,  # 兼容V1，使用user_id作为username
            hashed_password="",  # SSO用户不需要密码
            display_name=validation_result.user_name,
            role="ANNOTATOR",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        user.updated_at = datetime.utcnow()
        if validation_result.user_name:
            user.display_name = validation_result.user_name
        await db.commit()

    return user
```

**⚠️ 待实现: 用户信息缓存服务**

以下缓存服务需要Redis支持，当前未实现:
```python
# 计划: app/services/user_cache_service.py
class UserCacheService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = 3600  # 1小时

    async def get_user_info(self, user_id: str) -> Optional[UserInfo]:
        key = f"user_info:{user_id}"
        data = await self.redis.get(key)
        if data:
            return UserInfo.parse_raw(data)
        return None

    async def set_user_info(self, user_id: str, user_info: UserInfo):
        key = f"user_info:{user_id}"
        await self.redis.setex(key, self.ttl, user_info.json())
```

### 3.4 JWT Token设计

**Token Payload（实际实现）**:
```python
{
    "exp": 1738876800,           # 过期时间（8天后，由ACCESS_TOKEN_EXPIRE_MINUTES控制）
    "sub": "U001",               # UserID（主体）
    "role": "SYSTEM_ADMIN"       # 用户角色
}
```

> **注意**: 当前实现不包含 `iat`（签发时间）和 `scenarios`（场景权限）字段。
> 场景权限通过 `GET /api/v1/permissions/me` 接口单独查询。

**Token生成代码（实际实现）**:
```python
# backend/app/services/sso_service.py
def _create_access_token(self, user_id: str, role: str) -> str:
    """生成JWT Access Token"""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "exp": expire,
        "sub": user_id,
        "role": role
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token
```

### 3.5 Token刷新机制（⚠️ 待实现）

> **当前状态**: Token刷新机制尚未实现。`/sso/refresh` 端点不存在。
> 当前JWT有效期为8天（`ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8`），过期后需重新从门户登录。
> 登录响应中也不包含 `refresh_token` 字段。

**计划实现**:
```python
# 登录时同时返回Access Token和Refresh Token
{
    "access_token": "eyJhbGci...",   # 8小时有效
    "refresh_token": "eyJhbGci...",  # 7天有效
    "token_type": "bearer",
    "expires_in": 28800
}
```

**计划刷新接口**:
```python
@router.post("/sso/refresh")
async def refresh_token(refresh_token: str, sso_service: SSOService = Depends()):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        user = await sso_service.get_user(user_id)
        permissions = await sso_service.get_user_permissions(user_id)
        new_token = await sso_service.create_access_token(
            user_id=user_id, role=user.role, scenarios=permissions.scenarios
        )
        return {"access_token": new_token, "token_type": "bearer", "expires_in": 28800}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
```

### 3.6 登出流程

**前端登出（已实现）**:
```typescript
// 前端通过清除localStorage实现登出
// 401响应拦截器中自动清除token并重定向到/login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_role');
      localStorage.removeItem('current_app_id');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

**⚠️ 待实现: 后端登出（全局登出）**:

> `/sso/logout` 端点尚未实现。需要Redis支持Token黑名单机制。

```python
# 计划实现:
@router.post("/sso/logout")
async def sso_logout(
    user_id: str = Depends(get_current_user_id),
    token: str = Depends(get_current_token)
):
    # 将Token加入黑名单（Redis）
    await redis_client.setex(f"token_blacklist:{token}", 28800, "1")
    return {"message": "Logged out successfully"}
```

### 3.7 异常处理

**Ticket验证失败**:

| 错误场景 | HTTP状态码 | 错误信息 | 处理方式 |
|---------|-----------|---------|---------|
| Ticket不存在 | 401 | Ticket invalid | 重定向到门户登录 |
| Ticket已过期 | 401 | Ticket expired | 重定向到门户登录 |
| Ticket已使用 | 401 | Ticket already used | 重定向到门户登录 |
| USAP服务不可用 | 503 | USAP service unavailable | 显示错误页面，稍后重试 |

**JWT Token验证失败**:

| 错误场景 | HTTP状态码 | 错误信息 | 处理方式 |
|---------|-----------|---------|---------|
| Token不存在 | 401 | Not authenticated | 重定向到SSO登录 |
| Token已过期 | 401 | Token expired | 尝试刷新Token |
| Token无效 | 401 | Invalid token | 清除本地Token，重定向到SSO登录 |
| 用户被禁用 | 403 | User disabled | 显示禁用提示 |

### 3.8 时序图

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

## 四、功能需求

### 4.1 认证相关需求

#### 4.1.1 SSO单点登录
**需求描述**: 用户通过门户系统登录后，携带Ticket跳转到安全管理平台，平台验证Ticket后建立会话。

**功能点**:
- [x] 接收门户系统传递的Ticket参数
- [x] 调用USAP接口验证Ticket有效性
- [x] Ticket验证成功后获取UserID
- [x] 根据UserID查询/创建本地用户记录
- [x] 生成JWT Token并返回给前端
- [x] 前端存储Token并跳转到主页

**接口定义（已实现）**:
```
POST /api/v1/sso/login
Request:  { "ticket": "TK_xxx" }
Response: {
  "access_token": "eyJhbGci...",
  "token_type": "bearer", "expires_in": 11520,
  "user_id": "U001", "role": "ANNOTATOR"
}
```

> **注意**: 实际响应不包含 `refresh_token` 字段。`expires_in` 值为 `ACCESS_TOKEN_EXPIRE_MINUTES * 60`（默认8天 = 691200秒）。新用户默认角色为 `ANNOTATOR`。

**验证标准**:
- Ticket验证失败返回401错误
- Ticket过期返回401错误
- 验证成功返回有效JWT Token
- Token包含user_id和role信息（不包含scenarios）

#### 4.1.2 Token刷新（⚠️ 待实现）
**功能点**:
- [ ] 提供Token刷新接口
- [ ] 验证Refresh Token有效性
- [ ] 重新查询用户权限
- [ ] 生成新的Access Token

```
POST /api/v1/sso/refresh  （⚠️ 待实现）
Request:  { "refresh_token": "eyJhbGci..." }
Response: { "access_token": "eyJhbGci...", "token_type": "bearer", "expires_in": 28800 }
```

#### 4.1.3 登出（⚠️ 后端待实现）
**功能点**:
- [x] 前端清除本地Token（已实现，通过401拦截器）
- [ ] 后端将Token加入黑名单（⚠️ 待实现，需要Redis）
- [ ] 可选：通知USAP系统登出
- [ ] 重定向到门户系统登出页面

```
POST /api/v1/sso/logout  （⚠️ 待实现）
Response: { "message": "Logged out successfully" }
```

### 4.2 用户信息相关需求

#### 4.2.1 获取当前用户信息
**功能点**:
- [x] 从JWT Token提取UserID
- [ ] 优先从缓存获取用户信息（⚠️ 待实现，需要Redis）
- [x] 从USAP获取用户信息（已实现，直接调用USAP API）
- [ ] 更新缓存并返回用户信息（⚠️ 待实现）

```
GET /api/v1/sso/user-info
Response: {
  "user_id": "U001", "user_name": "张三",
  "email": "zhangsan@company.com", "department": "技术部",
  "role": "SYSTEM_ADMIN", "scenarios": [...]
}
```

#### 4.2.2 批量获取用户信息
**功能点**:
- [x] 接收UserID列表
- [ ] 批量从缓存查询（⚠️ 待实现，需要Redis）
- [x] 从USAP批量查询（已实现，直接调用USAP API）
- [ ] 更新缓存并返回结果（⚠️ 待实现）

```
POST /api/v1/sso/users/batch
Request:  { "user_ids": ["U001", "U002", "U003"] }
Response: { "users": [ { "user_id": "U001", "user_name": "张三", ... }, ... ] }
```

#### 4.2.3 用户信息缓存管理（⚠️ 全部待实现，需要Redis）
**功能点**:
- [ ] 缓存TTL: 1小时
- [ ] 提供手动刷新接口
- [ ] 提供清除缓存接口
- [ ] 定期清理过期缓存

### 4.3 USAP客户端需求

#### 4.3.1 Ticket验证接口
**USAP接口规范**:
```
POST https://usap.company.com/api/auth/validate-ticket
Headers: X-Client-ID: llm-guard-manager / X-Client-Secret: {secret}
Request:  { "ticket": "TK_xxx" }
Response: { "valid": true, "user_id": "U001", "user_name": "张三", "email": "...", "department": "..." }
```

**功能点**: 实现USAP客户端（已实现）、支持Ticket验证（已实现）、处理USAP API错误（已实现）、超时重试机制（⚠️ 待实现，当前仅超时处理无重试）、记录调用日志（⚠️ 待实现）

#### 4.3.2 获取用户信息接口
```
GET https://usap.company.com/api/users/{user_id}
Headers: X-Client-ID: llm-guard-manager / X-Client-Secret: {secret}
Response: { "user_id": "U001", "user_name": "张三", "email": "...", "department": "...", "phone": "...", "status": "active" }
```

### 4.4 数据库变更需求

#### 4.4.1 用户表改造

**V1表结构**:
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(20),
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**V2表结构（实际实现）**:
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(64) UNIQUE,              -- USAP的UserID（nullable，渐进式迁移）
    username VARCHAR(64) UNIQUE NOT NULL,     -- 保留V1字段（SSO用户设为user_id）
    hashed_password VARCHAR(128) NOT NULL,    -- 保留V1字段（SSO用户设为空字符串）
    role VARCHAR(32) DEFAULT 'ANNOTATOR',     -- 本地角色
    display_name VARCHAR(128),               -- 保留V1字段（SSO用户从USAP同步）
    email VARCHAR(128),                      -- 保留V1字段
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by VARCHAR(36),
    INDEX idx_user_id (user_id),
    INDEX idx_username (username)
);
```

> **注意**: 实际实现采用渐进式迁移策略:
> - `user_id` 字段为 **nullable**（允许V1用户暂时没有USAP ID）
> - 保留了 `username`、`hashed_password`、`display_name`、`email` 等V1字段
> - **没有** `last_login_at` 字段（使用 `updated_at` 代替）
> - 新增了 `created_by` 字段

**迁移脚本**:
```sql
-- 添加user_id字段（nullable，允许渐进式迁移）
ALTER TABLE users ADD COLUMN user_id VARCHAR(64);
ALTER TABLE users ADD UNIQUE INDEX idx_user_id (user_id);
-- 可选：为现有用户设置user_id
UPDATE users SET user_id = username WHERE user_id IS NULL;
-- 注意: 当前实现保留了所有V1字段（username, hashed_password, display_name, email）
-- 完全迁移后可选清理:
-- ALTER TABLE users DROP COLUMN hashed_password;
-- ALTER TABLE users DROP COLUMN email;
-- ALTER TABLE users DROP COLUMN display_name;
```

#### 4.4.2 用户信息缓存表（⚠️ 可选，待实现）
```sql
CREATE TABLE user_info_cache (
    user_id VARCHAR(50) PRIMARY KEY,
    user_name VARCHAR(100),
    email VARCHAR(100),
    department VARCHAR(100),
    phone VARCHAR(20),
    cached_at TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_expires_at (expires_at)
);
```

---

## 五、非功能需求

### 5.1 性能需求

#### 5.1.1 响应时间
| 接口 | 目标响应时间 | 说明 |
|------|-------------|------|
| SSO登录 | < 1秒 | 包含Ticket验证和Token生成 |
| Token刷新 | < 200ms | 仅查询数据库和生成Token |
| 获取用户信息（缓存命中） | < 50ms | 从Redis读取 |
| 获取用户信息（缓存未命中） | < 500ms | 调用USAP API |
| 批量获取用户信息 | < 1秒 | 最多100个用户 |

#### 5.1.2 并发能力
- 支持1000+ QPS
- SSO登录峰值: 100 QPS
- 用户信息查询峰值: 500 QPS

#### 5.1.3 缓存命中率
- 用户信息缓存命中率 > 90%
- 缓存TTL: 1小时
- 缓存预热策略: 登录时自动缓存

### 5.2 可用性需求

#### 5.2.1 服务可用性
- 系统可用性: 99.9%
- 计划内停机时间: < 4小时/月
- 故障恢复时间: < 15分钟

#### 5.2.2 降级策略
| 场景 | 降级方案 | 状态 |
|------|---------|------|
| USAP不可用 | 使用缓存的用户信息，显示警告 | ⚠️ 缓存待实现，当前直接失败 |
| Redis不可用 | 直接调用USAP，性能下降 | ⚠️ Redis未集成 |
| 数据库不可用 | 返回503错误，拒绝服务 | 已实现 |

#### 5.2.3 容错机制
- USAP API调用超时: 5秒（已实现）
- 重试次数: ⚠️ 待实现（当前无重试机制）
- 重试间隔: 计划1秒、2秒、4秒（指数退避）

### 5.3 安全需求

#### 5.3.1 认证安全
- [x] Ticket一次性使用（Mock USAP已实现）
- [x] Ticket有效期: 5分钟（Mock USAP已实现）
- [x] JWT签名验证（已实现）
- [ ] Token黑名单机制（⚠️ 待实现，需要Redis）
- [ ] 所有通信使用HTTPS

#### 5.3.2 数据安全
- [ ] 敏感数据不存储在本地
- [ ] 用户信息缓存加密（可选）
- [ ] 审计日志记录所有认证操作
- [ ] 定期清理过期数据

#### 5.3.3 API安全
- [ ] Client ID和Secret验证
- [ ] API限流: 100 req/min/user
- [ ] 防暴力破解: 5次失败锁定10分钟
- [ ] CORS配置限制来源

### 5.4 可维护性需求

#### 5.4.1 日志记录
- [ ] 所有认证操作记录日志
- [ ] USAP API调用记录日志
- [ ] 错误日志包含堆栈信息
- [ ] 日志格式: JSON
- [ ] 日志级别: INFO, WARNING, ERROR

#### 5.4.2 监控指标
- [ ] Ticket验证成功率
- [ ] USAP API响应时间
- [ ] 用户信息缓存命中率
- [ ] SSO登录成功率
- [ ] Token刷新成功率

#### 5.4.3 告警规则
- [ ] USAP API连续失败 > 5次
- [ ] Ticket验证失败率 > 5%
- [ ] 缓存命中率 < 80%
- [ ] SSO登录失败率 > 10%

---

## 六、接口规范

### 6.1 后端API接口

#### 6.1.1 SSO相关接口
| 接口 | 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|------|
| SSO登录 | POST | /api/v1/sso/login | Ticket验证并登录 | 已实现 |
| Token刷新 | POST | /api/v1/sso/refresh | 刷新Access Token | ⚠️ 待实现 |
| 登出 | POST | /api/v1/sso/logout | 用户登出 | ⚠️ 待实现 |
| 获取用户信息 | GET | /api/v1/sso/user-info | 获取当前用户信息 | 已实现 |
| 批量获取用户 | POST | /api/v1/sso/users/batch | 批量获取用户信息 | 已实现 |
| SSO健康检查 | GET | /api/v1/sso/health | 检查USAP服务可用性 | 已实现 |

#### 6.1.2 USAP接口（外部）
| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 验证Ticket | POST | /api/auth/validate-ticket | 验证Ticket有效性 |
| 获取用户信息 | GET | /api/users/{userId} | 获取单个用户信息 |
| 批量获取用户 | POST | /api/users/batch | 批量获取用户信息 |
| 健康检查 | GET | /api/health | 检查服务可用性 |

### 6.2 前端路由

#### 6.2.1 新增路由
| 路由 | 组件 | 说明 |
|------|------|------|
| /sso/login | SSOLogin | SSO登录页面 |
| /sso/callback | SSOCallback | SSO回调页面（可选） |

#### 6.2.2 修改路由
- 移除 `/login` 路由（或保留作为备用）
- 所有未认证访问重定向到门户系统

### 6.3 前端SSO API（已实现）

前端SSO API定义在 `frontend/src/api.ts` 中:

```typescript
// frontend/src/api.ts
export const ssoApi = {
  // SSO登录（使用Ticket）
  login: (ticket: string) => api.post<{
    access_token: string;
    token_type: string;
    expires_in: number;
    user_id: string;
    role: string;
  }>('/sso/login', { ticket }),

  // 获取当前用户信息
  getUserInfo: () => api.get<{
    user_id: string;
    user_name: string;
    email?: string;
    department?: string;
    phone?: string;
    role: string;
    scenarios: any[];
  }>('/sso/user-info'),

  // 批量获取用户信息
  getUsersBatch: (userIds: string[]) => api.post<{
    users: Array<{
      user_id: string;
      user_name: string;
      email?: string;
      department?: string;
    }>;
    not_found: string[];
  }>('/sso/users/batch', { user_ids: userIds }),

  // SSO健康检查
  health: () => api.get<{
    sso_enabled: boolean;
    usap_healthy: boolean;
  }>('/sso/health'),
};
```

> **注意**: 前端ssoApi没有 `loginWithTicket` 方法（文档3.2.1中曾引用），实际方法名为 `login`。
> 也没有 `refresh` 或 `logout` 方法（对应后端待实现的端点）。

---

## 七、数据模型

### 7.1 核心数据模型

#### 7.1.1 User（用户）
```python
class User(Base):
    """用户表 - 扩展支持 RBAC 和 SSO"""
    __tablename__ = "users"
    id: str                    # 本地ID (CHAR(36), PK)
    user_id: Optional[str]    # USAP的UserID（nullable，渐进式迁移）
    username: str             # 用户名（保留V1字段，SSO用户设为user_id）
    hashed_password: str      # 密码哈希（保留V1字段，SSO用户设为空字符串）
    role: str                 # 本地角色 (SYSTEM_ADMIN, SCENARIO_ADMIN, ANNOTATOR, AUDITOR)
    display_name: Optional[str]  # 显示名称（保留V1字段，SSO用户从USAP同步）
    email: Optional[str]      # 邮箱（保留V1字段）
    is_active: bool           # 激活状态
    created_at: datetime      # 创建时间
    updated_at: Optional[datetime]  # 更新时间（SSO登录时更新，替代last_login_at）
    created_by: Optional[str] # 创建者
```

> **注意**: 实际模型没有 `last_login_at` 字段，使用 `updated_at` 记录最后活动时间。

#### 7.1.2 UserInfo（用户信息，从USAP获取）
```python
class UserInfo(BaseModel):
    user_id: str
    user_name: str
    email: str
    department: str
    phone: Optional[str]
    status: str
```

#### 7.1.3 TicketValidationResult（Ticket验证结果）
```python
class TicketValidationResult(BaseModel):
    valid: bool
    user_id: Optional[str]
    user_name: Optional[str]
    email: Optional[str]
    department: Optional[str]
    error: Optional[str]
```

#### 7.1.4 SSOLoginResponse（SSO登录响应）
```python
# backend/app/schemas/sso.py（实际实现）
class SSOLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    role: str
```

> **注意**: 实际响应不包含 `refresh_token` 字段。

**其他SSO Schema（已实现）**:
```python
class SSOUserInfoResponse(BaseModel):
    """SSO用户信息响应"""
    user_id: str
    user_name: str
    email: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    role: str
    scenarios: List[dict] = []

class SSOBatchUsersRequest(BaseModel):
    """批量获取用户请求"""
    user_ids: List[str]

class SSOUserBrief(BaseModel):
    """用户简要信息"""
    user_id: str
    user_name: str
    email: Optional[str] = None
    department: Optional[str] = None

class SSOBatchUsersResponse(BaseModel):
    """批量获取用户响应"""
    users: List[SSOUserBrief]
    not_found: List[str]
```

---

## 八、Mock USAP 服务设计

### 8.1 概述
创建一个独立的Mock服务，模拟企业USAP（统一认证平台）的核心功能，用于：
- V2版本开发阶段的联调测试
- 验证SSO认证流程
- 模拟各种异常场景

### 8.2 项目结构
```
mock-usap/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口（注册路由、CORS、健康检查）
│   ├── routes/
│   │   ├── __init__.py         # 导出 auth_router, users_router
│   │   ├── auth.py             # 认证相关接口（login, ticket, validate-ticket）
│   │   └── users.py            # 用户信息接口（单个查询、批量查询）
│   ├── services/
│   │   ├── __init__.py         # 导出 user_service, session_service, ticket_service
│   │   ├── session_service.py  # Session管理（创建、验证、获取user_id）
│   │   ├── ticket_service.py   # Ticket管理（创建、验证、一次性使用）
│   │   └── user_service.py     # 用户管理（认证、查询、批量查询）
│   └── data/
│       └── mock_users.json     # Mock用户数据（10个测试用户）
├── tests/                      # 测试目录（空）
├── Dockerfile
├── requirements.txt
└── README.md
```

> **注意**: 实际结构与原设计的区别:
> - 没有 `config.py`（配置直接在各服务中硬编码）
> - 没有 `models.py`（使用Pydantic BaseModel内联定义）
> - 新增 `session_service.py`（Session管理独立为服务）
> - 没有 `tests/test_api.py`（tests目录为空）

### 8.3 API接口

#### 8.3.1 用户登录（建立会话）
```
POST /api/auth/login
Request:  { "username": "zhangsan", "password": "123456" }
成功响应 (200): { "success": true, "session_id": "SES_a1b2c3d4e5f6g7h8", "user_id": "U001", "user_name": "张三", "expires_in": 28800 }
失败响应 (401): { "success": false, "error": "用户名或密码错误" }
```

#### 8.3.2 获取Ticket（跳转时调用）
```
POST /api/auth/ticket
Request:  { "session_id": "SES_a1b2c3d4e5f6g7h8", "target_system": "llm-guard-manager" }
成功响应 (200): { "success": true, "ticket": "TK_a1b2c3d4...", "expires_in": 300, "target_system": "llm-guard-manager" }
失败响应 (401): { "success": false, "error": "Session无效或已过期" }
```

#### 8.3.3 验证Ticket（目标系统调用）
```
POST /api/auth/validate-ticket
Headers: X-Client-ID: llm-guard-manager / X-Client-Secret: mock-secret-key
Request:  { "ticket": "TK_a1b2c3d4..." }
成功响应 (200): { "valid": true, "user_id": "U001", "user_name": "张三", "email": "zhangsan@company.com", "department": "技术部", "phone": "13800138001" }
失败响应 (401): { "valid": false, "error": "Ticket无效" }  -- 或 "Ticket已过期" / "Ticket已被使用"
```

#### 8.3.4 获取单个用户信息
```
GET /api/users/{user_id}
Headers: X-Client-ID: llm-guard-manager / X-Client-Secret: mock-secret-key
成功响应 (200): { "user_id": "U001", "user_name": "张三", "email": "zhangsan@company.com", "department": "技术部", "phone": "13800138001", "status": "active" }
失败响应 (404): { "error": "用户不存在" }
```

#### 8.3.5 批量获取用户信息
```
POST /api/users/batch
Headers: X-Client-ID: llm-guard-manager / X-Client-Secret: mock-secret-key
Request:  { "user_ids": ["U001", "U002", "U003"] }
响应 (200): { "users": [ { "user_id": "U001", "user_name": "张三", ... }, ... ], "not_found": ["U003"] }
```

#### 8.3.6 健康检查
```
GET /api/health
响应 (200): { "status": "healthy", "service": "mock-usap", "version": "1.0.0" }
```

### 8.4 Mock数据

**10个测试用户**:
```json
{
  "users": [
    { "user_id": "U001", "username": "zhangsan", "password": "123456", "user_name": "张三", "email": "zhangsan@company.com", "department": "技术部", "phone": "13800138001", "status": "active" },
    { "user_id": "U002", "username": "lisi", "password": "123456", "user_name": "李四", "email": "lisi@company.com", "department": "产品部", "phone": "13800138002", "status": "active" },
    { "user_id": "U003", "username": "wangwu", "password": "123456", "user_name": "王五", "email": "wangwu@company.com", "department": "运营部", "phone": "13800138003", "status": "active" },
    { "user_id": "U004", "username": "zhaoliu", "password": "123456", "user_name": "赵六", "email": "zhaoliu@company.com", "department": "技术部", "phone": "13800138004", "status": "active" },
    { "user_id": "U005", "username": "sunqi", "password": "123456", "user_name": "孙七", "email": "sunqi@company.com", "department": "安全部", "phone": "13800138005", "status": "active" },
    { "user_id": "U006", "username": "zhouba", "password": "123456", "user_name": "周八", "email": "zhouba@company.com", "department": "技术部", "phone": "13800138006", "status": "inactive" },
    { "user_id": "U007", "username": "wujiu", "password": "123456", "user_name": "吴九", "email": "wujiu@company.com", "department": "产品部", "phone": "13800138007", "status": "active" },
    { "user_id": "U008", "username": "zhengshi", "password": "123456", "user_name": "郑十", "email": "zhengshi@company.com", "department": "运营部", "phone": "13800138008", "status": "active" },
    { "user_id": "U009", "username": "admin", "password": "admin123", "user_name": "系统管理员", "email": "admin@company.com", "department": "IT部", "phone": "13800138009", "status": "active" },
    { "user_id": "U010", "username": "test", "password": "test123", "user_name": "测试用户", "email": "test@company.com", "department": "测试部", "phone": "13800138010", "status": "active" }
  ]
}
```

**用户角色映射建议**:

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

### 8.5 Session和Ticket管理

**Session生成规则**:
```python
def generate_session_id() -> str:
    """格式: SES_{随机字符串16位}"""
    random_part = secrets.token_hex(8)
    return f"SES_{random_part}"
```

**Session存储结构**:
```python
sessions = {
    "SES_xxx": {
        "user_id": "U001",
        "created_at": 1738848000,
        "expires_at": 1738876800,  # 8小时后
    }
}
```

**Ticket生成规则**:
```python
def generate_ticket() -> str:
    """格式: TK_{随机字符串32位}"""
    random_part = secrets.token_hex(16)
    return f"TK_{random_part}"
```

**Ticket存储结构**:
```python
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

### 8.6 部署配置

**Dockerfile**:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**requirements.txt**:
```
fastapi==0.109.0
uvicorn==0.27.0
pydantic==2.5.3
```

**K8s部署配置**:
```yaml
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

**本地运行**:
```bash
cd mock-usap
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

**安全管理平台配置（实际实现）**:
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    USAP_BASE_URL: str = "http://mock-usap-svc:8080"  # K8s内部地址
    USAP_CLIENT_ID: str = "llm-guard-manager"
    USAP_CLIENT_SECRET: str = "mock-secret"
    SSO_ENABLED: bool = True  # 是否启用SSO登录
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天
```

---

## 八（附）、门户服务（Portal Service）

### 8A.1 概述
门户服务是统一登录入口，提供用户登录界面和应用跳转功能。用户通过门户登录后，可以选择目标应用并携带Ticket跳转。

**项目位置**: `portal/`

### 8A.2 项目结构
```
portal/
├── main.py              # FastAPI应用（包含所有API端点和HTML页面）
└── requirements.txt     # 依赖: fastapi, uvicorn, httpx, pydantic
```

### 8A.3 配置
```python
# 环境变量
USAP_BASE_URL = os.getenv("USAP_BASE_URL", "http://mock-usap-svc:8080")
PORTAL_BASE_PATH = os.getenv("PORTAL_BASE_PATH", "/portal")

# 目标应用配置
TARGET_APPS = {
    "llm-guard-manager": {
        "name": "LLM安全管理平台",
        "url": "/web-manager/",
        "sso_path": "/web-manager/sso/login"
    }
}
```

### 8A.4 API接口

#### 8A.4.1 健康检查
```
GET /api/health
Response: { "status": "healthy", "service": "portal" }
```

#### 8A.4.2 用户登录
```
POST /api/login
Request:  { "username": "zhangsan", "password": "123456" }
成功响应: { "success": true, "session_id": "SES_xxx", "user_name": "张三" }
失败响应: { "success": false, "error": "登录失败" }
```
> 内部调用 USAP 的 `POST /api/auth/login` 接口

#### 8A.4.3 获取应用列表
```
GET /api/apps
Response: [{ "id": "llm-guard-manager", "name": "LLM安全管理平台", "url": "/web-manager/" }]
```

#### 8A.4.4 跳转到应用（获取Ticket）
```
POST /api/jump
Request:  { "session_id": "SES_xxx", "target_app": "llm-guard-manager" }
成功响应: { "success": true, "redirect_url": "/web-manager/sso/login?ticket=TK_xxx" }
失败响应: HTTP 400 { "detail": "获取Ticket失败" }
```
> 内部调用 USAP 的 `POST /api/auth/ticket` 接口获取Ticket，然后拼接跳转URL

### 8A.5 页面

| 路由 | 功能 | 说明 |
|------|------|------|
| `/` | 登录页面 | 用户名/密码登录表单，登录成功后跳转到 `/apps` |
| `/apps` | 应用列表页面 | 显示可用应用卡片，点击后获取Ticket并跳转 |

### 8A.6 登录流程
```
1. 用户访问门户首页 (/)
2. 输入用户名/密码，POST /api/login
3. 门户调用 USAP /api/auth/login 验证
4. 验证成功，保存 session_id 到 sessionStorage
5. 跳转到应用列表页 (/apps)
6. 用户点击目标应用，POST /api/jump
7. 门户调用 USAP /api/auth/ticket 获取Ticket
8. 返回跳转URL: /web-manager/sso/login?ticket=TK_xxx
9. 前端重定向到目标应用的SSO登录页面
```

### 8A.7 运行方式
```bash
cd portal
pip install -r requirements.txt
python main.py  # 或 uvicorn main:app --host 0.0.0.0 --port 8080
```

---

## 九、RBAC 权限模型

> 详细设计请参考 `RBAC_REQUIREMENTS.md`

### 9.1 设计理念

采用标准 RBAC（Role-Based Access Control）模型：

```
角色 (Role) → 绑定菜单/功能权限 (Permission)
     ↓
用户 (User) → 按场景分配角色 (User-Scenario-Role)
```

**核心原则**:
1. 权限绑定在角色上，而非用户上
2. 用户通过分配角色获得权限
3. 角色分为全局角色和场景级角色
4. 权限分为全局权限和场景级权限

### 9.2 预置角色

| 角色编码 | 角色名称 | 类型 | 权限 |
|----------|----------|------|------|
| SYSTEM_ADMIN | 系统管理员 | GLOBAL | 所有权限 |
| AUDITOR | 审计员 | GLOBAL | smart_labeling, annotator_stats, audit_logs |
| SCENARIO_ADMIN | 场景管理员 | SCENARIO | smart_labeling, scenario_* 系列, playground, performance_test |
| ANNOTATOR | 标注员 | SCENARIO | smart_labeling |

### 9.3 权限检查流程

```
1. 用户登录 → 获取 JWT Token
2. 前端调用 GET /permissions/me
3. 后端查询:
   a. user_scenario_roles 获取用户所有角色
   b. role_permissions 获取角色对应权限
   c. 合并去重返回权限列表
4. 前端根据权限列表:
   a. 动态渲染菜单
   b. 控制按钮显示/隐藏
5. 后端 API 权限校验:
   a. 全局权限: require_permission("permission_code")
   b. 场景权限: require_permission("permission_code", scenario_id)
```

---

## 十、开发任务分解

### 10.1 阶段1: USAP Mock服务开发（1-2天）✅ 已完成
- [x] 创建Mock服务项目结构
- [x] 实现Ticket生成/验证接口
- [x] 实现用户信息查询接口（单个+批量）
- [x] 添加Mock数据（10个测试用户）
- [x] Docker化Mock服务
- **交付物**: `mock-usap/` 目录、Docker镜像、API文档

### 10.2 阶段2: 后端SSO功能开发（3-4天）🔶 部分完成
- [x] 创建USAP客户端 (`app/clients/usap_client.py`)
- [x] 创建SSO服务 (`app/services/sso_service.py`)
- [ ] 创建用户缓存服务 (`app/services/user_cache_service.py`) ⚠️ 待实现
- [x] 创建SSO Schema (`app/schemas/sso.py`)
- [x] 创建SSO API端点 (`app/api/v1/endpoints/sso.py`)
- [x] 修改依赖注入 (`app/api/v1/deps.py`)
- [ ] 编写单元测试和集成测试
- **交付物**: SSO服务实现（缺少缓存服务和Token刷新/登出端点）

### 10.3 阶段3: 数据库迁移（1天）🔶 部分完成
- [x] 添加user_id字段（nullable）
- [ ] 添加last_login_at字段（未实现，使用updated_at代替）
- [ ] 创建user_info_cache表（可选，未实现）
- [ ] 迁移现有用户数据
- [ ] 编写回滚脚本
- **交付物**: User模型已更新，保留V1字段兼容

### 10.4 阶段4: 前端SSO功能开发（2-3天）✅ 已完成
- [x] 创建SSOLogin组件 (`src/pages/SSOLogin.tsx`)
- [x] 修改API客户端（添加SSO接口 `ssoApi`）
- [x] 修改路由配置（添加/sso/login路由）
- [x] 修改用户信息显示
- [x] 更新类型定义 (`src/types.ts`)
- **交付物**: SSOLogin组件、ssoApi客户端

### 10.5a 阶段5a: 门户服务开发 ✅ 已完成
- [x] 创建门户服务 (`portal/main.py`)
- [x] 实现登录页面和应用列表页面
- [x] 实现登录API（调用USAP）
- [x] 实现跳转API（获取Ticket并生成跳转URL）
- **交付物**: `portal/` 目录

### 10.5 阶段5: Redis集成（1-2天）⚠️ 未开始
- [ ] 添加Redis依赖
- [ ] 创建Redis客户端 (`app/core/redis.py`)
- [ ] 实现用户信息缓存和Token黑名单
- [ ] 性能测试
- **交付物**: Redis客户端实现、缓存服务、性能测试报告

### 10.6 阶段6: 现有功能改造（2-3天）
- [ ] 修改用户管理API（创建用户时仅需user_id，显示时从USAP获取）
- [ ] 修改审计日志（记录user_id，显示时从USAP获取用户名）
- [ ] 修改权限检查（基于user_id）
- [ ] 修改前端用户显示（列表页面批量获取、详情页面单独获取）
- **交付物**: 修改后的用户管理、审计日志、权限检查功能

### 10.7 阶段7: K8s部署配置（1-2天）
- [ ] 创建ConfigMap、Secret配置
- [ ] 创建Frontend/Backend Deployment
- [ ] 创建Redis StatefulSet
- [ ] 创建Service和Ingress配置
- [ ] 编写部署脚本和测试脚本
- **交付物**: K8s配置文件、部署脚本、部署文档

### 10.8 阶段8: 测试和验证（2-3天）
- [ ] 单元测试（覆盖率 > 80%）
- [ ] 集成测试、E2E测试
- [ ] 性能测试、安全测试
- [ ] 兼容性测试、压力测试
- **交付物**: 测试报告、性能测试报告、安全测试报告

### 10.9 阶段9: 文档和培训（1-2天）
- [ ] 编写用户手册、运维手册
- [ ] 编写API文档、故障排查指南
- [ ] 录制演示视频、组织培训会议
- **交付物**: 用户手册、运维手册、API文档

---

## 十一、测试计划

### 11.1 单元测试

#### USAP客户端测试
```python
# tests/clients/test_usap_client.py
class TestUSAPClient:
    async def test_validate_ticket_success(self): ...
    async def test_validate_ticket_expired(self): ...
    async def test_validate_ticket_invalid(self): ...
    async def test_get_user_info_success(self): ...
    async def test_get_user_info_not_found(self): ...
    async def test_get_users_batch(self): ...
```

#### SSO服务测试
```python
# tests/services/test_sso_service.py
class TestSSOService:
    async def test_login_with_ticket_success(self): ...
    async def test_login_with_ticket_invalid(self): ...
    async def test_sync_user_from_usap_new_user(self): ...
    async def test_sync_user_from_usap_existing_user(self): ...
    async def test_create_access_token(self): ...
    async def test_refresh_token(self): ...
```

#### 用户缓存服务测试
```python
# tests/services/test_user_cache_service.py
class TestUserCacheService:
    async def test_get_user_info_cache_hit(self): ...
    async def test_get_user_info_cache_miss(self): ...
    async def test_set_user_info(self): ...
    async def test_cache_expiration(self): ...
```

### 11.2 集成测试

```python
# tests/integration/test_sso_flow.py
class TestSSOFlow:
    async def test_complete_sso_login_flow(self): ...
    async def test_token_refresh_flow(self): ...
    async def test_logout_flow(self): ...

class TestUserInfoFlow:
    async def test_get_user_info_with_cache(self): ...
    async def test_get_user_info_without_cache(self): ...
    async def test_batch_get_users(self): ...
```

### 11.3 E2E测试

```typescript
// e2e/sso-login.spec.ts
describe('SSO Login', () => {
  it('should login successfully with valid ticket', () => { ... });
  it('should redirect to portal when ticket is invalid', () => { ... });
  it('should refresh token automatically', () => { ... });
});
```

### 11.4 性能测试

| 场景 | 并发数 | 持续时间 | 目标TPS | 目标响应时间 |
|------|--------|---------|---------|-------------|
| SSO登录 | 100 | 5分钟 | 100 | < 1秒 |
| Token刷新 | 500 | 5分钟 | 500 | < 200ms |
| 获取用户信息 | 1000 | 5分钟 | 1000 | < 100ms |
| 批量获取用户 | 200 | 5分钟 | 200 | < 1秒 |

**性能指标**:
- 响应时间P95 < 目标响应时间
- 响应时间P99 < 目标响应时间 * 2
- 错误率 < 0.1%
- CPU使用率 < 70%
- 内存使用率 < 80%

### 11.5 安全测试

- [ ] Ticket重放攻击测试
- [ ] Ticket篡改测试
- [ ] JWT Token篡改测试
- [ ] SQL注入测试
- [ ] XSS攻击测试
- [ ] CSRF攻击测试
- [ ] 暴力破解测试
- [ ] 权限绕过测试

---

## 十二、风险评估与上线计划

### 12.1 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| USAP接口不稳定 | 高 | 中 | 实现降级策略，使用缓存 |
| 性能不达标 | 中 | 低 | 充分的性能测试和优化 |
| 数据迁移失败 | 高 | 低 | 充分测试，准备回滚方案 |
| Redis故障 | 中 | 低 | 实现降级策略，直接调用USAP |
| Token泄露 | 高 | 低 | 短期有效，黑名单机制 |

### 12.2 业务风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 用户体验下降 | 中 | 中 | 充分的用户测试和培训 |
| 现有功能受影响 | 高 | 低 | 充分的回归测试 |
| 迁移周期过长 | 中 | 中 | 渐进式迁移，分阶段上线 |
| 用户抵触 | 低 | 中 | 提前沟通，做好培训 |

### 12.3 运维风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 部署失败 | 高 | 低 | 充分测试，准备回滚方案 |
| 监控不完善 | 中 | 中 | 完善监控指标和告警 |
| 故障排查困难 | 中 | 中 | 完善日志和文档 |
| 依赖服务故障 | 高 | 低 | 实现降级策略 |

### 12.4 上线前准备

#### 环境准备
- [ ] 生产环境K8s集群就绪
- [ ] MySQL数据库就绪
- [ ] Redis集群就绪
- [ ] USAP系统对接完成
- [ ] 门户系统对接完成
- [ ] 域名和证书配置完成

#### 数据准备
- [ ] 数据库迁移脚本准备
- [ ] 测试数据准备
- [ ] 用户数据映射表准备
- [ ] 备份策略确认

#### 监控准备
- [ ] 监控指标配置
- [ ] 告警规则配置
- [ ] 日志收集配置
- [ ] 仪表盘配置

### 12.5 灰度发布计划

**第1周 - 灰度发布**:
1. 部署V2版本到灰度环境
2. 选择10%用户进行灰度
3. 监控关键指标
4. 验证SSO登录、用户信息显示、权限控制、业务功能

**第2周 - 扩大灰度**:
1. 扩大到50%用户
2. 持续监控和优化
3. 收集反馈并修复问题

**第3周 - 全量发布**:
1. 全量切换到V2
2. 关闭V1登录入口
3. 执行数据清理

### 12.6 回滚方案

**回滚触发条件**:
- 错误率 > 5%
- 响应时间 > 目标值 * 3
- 核心功能不可用
- 用户投诉 > 10次/小时

**回滚步骤**:
1. 停止V2流量
2. 切换到V1版本
3. 回滚数据库（如果需要）
4. 验证V1功能正常
5. 通知用户

---

## 十三、运维手册

### 13.1 健康检查
```bash
# 检查Pod状态
kubectl get pods -n llmsafe

# 检查服务状态
kubectl get svc -n llmsafe

# 检查Ingress状态
kubectl get ingress -n llmsafe

# 检查日志
kubectl logs -f deployment/llmsafe-backend -n llmsafe
```

### 13.2 缓存管理（⚠️ Redis待实现后可用）
```bash
# 清理过期缓存
redis-cli -h redis-svc -p 6379 FLUSHDB

# 查看缓存命中率
redis-cli -h redis-svc -p 6379 INFO stats
```

### 13.3 数据库维护
```sql
-- 查看用户统计
SELECT role, COUNT(*) FROM users GROUP BY role;

-- 查看最近登录（使用updated_at，因为last_login_at字段不存在）
SELECT user_id, updated_at FROM users ORDER BY updated_at DESC LIMIT 10;
```

### 13.4 故障排查

#### SSO登录失败
**症状**: 用户无法登录，返回401错误

**排查步骤**:
1. 检查Ticket是否有效
   ```bash
   kubectl logs deployment/llmsafe-backend -n llmsafe | grep "Ticket"
   ```
2. 检查USAP服务是否可用
   ```bash
   curl https://usap.company.com/api/health
   ```
3. 检查网络连接
   ```bash
   kubectl exec -it deployment/llmsafe-backend -n llmsafe -- curl https://usap.company.com/api/health
   ```
4. 检查配置
   ```bash
   kubectl get configmap llmsafe-config -n llmsafe -o yaml
   kubectl get secret llmsafe-secrets -n llmsafe -o yaml
   ```

#### 用户信息显示异常
**症状**: 用户信息显示为UserID而非用户名

**排查步骤**:
1. 检查缓存: `redis-cli -h redis-svc -p 6379 GET "user_info:U001"`
2. 检查USAP接口: `curl https://usap.company.com/api/users/U001 -H "X-Client-ID: llm-guard-manager" -H "X-Client-Secret: xxx"`
3. 检查后端日志: `kubectl logs deployment/llmsafe-backend -n llmsafe | grep "user_info"`

#### 性能问题
**症状**: 响应时间过长

**排查步骤**:
1. 检查缓存命中率: `redis-cli -h redis-svc -p 6379 INFO stats | grep hit_rate`
2. 检查USAP响应时间: `kubectl logs deployment/llmsafe-backend -n llmsafe | grep "usap_api_time"`
3. 检查数据库性能: `SHOW PROCESSLIST; SHOW STATUS LIKE 'Slow_queries';`
4. 检查Pod资源使用: `kubectl top pods -n llmsafe`

---

**文档版本**: V2.1
**最后更新**: 2026-02-09
**文档状态**: 已审校（与代码对齐）
**审阅状态**: 已审阅

**相关文档**:
- [V2_SYSTEM_ARCHITECTURE.md](./V2_SYSTEM_ARCHITECTURE.md) - 系统架构设计
- [V2_AUTHENTICATION_FLOW.md](./V2_AUTHENTICATION_FLOW.md) - 认证流程设计
- [V2_DEPLOYMENT_ARCHITECTURE.md](./V2_DEPLOYMENT_ARCHITECTURE.md) - 部署架构设计
- [V2_MOCK_USAP_DESIGN.md](./V2_MOCK_USAP_DESIGN.md) - Mock USAP服务设计
- [RBAC_REQUIREMENTS.md](./RBAC_REQUIREMENTS.md) - RBAC权限模型详细设计
