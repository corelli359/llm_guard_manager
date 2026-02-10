# 角色权限管理系统（RBAC）技术文档

## 文档版本
- **版本**: v3.0
- **日期**: 2026-02-09
- **状态**: 已实现（基于代码审计更新）

---

## 一、系统概述

### 1.1 双 RBAC 系统架构

本系统存在 **两套并行的 RBAC 实现**，分别称为 V1（旧版）和 V2（标准版）。两套系统目前同时运行，权限检查时 **任一系统通过即放行**。

| 维度 | V1（旧版/Legacy） | V2（标准 RBAC） |
|------|-------------------|-----------------|
| 角色存储 | `users.role` 字段（字符串） | `roles` 表 + `user_scenario_roles` 关联表 |
| 权限模型 | 5 个布尔字段（硬编码在 `scenario_admin_permissions` 表） | `permissions` 表 + `role_permissions` 关联表（14 个预置权限） |
| 场景分配 | `user_scenario_assignments` 表 | `user_scenario_roles` 表（scenario_id 可为 NULL 表示全局） |
| 权限检查 | `PermissionService`（`app/services/permission.py`） | `UserScenarioRoleRepository.get_user_permission_codes()`（`app/repositories/role.py`） |
| 权限格式 | `{role, scenarios: [{scenario_id, permissions: {bool fields}}]}` | `{user_id, global_permissions: [codes], scenario_permissions: {id: [codes]}}` |
| 前端使用 | 未使用（V1 格式的 `/permissions/me` 端点存在但前端不调用） | 前端 `PermissionContext` 调用 `/users/me/permissions` |

### 1.2 当前状态

- **前端**：使用 V2 权限系统（`PermissionContext.tsx` 调用 `GET /api/v1/users/me/permissions`）
- **后端 API 保护**：混合使用两套系统
  - `require_role()` 依赖（`deps.py`）：读取 `users.role` 字段（V1）
  - `permission_helpers.py`：同时检查 V1 和 V2，任一通过即放行
  - `roles.py` 端点中的 `_check_admin()`：读取 `users.role` 字段（V1）
- **初始化脚本** `init_rbac.py`：负责创建 V2 表并从 V1 数据迁移到 V2

### 1.3 迁移方向

V1 是旧版系统，V2 是目标系统。`init_rbac.py` 包含从 V1 到 V2 的数据迁移逻辑：
- 将 `users.role` 映射到 `user_scenario_roles`（全局角色，scenario_id=NULL）
- 将 `user_scenario_assignments` 映射到 `user_scenario_roles`（场景角色）

---

## 二、V1 旧版 RBAC 系统

### 2.1 数据模型

V1 使用三张表实现权限控制：

**users 表**（角色字段）：
```
users.role: VARCHAR(32)  -- 值: SYSTEM_ADMIN, SCENARIO_ADMIN, ANNOTATOR, AUDITOR
```
代码位置：`backend/app/models/db_meta.py` -> `User` 类

**user_scenario_assignments 表**（场景分配）：
```sql
-- 将用户分配到特定场景，指定场景内角色
user_scenario_assignments (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),          -- 关联 users.id
    scenario_id VARCHAR(64),    -- 关联 scenarios.app_id
    role VARCHAR(32),           -- SCENARIO_ADMIN 或 ANNOTATOR
    created_at DATETIME,
    created_by VARCHAR(36)
)
```
代码位置：`backend/app/models/db_meta.py` -> `UserScenarioAssignment` 类

**scenario_admin_permissions 表**（细粒度权限）：
```sql
-- 场景管理员在特定场景的 5 个布尔权限
scenario_admin_permissions (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),
    scenario_id VARCHAR(64),
    scenario_basic_info BOOLEAN DEFAULT TRUE,   -- 场景基本信息管理
    scenario_keywords BOOLEAN DEFAULT TRUE,     -- 场景敏感词管理
    scenario_policies BOOLEAN DEFAULT FALSE,    -- 场景规则管理
    playground BOOLEAN DEFAULT TRUE,            -- 输入试验场
    performance_test BOOLEAN DEFAULT FALSE,     -- 性能测试
    created_at DATETIME,
    updated_at DATETIME,
    created_by VARCHAR(36)
)
```
代码位置：`backend/app/models/db_meta.py` -> `ScenarioAdminPermission` 类

