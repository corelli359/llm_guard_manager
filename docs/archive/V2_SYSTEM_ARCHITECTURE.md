# LLM Guard Manager V2 系统架构设计

## 版本信息
- **版本**: V2.0
- **设计日期**: 2026-02-06
- **架构类型**: 企业级SSO集成架构

---

## 一、架构概述

### 1.1 V1 vs V2 对比

| 维度 | V1（当前版本） | V2（目标版本） |
|------|---------------|---------------|
| 认证方式 | 独立认证（JWT） | SSO单点登录（Ticket） |
| 用户管理 | 本地用户表（完整信息） | 仅存储UserID（引用USAP） |
| 登录入口 | 直接登录 | 门户系统跳转 |
| 用户信息 | 本地存储 | 实时从USAP获取 |
| 会话管理 | JWT Token | Ticket + Session |
| 适用场景 | 独立部署 | 企业内网集成 |

### 1.2 核心变化
1. **认证中心化**: 所有认证由USAP统一管理
2. **用户信息外部化**: 用户基本信息从USAP实时获取
3. **单点登录**: 一次登录，多系统访问
4. **Ticket机制**: 基于Ticket的安全认证

---

## 二、系统组成

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
- **功能**:
  - 用户身份认证（用户名/密码验证）
  - 用户信息管理（UserID、姓名、部门、邮箱等）
  - Ticket生成与验证
  - 用户权限基础信息
- **接口**:
  - `POST /api/auth/login` - 用户登录
  - `POST /api/auth/validate-ticket` - Ticket验证
  - `GET /api/users/{userId}` - 获取用户信息
  - `GET /api/users/batch` - 批量获取用户信息

#### 2.2.2 门户系统（Portal）
- **职责**: 统一入口和导航
- **功能**:
  - 用户登录界面
  - 系统导航菜单
  - 跳转到各子系统（携带Ticket）
  - 会话管理
- **跳转方式**:
  - URL: `https://portal.company.com/redirect?system=llm-guard&ticket={ticket}`
  - 目标: `https://llm-guard.company.com/sso/login?ticket={ticket}`

#### 2.2.3 安全管理平台（LLM Guard Manager）
- **职责**: LLM安全策略管理
- **功能**:
  - 接收Ticket并验证
  - 基于UserID的权限管理
  - 业务功能（场景管理、敏感词管理、策略配置等）
- **认证流程**:
  1. 接收Portal传递的Ticket
  2. 调用USAP验证Ticket
  3. 获取UserID
  4. 查询本地权限配置
  5. 建立本地会话（JWT）

---

## 三、核心架构设计

### 3.1 认证架构

```
┌─────────┐
│  用户   │
└────┬────┘
     │ 1. 访问门户
     ▼
┌─────────────┐
│  门户系统   │
└────┬────────┘
     │ 2. 输入用户名/密码
     ▼
┌─────────────┐
│  USAP系统   │◄──────────────┐
└────┬────────┘                │
     │ 3. 返回Ticket           │
     ▼                          │
┌─────────────┐                │
│  门户系统   │                │
└────┬────────┘                │
     │ 4. 跳转到安全管理平台    │
     │    (携带Ticket)         │
     ▼                          │
┌──────────────────┐           │
│  安全管理平台    │           │
└────┬─────────────┘           │
     │ 5. 验证Ticket           │
     └─────────────────────────┘
     │ 6. 返回UserID + 用户信息
     ▼
┌──────────────────┐
│  建立本地会话    │
│  (JWT Token)     │
└──────────────────┘
```

### 3.2 数据架构

#### 3.2.1 V1数据模型（当前）
```sql
-- 用户表（完整信息）
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

#### 3.2.2 V2数据模型（目标）
```sql
-- 用户表（仅存储UserID和权限）
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,           -- 本地ID（保留）
    user_id VARCHAR(50) UNIQUE NOT NULL,  -- USAP的UserID（核心）
    role VARCHAR(20) NOT NULL,            -- 本地角色
    is_active BOOLEAN DEFAULT TRUE,       -- 本地激活状态
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_login_at TIMESTAMP,
    INDEX idx_user_id (user_id)
);