### 2.2 V1 权限检查逻辑

核心实现在 `backend/app/services/permission.py` -> `PermissionService` 类：

1. **角色检查** (`check_role`)：直接读取 `user.role` 字段
2. **场景访问检查** (`check_scenario_access`)：
   - SYSTEM_ADMIN / AUDITOR -> 所有场景
   - 其他角色 -> 查询 `user_scenario_assignments` 表
3. **场景权限检查** (`check_scenario_permission`)：
   - SYSTEM_ADMIN -> 全部通过
   - AUDITOR / ANNOTATOR -> 全部拒绝
   - SCENARIO_ADMIN -> 查询 `scenario_admin_permissions` 表的对应布尔字段
4. **获取用户权限** (`get_user_permissions`)：返回格式：
```json
{
  "role": "SCENARIO_ADMIN",
  "scenarios": [
    {
      "scenario_id": "app001",
      "scenario_name": "客服场景",
      "role": "SCENARIO_ADMIN",
      "permissions": {
        "scenario_basic_info": true,
        "scenario_keywords": true,
        "scenario_policies": false,
        "playground": true,
        "performance_test": false
      }
    }
  ]
}
```

### 2.3 V1 相关代码文件

| 文件 | 说明 |
|------|------|
| `backend/app/models/db_meta.py` | `UserScenarioAssignment`, `ScenarioAdminPermission` 模型 |
| `backend/app/services/permission.py` | `PermissionService` 权限检查服务 |
| `backend/app/repositories/user_scenario_assignment.py` | 场景分配数据访问 |
| `backend/app/repositories/scenario_admin_permission.py` | 细粒度权限数据访问 |
| `backend/app/schemas/permission.py` | V1 格式的权限响应 Schema |
| `backend/app/schemas/user_scenario_assignment.py` | 场景分配 Schema |
| `backend/app/schemas/scenario_admin_permission.py` | 细粒度权限 Schema |
| `backend/app/api/v1/endpoints/permissions.py` | V1 权限查询 API（`/permissions/me`, `/permissions/check`） |
| `backend/app/api/v1/deps.py` | `require_role()` 和 `require_scenario_permission()` 依赖 |

---

## 三、V2 标准 RBAC 系统

### 3.1 数据模型

V2 使用标准的 RBAC 多表关联模型：

**roles 表**（角色定义）：
```sql
roles (
    id CHAR(36) PRIMARY KEY,
    role_code VARCHAR(64) UNIQUE,    -- 角色编码，如 SYSTEM_ADMIN
    role_name VARCHAR(128),          -- 角色名称，如 系统管理员
    role_type VARCHAR(16),           -- GLOBAL（全局角色）或 SCENARIO（场景角色）
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE, -- 系统预置角色不可删除
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    updated_at DATETIME
)
```

**permissions 表**（权限定义）：
```sql
permissions (
    id CHAR(36) PRIMARY KEY,
    permission_code VARCHAR(64) UNIQUE,  -- 权限编码，如 smart_labeling
    permission_name VARCHAR(128),        -- 权限名称，如 智能标注
    permission_type VARCHAR(16),         -- MENU（菜单权限）或 ACTION（操作权限）
    scope VARCHAR(16),                   -- GLOBAL（全局）或 SCENARIO（场景级）
    parent_code VARCHAR(64),             -- 父权限编码（预留，当前未使用）
    sort_order INT DEFAULT 0,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
)
```

**role_permissions 表**（角色-权限关联）：
```sql
role_permissions (
    id CHAR(36) PRIMARY KEY,
    role_id CHAR(36),        -- 关联 roles.id
    permission_id CHAR(36),  -- 关联 permissions.id
    created_at DATETIME,
    UNIQUE KEY (role_id, permission_id)
)
```

**user_scenario_roles 表**（用户-场景-角色关联）：
```sql
user_scenario_roles (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),           -- 关联 users.id
    scenario_id VARCHAR(64),    -- 关联 scenarios.app_id，NULL 表示全局角色
    role_id CHAR(36),           -- 关联 roles.id
    created_at DATETIME,
    created_by VARCHAR(36),
    UNIQUE KEY (user_id, scenario_id, role_id)
)
```

代码位置：`backend/app/models/db_meta.py` -> `Role`, `Permission`, `RolePermission`, `UserScenarioRole` 类

### 3.2 预置权限（14 个）

由 `backend/init_rbac.py` 初始化，分为全局权限和场景权限两类：

**全局权限（GLOBAL scope）- 9 个：**

| 编码 | 名称 | 类型 | 排序 |
|------|------|------|------|
| `smart_labeling` | 智能标注 | MENU | 1 |
| `annotator_stats` | 标注统计 | MENU | 2 |
| `user_management` | 用户管理 | MENU | 10 |
| `role_management` | 角色管理 | MENU | 11 |
| `audit_logs` | 审计日志 | MENU | 12 |
| `app_management` | 应用管理 | MENU | 20 |
| `tag_management` | 标签管理 | MENU | 21 |
| `global_keywords` | 全局敏感词 | MENU | 22 |
| `global_policies` | 全局默认规则 | MENU | 23 |

**场景权限（SCENARIO scope）- 5 个：**

| 编码 | 名称 | 类型 | 排序 |
|------|------|------|------|
| `scenario_basic_info` | 场景基本信息 | ACTION | 30 |
| `scenario_keywords` | 场景敏感词 | MENU | 31 |
| `scenario_policies` | 场景策略管理 | MENU | 32 |
| `playground` | 输入试验场 | MENU | 40 |
| `performance_test` | 性能测试 | MENU | 41 |

### 3.3 预置角色（4 个）及权限分配

由 `backend/init_rbac.py` 初始化：

**SYSTEM_ADMIN（系统管理员）**
- 类型：GLOBAL
- 权限：`*`（所有 14 个权限）
- 说明：拥有所有权限，系统预置不可删除

**AUDITOR（审计员）**
- 类型：GLOBAL
- 权限：`smart_labeling`, `annotator_stats`, `audit_logs`（3 个）
- 说明：只读审计权限

**SCENARIO_ADMIN（场景管理员）**
- 类型：SCENARIO
- 权限：`smart_labeling`, `scenario_basic_info`, `scenario_keywords`, `scenario_policies`, `playground`, `performance_test`（6 个）
- 说明：管理分配的场景，需要通过 `user_scenario_roles` 绑定到具体场景

**ANNOTATOR（标注员）**
- 类型：SCENARIO
- 权限：`smart_labeling`（1 个）
- 说明：仅标注任务，需要通过 `user_scenario_roles` 绑定到具体场景

### 3.4 V2 权限检查逻辑

核心实现在 `backend/app/repositories/role.py` -> `UserScenarioRoleRepository.get_user_permission_codes()` 方法：

1. 查询 `user_scenario_roles` 获取用户所有角色分配
2. 对每个分配，通过 `role_permissions` + `permissions` 获取权限编码
3. 如果 `scenario_id` 为 NULL（全局角色），权限加入 `global_permissions`
4. 如果 `scenario_id` 有值（场景角色），权限加入 `scenario_permissions[scenario_id]`
5. 返回格式：
```json
{
  "user_id": "user123",
  "global_permissions": ["smart_labeling", "annotator_stats", "user_management", ...],
  "scenario_permissions": {
    "app001": ["smart_labeling", "scenario_keywords", "playground", ...],
    "app002": ["smart_labeling"]
  }
}
```