-- 用户信息缓存表（可选，用于性能优化）
CREATE TABLE user_info_cache (
    user_id VARCHAR(50) PRIMARY KEY,
    display_name VARCHAR(100),
    email VARCHAR(100),
    department VARCHAR(100),
    cached_at TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_expires_at (expires_at)
);
```

### 3.3 会话架构

#### 3.3.1 双Token机制
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
│  - 有效期: 8小时                         │
│  - 刷新机制: Refresh Token               │
│  - Payload: {user_id, role, scenarios}   │
└─────────────────────────────────────────┘
```

#### 3.3.2 会话生命周期
1. **Ticket阶段** (0-5分钟)
   - 用户从门户跳转，携带Ticket
   - 安全管理平台验证Ticket
   - 一次性使用，验证后失效

2. **JWT阶段** (5分钟-8小时)
   - Ticket验证成功后颁发JWT
   - 所有API调用使用JWT
   - JWT过期前可刷新

3. **刷新阶段** (8小时后)
   - JWT过期，使用Refresh Token刷新
   - 或重新从门户登录

---

## 四、技术架构

### 4.1 技术栈

| 层次 | V1 | V2 | 变化说明 |
|------|----|----|---------|
| 前端 | React + TypeScript | React + TypeScript | 无变化 |
| 后端 | FastAPI | FastAPI | 无变化 |
| 认证 | JWT | Ticket + JWT | 新增Ticket验证 |
| 用户管理 | 本地数据库 | USAP API | 新增外部调用 |
| 会话 | JWT | JWT + Session | 新增Session管理 |
| 缓存 | 无 | Redis（可选） | 新增用户信息缓存 |

### 4.2 新增组件

#### 4.2.1 USAP客户端（Backend）
```python
# app/clients/usap_client.py
class USAPClient:
    """USAP系统客户端"""

    async def validate_ticket(self, ticket: str) -> TicketValidationResult:
        """验证Ticket并获取UserID"""

    async def get_user_info(self, user_id: str) -> UserInfo:
        """获取用户基本信息"""

    async def get_users_batch(self, user_ids: List[str]) -> List[UserInfo]:
        """批量获取用户信息"""
```

#### 4.2.2 SSO认证服务（Backend）
```python
# app/services/sso_service.py
class SSOService:
    """SSO单点登录服务"""

    async def login_with_ticket(self, ticket: str) -> LoginResult:
        """使用Ticket登录"""

    async def sync_user_from_usap(self, user_id: str) -> User:
        """从USAP同步用户信息"""
```

#### 4.2.3 用户信息缓存（Backend）
```python
# app/services/user_cache_service.py
class UserCacheService:
    """用户信息缓存服务"""

    async def get_user_info(self, user_id: str) -> UserInfo:
        """获取用户信息（优先从缓存）"""

    async def refresh_cache(self, user_id: str) -> None:
        """刷新缓存"""
```

### 4.3 API变化

#### 4.3.1 新增API
```
POST /api/v1/sso/login          # SSO登录（Ticket验证）
POST /api/v1/sso/logout         # SSO登出
GET  /api/v1/sso/user-info      # 获取当前用户完整信息
POST /api/v1/sso/refresh        # 刷新Token
```

#### 4.3.2 修改API
```
# 所有需要用户信息的API，从返回完整信息改为返回UserID
# 前端需要显示用户名时，调用 /api/v1/sso/user-info 或批量接口
```

---

## 五、安全设计

### 5.1 Ticket安全
- **一次性使用**: Ticket验证后立即失效
- **短期有效**: 5分钟有效期
- **签名验证**: USAP使用数字签名
- **HTTPS传输**: 所有通信使用HTTPS

### 5.2 JWT安全
- **签名算法**: HS256
- **Payload最小化**: 仅包含user_id、role、scenarios
- **定期刷新**: 8小时过期，需刷新
- **黑名单机制**: 登出时加入黑名单