### 3.5 V2 相关代码文件

| 文件 | 说明 |
|------|------|
| `backend/app/models/db_meta.py` | `Role`, `Permission`, `RolePermission`, `UserScenarioRole` 模型 |
| `backend/app/repositories/role.py` | `RoleRepository`, `PermissionRepository`, `UserScenarioRoleRepository` |
| `backend/app/schemas/role.py` | V2 角色/权限/用户权限 Schema |
| `backend/app/api/v1/endpoints/roles.py` | 角色管理 CRUD + 权限配置 API |
| `backend/app/api/v1/endpoints/users.py` | 用户管理 + V2 角色分配 + 权限查询 API |
| `backend/init_rbac.py` | V2 表创建 + 预置数据 + V1->V2 迁移 |

---

## 四、权限检查融合层

### 4.1 permission_helpers.py

文件 `backend/app/api/v1/permission_helpers.py` 是 V1 和 V2 的融合层，提供两个核心函数：

**`check_scenario_access_or_403(user, scenario_id, db, permission=None)`**

检查顺序：
1. 如果 `user.role == "SYSTEM_ADMIN"` -> 直接放行（V1 字段）
2. V2 检查：调用 `_check_v2_permission()` -> 通过则放行
3. V1 检查：调用 `PermissionService` -> 通过则放行
4. 都不通过 -> 抛出 HTTP 403

**`get_user_scenario_ids_or_all(user, db)`**

获取用户可访问的场景列表：
1. 如果 `user.role` 是 SYSTEM_ADMIN 或 AUDITOR -> 返回 None（表示所有场景）
2. V2 检查：如果全局权限包含 `app_management` 或 `audit_logs` -> 返回 None
3. 合并 V1 场景列表（`user_scenario_assignments`）和 V2 场景列表（`user_scenario_roles`）

### 4.2 deps.py 中的权限依赖

文件 `backend/app/api/v1/deps.py` 提供 FastAPI 依赖注入：

**`require_role(allowed_roles)`**：
- 读取 `user.role` 字段（V1）
- 用于保护需要特定角色的端点
- 示例：`Depends(require_role(["SYSTEM_ADMIN"]))`

**`require_scenario_permission(permission)`**：
- 使用 V1 的 `PermissionService` 检查
- SYSTEM_ADMIN 直接放行
- 其他角色检查 `scenario_admin_permissions` 表

---

## 五、API 端点（实际实现）

### 5.1 路由注册

所有路由在 `backend/app/api/v1/api.py` 中注册，基础路径为 `/api/v1`：

```python
/login          -> auth.router          # 登录认证
/sso            -> sso.router           # SSO 单点登录
/users          -> users.router         # 用户管理 + V2 角色分配
/roles          -> roles.router         # V2 角色管理
/permissions    -> permissions.router   # V1 权限查询
/audit-logs     -> audit_logs.router    # 审计日志
/staging        -> staging.router       # 智能标注暂存
/tags           -> meta_tags.router     # 元数据标签
/keywords/global    -> global_keywords.router    # 全局敏感词
/keywords/scenario  -> scenario_keywords.router  # 场景敏感词
/policies       -> rule_policy.router   # 规则策略
/apps           -> scenarios.router     # 场景/应用管理
/playground     -> playground.router    # 输入试验场
/performance    -> performance.router   # 性能测试
```

### 5.2 用户管理 API（`/api/v1/users`）

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/users/` | 获取用户列表 | SYSTEM_ADMIN（V1 role 字段） |
| PUT | `/users/{user_id}/role` | 修改用户角色（V1 role 字段） | SYSTEM_ADMIN |
| PATCH | `/users/{user_id}/status` | 启用/禁用用户 | SYSTEM_ADMIN |
| DELETE | `/users/{user_id}` | 删除用户 | SYSTEM_ADMIN |
| GET | `/users/{user_id}/roles` | 获取用户 V2 角色分配列表 | SYSTEM_ADMIN 或本人 |
| POST | `/users/{user_id}/roles` | 分配 V2 角色给用户 | SYSTEM_ADMIN |
| DELETE | `/users/{user_id}/roles/{assignment_id}` | 移除 V2 角色分配 | SYSTEM_ADMIN |
| GET | `/users/me/permissions` | 获取当前用户 V2 权限 | 已登录用户 |

注意：`/users/me/permissions` 是前端实际调用的权限查询端点，返回 V2 格式。

### 5.3 角色管理 API（`/api/v1/roles`）

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/roles/` | 获取角色列表 | 已登录用户 |
| POST | `/roles/` | 创建角色 | SYSTEM_ADMIN |
| PUT | `/roles/{role_id}` | 更新角色 | SYSTEM_ADMIN |
| DELETE | `/roles/{role_id}` | 删除角色（系统角色不可删） | SYSTEM_ADMIN |
| GET | `/roles/{role_id}/permissions` | 获取角色权限列表 | 已登录用户 |
| PUT | `/roles/{role_id}/permissions` | 更新角色权限 | SYSTEM_ADMIN |
| GET | `/roles/permissions/all` | 获取所有权限列表 | 已登录用户 |

### 5.4 V1 权限查询 API（`/api/v1/permissions`）

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/permissions/me` | 获取当前用户 V1 格式权限 | 已登录用户 |
| POST | `/permissions/check` | 检查特定场景权限 | 已登录用户 |

注意：前端不调用这些端点，它们是 V1 遗留接口。

### 5.5 审计日志 API（`/api/v1/audit-logs`）

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/audit-logs/` | 查询审计日志（支持多条件过滤） | SYSTEM_ADMIN 或 AUDITOR |
| GET | `/audit-logs/count` | 统计审计日志数量 | SYSTEM_ADMIN 或 AUDITOR |

查询参数：`user_id`, `username`, `action`, `resource_type`, `scenario_id`, `start_date`, `end_date`, `skip`, `limit`

### 5.6 SSO 单点登录 API（`/api/v1/sso`）

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/sso/login` | SSO 登录（USAP Ticket 换 JWT） | 公开 |
| GET | `/sso/user-info` | 获取当前用户信息 | 已登录用户 |
| POST | `/sso/users/batch` | 批量获取用户信息 | 已登录用户 |
| GET | `/sso/health` | SSO 服务健康检查 | 公开 |

---

## 六、前端权限系统

### 6.1 权限上下文（PermissionContext）

文件：`frontend/src/contexts/PermissionContext.tsx`

前端使用 V2 权限系统。登录后调用 `GET /api/v1/users/me/permissions` 获取权限数据，存储在 React Context 中。

**期望的数据格式**（`UserPermissionsV2` 类型，定义在 `frontend/src/types.ts`）：
```typescript
interface UserPermissionsV2 {
  user_id: string;
  global_permissions: string[];           // 全局权限编码列表
  scenario_permissions: Record<string, string[]>;  // {场景ID: 权限编码列表}
}
```

**后端实际返回格式**（`GET /api/v1/users/me/permissions`，由 `UserScenarioRoleRepository.get_user_permission_codes()` 生成）：
```json
{
  "user_id": "user123",
  "global_permissions": ["smart_labeling", "user_management", "role_management", ...],
  "scenario_permissions": {
    "app001": ["smart_labeling", "scenario_keywords", "playground"]
  }
}
```

前端和后端的 V2 格式是一致的，不存在格式不匹配问题。

注意：V1 的 `/permissions/me` 端点返回的是不同格式（`{role, scenarios: [...]}`），但前端不调用该端点。

### 6.2 权限检查方法

`PermissionContext` 提供以下方法：

**`hasPermission(permissionCode)`**：检查全局权限
```typescript
// 检查 global_permissions 是否包含指定编码
hasPermission('user_management')  // true for SYSTEM_ADMIN
```

**`hasScenarioPermission(scenarioId, permissionCode)`**：检查场景权限
```typescript
// 先检查全局权限，再检查场景权限
hasScenarioPermission('app001', 'scenario_keywords')
```

**`hasRole(roles)`**：基于权限推断角色（注意：不是直接读取角色字段）
```typescript
// 通过权限组合推断角色：
// SYSTEM_ADMIN: 拥有 user_management 权限
// SCENARIO_ADMIN: 有场景级权限分配
// AUDITOR: 拥有 audit_logs 但没有 user_management
// ANNOTATOR: 拥有 smart_labeling
hasRole(['SYSTEM_ADMIN'])
```

**`hasScenarioAccess(scenarioId)`**：检查场景访问权
```typescript
// 拥有 app_management 全局权限 -> 所有场景
// 否则检查 scenario_permissions 中是否有该场景
hasScenarioAccess('app001')
```

### 6.3 PermissionGuard 组件

文件：`frontend/src/components/PermissionGuard.tsx`

用于在 JSX 中进行声明式权限控制：
```tsx
<PermissionGuard roles={['SYSTEM_ADMIN']}>
  <AdminPanel />