### 5.3 API安全
- **双重验证**: Ticket验证 + JWT验证
- **权限检查**: 基于UserID的权限验证
- **审计日志**: 记录所有认证和授权操作

---

## 六、性能设计

### 6.1 缓存策略
```
┌─────────────────────────────────────────┐
│  用户信息缓存（Redis/内存）              │
│  - Key: user_id                          │
│  - Value: {display_name, email, dept}    │
│  - TTL: 1小时                            │
│  - 更新策略: 被动更新 + 定期刷新         │
└─────────────────────────────────────────┘
```

### 6.2 批量查询优化
- 前端列表页面批量获取用户信息
- 后端提供批量查询接口
- 使用DataLoader模式避免N+1查询

### 6.3 降级策略
- USAP不可用时，使用缓存的用户信息
- 缓存过期时，显示UserID而非用户名
- 关键业务功能不依赖用户显示名

---

## 七、兼容性设计

### 7.1 渐进式迁移
```
阶段1: 双模式支持（V1 + V2）
  - 保留原有登录方式
  - 新增SSO登录入口
  - 数据库同时支持两种模式

阶段2: V2为主，V1为备
  - SSO为主要登录方式
  - 保留本地登录作为应急方案

阶段3: 完全V2
  - 移除本地登录
  - 完全依赖USAP
```

### 7.2 数据迁移
```sql
-- 迁移脚本：将现有用户映射到USAP UserID
UPDATE users
SET user_id = username  -- 假设username就是USAP的UserID
WHERE user_id IS NULL;

-- 清理敏感数据
UPDATE users
SET hashed_password = NULL,
    email = NULL,
    display_name = NULL;
```

---

## 八、监控与运维

### 8.1 监控指标
- **Ticket验证成功率**: 目标 > 99%
- **USAP API响应时间**: 目标 < 200ms
- **用户信息缓存命中率**: 目标 > 90%
- **SSO登录成功率**: 目标 > 99%

### 8.2 告警规则
- USAP API连续失败 > 5次
- Ticket验证失败率 > 5%
- 用户信息缓存命中率 < 80%
- SSO登录失败率 > 10%

---

## 九、部署架构（概述）

详见 `V2_DEPLOYMENT_ARCHITECTURE.md`

### 9.1 部署拓扑
```
┌─────────────────────────────────────────────────────────┐
│  Kubernetes Cluster                                      │
│                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Frontend   │  │  Backend    │  │  Redis      │     │
│  │  (Nginx)    │  │  (FastAPI)  │  │  (Cache)    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                           │
└─────────────────────────────────────────────────────────┘
         │                    │
         │                    │ HTTPS
         ▼                    ▼
┌─────────────┐      ┌─────────────┐
│  门户系统   │      │  USAP系统   │
└─────────────┘      └─────────────┘
```

---

## 十、总结

### 10.1 核心优势
1. ✅ **统一认证**: 企业级SSO，一次登录多系统访问
2. ✅ **安全增强**: Ticket + JWT双重验证
3. ✅ **数据分离**: 用户信息集中管理，避免数据冗余
4. ✅ **易于集成**: 标准SSO流程，易于接入企业生态

### 10.2 技术挑战
1. ⚠️ **外部依赖**: 依赖USAP系统可用性
2. ⚠️ **性能优化**: 需要缓存策略避免频繁调用USAP
3. ⚠️ **数据迁移**: 现有用户数据需要迁移
4. ⚠️ **兼容性**: 需要支持渐进式迁移

### 10.3 实施建议
1. 先实现USAP Mock服务，用于开发和测试
2. 采用渐进式迁移策略，降低风险
3. 完善监控和降级方案，确保系统稳定性
4. 充分测试Ticket验证流程和边界情况

---

**下一步**: 请查看以下文档
- `V2_AUTHENTICATION_FLOW.md` - 认证流程详细设计
- `V2_DEPLOYMENT_ARCHITECTURE.md` - 部署架构详细设计
- `V2_REQUIREMENTS.md` - 完整需求文档