</PermissionGuard>

<PermissionGuard scenarioId="app001" permission="scenario_keywords">
  <KeywordEditor />
</PermissionGuard>
```

### 6.4 前端 API 调用

文件：`frontend/src/api.ts`

**角色管理 API（`rolesApi`）**：
```typescript
rolesApi.list()                          // GET /roles/
rolesApi.create(data)                    // POST /roles/
rolesApi.update(id, data)               // PUT /roles/{id}
rolesApi.delete(id)                     // DELETE /roles/{id}
rolesApi.getPermissions(id)             // GET /roles/{id}/permissions
rolesApi.updatePermissions(id, ids)     // PUT /roles/{id}/permissions
rolesApi.listAllPermissions()           // GET /roles/permissions/all
```

**用户角色 API（`userRolesApi`）**：
```typescript
userRolesApi.getUserRoles(userId)       // GET /users/{userId}/roles
userRolesApi.assignRole(userId, data)   // POST /users/{userId}/roles
userRolesApi.removeRole(userId, aId)    // DELETE /users/{userId}/roles/{aId}
userRolesApi.getMyPermissions()         // GET /users/me/permissions
```

---

## 七、审计日志系统

### 7.1 数据模型

**audit_logs 表**：
```sql
audit_logs (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),
    username VARCHAR(64),
    action VARCHAR(64),          -- CREATE, UPDATE, DELETE, VIEW, EXPORT
    resource_type VARCHAR(64),   -- USER, SCENARIO, KEYWORD, POLICY, USER_ROLE_ASSIGNMENT, etc.
    resource_id VARCHAR(64),
    scenario_id VARCHAR(64),
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at DATETIME
)
```

### 7.2 审计服务

文件：`backend/app/services/audit.py` -> `AuditService` 类

提供便捷方法：`log_create()`, `log_update()`, `log_delete()`, `log_view()`, `log_export()`

自动提取客户端 IP（支持 X-Forwarded-For、X-Real-IP 代理头）和 User-Agent。

### 7.3 已集成审计日志的操作

当前以下操作会记录审计日志：
- 修改用户角色（`PUT /users/{id}/role`）
- 启用/禁用用户（`PATCH /users/{id}/status`）
- 删除用户（`DELETE /users/{id}`）
- 分配 V2 角色（`POST /users/{id}/roles`）
- 移除 V2 角色（`DELETE /users/{id}/roles/{aid}`）

---

## 八、认证系统

### 8.1 双认证模式

**V1 本地认证**（开发/测试环境）：
- 用户名密码登录：`POST /api/v1/login/access-token`
- 本服务生成 JWT Token（8 天有效期）
- Token 中 `sub` 字段为 `username`

**V2 SSO 认证**（生产环境）：
- 通过 USAP 门户获取 Ticket
- 使用 Ticket 换取本服务 JWT：`POST /api/v1/sso/login`
- Token 中 `sub` 字段为 `user_id`（USAP 的 UserID）

### 8.2 Token 解析

`deps.py` 中的 `get_current_user_full()` 支持两种模式：
- 从 JWT 的 `sub` 字段提取标识符
- 在 `users` 表中同时匹配 `user_id` 和 `username` 字段
- 这样无论是 V1 还是 V2 认证方式生成的 Token 都能正确解析

---

## 九、数据模型完整清单

### 9.1 V1 旧版表

| 表名 | ORM 类 | 说明 | 状态 |
|------|--------|------|------|
| `users` (role 字段) | `User` | 用户角色字段 | 仍在使用（`require_role` 依赖） |
| `user_scenario_assignments` | `UserScenarioAssignment` | V1 场景分配 | 仍在使用（`permission_helpers` 兼容层） |
| `scenario_admin_permissions` | `ScenarioAdminPermission` | V1 细粒度权限 | 仍在使用（`permission_helpers` 兼容层） |

### 9.2 V2 标准表

| 表名 | ORM 类 | 说明 | 状态 |
|------|--------|------|------|
| `roles` | `Role` | 角色定义 | 已使用 |
| `permissions` | `Permission` | 权限定义 | 已使用 |
| `role_permissions` | `RolePermission` | 角色-权限关联 | 已使用 |
| `user_scenario_roles` | `UserScenarioRole` | 用户-场景-角色关联 | 已使用 |

### 9.3 共享表

| 表名 | ORM 类 | 说明 |
|------|--------|------|
| `audit_logs` | `AuditLog` | 审计日志 |
| `users` | `User` | 用户基本信息 |

---

## 十、权限矩阵（基于 V2 预置角色）

### 10.1 全局权限分配

| 权限编码 | SYSTEM_ADMIN | AUDITOR | SCENARIO_ADMIN | ANNOTATOR |
|----------|:---:|:---:|:---:|:---:|
| `smart_labeling` | Y | Y | Y | Y |
| `annotator_stats` | Y | Y | - | - |
| `user_management` | Y | - | - | - |
| `role_management` | Y | - | - | - |
| `audit_logs` | Y | Y | - | - |
| `app_management` | Y | - | - | - |
| `tag_management` | Y | - | - | - |
| `global_keywords` | Y | - | - | - |
| `global_policies` | Y | - | - | - |

### 10.2 场景权限分配

场景权限仅在用户通过 `user_scenario_roles` 绑定到具体场景时生效：

| 权限编码 | SYSTEM_ADMIN | SCENARIO_ADMIN | ANNOTATOR |
|----------|:---:|:---:|:---:|
| `scenario_basic_info` | Y | Y | - |
| `scenario_keywords` | Y | Y | - |
| `scenario_policies` | Y | Y | - |
| `playground` | Y | Y | - |
| `performance_test` | Y | Y | - |

注意：SYSTEM_ADMIN 作为全局角色拥有所有权限（包括场景权限），无需绑定到具体场景。AUDITOR 没有场景级权限。

---

## 十一、初始化与迁移

### 11.1 init_rbac.py 执行流程

文件：`backend/init_rbac.py`

```
[1/5] 创建表 -> roles, permissions, role_permissions, user_scenario_roles
[2/5] 插入预置权限 -> 14 个权限（INSERT IGNORE）
[3/5] 插入预置角色 -> 4 个角色（INSERT IGNORE）
[4/5] 配置角色-权限关联 -> SYSTEM_ADMIN 获得全部 14 个，其他按配置
[5/5] 迁移现有用户角色 ->
      - users.role -> user_scenario_roles (scenario_id=NULL)
      - user_scenario_assignments -> user_scenario_roles (带 scenario_id)
```

### 11.2 运行方式

```bash
cd backend
python init_rbac.py
```

使用 `INSERT IGNORE` 确保幂等性，可重复运行。

---

## 十二、已知问题与待改进项

### 12.1 V1/V2 并存的复杂性

- `require_role()` 依赖仍然读取 V1 的 `users.role` 字段，这意味着即使 V2 角色分配正确，如果 V1 的 `users.role` 字段不匹配，某些端点仍会拒绝访问
- `permission_helpers.py` 的双重检查增加了复杂性和数据库查询次数
- 建议：逐步将所有端点迁移到 V2 权限检查，最终废弃 V1

### 12.2 前端角色推断

前端 `PermissionContext.hasRole()` 通过权限组合推断角色，而非直接获取角色信息。这种方式在自定义角色场景下可能不准确。

### 12.3 缺少权限缓存

当前每次权限检查都查询数据库，没有缓存机制。高并发场景下可能成为性能瓶颈。

---

## 附录

### A. 术语表

| 术语 | 说明 |
|------|------|
| RBAC | Role-Based Access Control，基于角色的访问控制 |
| V1 | 旧版 RBAC，使用 `users.role` 字段 + `user_scenario_assignments` + `scenario_admin_permissions` |
| V2 | 标准 RBAC，使用 `roles` + `permissions` + `role_permissions` + `user_scenario_roles` |
| 场景 | 即应用（Application），业务场景的配置单元，对应 `scenarios` 表 |
| 全局角色 | `user_scenario_roles.scenario_id = NULL` 的角色分配 |
| 场景角色 | `user_scenario_roles.scenario_id` 有值的角色分配 |
| SSO | Single Sign-On，单点登录，通过 USAP 门户实现 |
| USAP | 企业统一认证平台，提供 Ticket 验证和用户信息查询 |

### B. 关键文件索引

**后端 - 模型层**：
- `backend/app/models/db_meta.py` - 所有 ORM 模型

**后端 - V1 RBAC**：
- `backend/app/services/permission.py` - V1 权限检查服务
- `backend/app/repositories/user_scenario_assignment.py` - V1 场景分配
- `backend/app/repositories/scenario_admin_permission.py` - V1 细粒度权限
- `backend/app/schemas/permission.py` - V1 权限 Schema
- `backend/app/api/v1/endpoints/permissions.py` - V1 权限 API

**后端 - V2 RBAC**：
- `backend/app/repositories/role.py` - V2 角色/权限/用户角色 Repository
- `backend/app/schemas/role.py` - V2 角色/权限 Schema
- `backend/app/api/v1/endpoints/roles.py` - V2 角色管理 API
- `backend/app/api/v1/endpoints/users.py` - V2 用户管理 + 角色分配 API
- `backend/init_rbac.py` - V2 初始化脚本

**后端 - 融合层**：
- `backend/app/api/v1/permission_helpers.py` - V1+V2 权限检查融合
- `backend/app/api/v1/deps.py` - 认证和角色依赖

**后端 - 审计**：
- `backend/app/services/audit.py` - 审计日志服务
- `backend/app/repositories/audit_log.py` - 审计日志 Repository
- `backend/app/api/v1/endpoints/audit_logs.py` - 审计日志 API

**后端 - SSO**：
- `backend/app/api/v1/endpoints/sso.py` - SSO 端点
- `backend/app/services/sso_service.py` - SSO 服务
- `backend/app/clients/usap_client.py` - USAP 客户端

**前端**：
- `frontend/src/contexts/PermissionContext.tsx` - 权限上下文
- `frontend/src/components/PermissionGuard.tsx` - 权限守卫组件
- `frontend/src/hooks/usePermission.ts` - 权限 Hook
- `frontend/src/types.ts` - `UserPermissionsV2` 类型定义
- `frontend/src/api.ts` - `rolesApi`, `userRolesApi` API 调用
