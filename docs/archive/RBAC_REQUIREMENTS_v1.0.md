# 角色权限管理系统（RBAC）需求设计文档

## 文档版本
- **版本**: v1.0
- **日期**: 2026-02-05
- **状态**: 需求设计阶段

---

## 一、需求概述

### 1.1 背景
当前系统只有简单的角色区分（ADMIN, AUDITOR），无法满足多租户、细粒度权限控制的需求。需要建立完整的 RBAC（基于角色的访问控制）系统，支持：
- 多种角色定义
- 细粒度权限控制
- 场景（应用）级别的权限隔离
- 灵活的权限配置

### 1.2 目标
1. 实现基于角色的权限管理
2. 支持场景级别的权限隔离
3. 提供灵活的权限配置能力
4. 确保数据安全和操作审计

---

## 二、角色定义

### 2.1 系统管理员（SYSTEM_ADMIN）

**职责**：系统的最高管理者，负责全局配置和用户管理

**权限范围**：
- ✅ 所有功能的完全访问权限
- ✅ 用户管理（创建、编辑、删除、分配角色）
- ✅ 场景管理（所有场景）
- ✅ 全局配置（标签、全局敏感词、全局规则）
- ✅ 为场景管理员分配场景和配置权限
- ✅ 查看所有审计日志和统计数据
- ✅ 系统配置和维护

**数量限制**：建议 1-3 人

---

### 2.2 场景管理员（SCENARIO_ADMIN）

**职责**：负责特定场景（应用）的配置和管理

**权限范围**：
- ✅ 管理分配给自己的场景
- ✅ 智能标注（自己场景的数据）
- ✅ 标注统计（自己场景的数据）
- ✅ 场景配置（根据系统管理员授予的细粒度权限）

**细粒度权限项**（由系统管理员配置）：
1. **场景基本信息管理** (`scenario_basic_info`)
   - 修改场景名称、描述
   - 启用/禁用场景

2. **场景敏感词管理** (`scenario_keywords`)
   - 查看场景敏感词
   - 添加/编辑/删除场景敏感词（黑名单）
   - 添加/编辑/删除场景敏感词（白名单）

3. **场景规则管理** (`scenario_policies`)
   - 查看场景规则
   - 添加/编辑/删除场景规则

4. **测试功能** (`playground`)
   - 使用输入测试功能
   - 查看测试历史

5. **性能测试** (`performance_test`)
   - 执行性能测试
   - 查看性能报告

**权限配置示例**：
```json
{
  "scenario_id": "app001",
  "permissions": {
    "scenario_basic_info": true,
    "scenario_keywords": true,
    "scenario_policies": false,  // 不能配置规则
    "playground": true,
    "performance_test": false
  }
}
```

**数量限制**：无限制，一个场景可以有多个管理员

---

### 2.3 数据标注员（ANNOTATOR）

**职责**：负责智能标注任务的执行

**权限范围**：
- ✅ 智能标注（仅限分配的场景）
- ✅ 认领标注任务
- ✅ 提交标注结果
- ❌ 无场景配置权限
- ❌ 无统计查看权限（只能看自己的标注记录）

**场景分配**：
- 可以分配到一个或多个场景
- 只能看到和操作分配给自己的场景的标注任务

**数量限制**：无限制

---

### 2.4 审计员（AUDITOR）- 可选角色

**职责**：查看系统运行状态和审计日志（只读）

**权限范围**：
- ✅ 查看所有场景配置（只读）
- ✅ 查看标注统计
- ✅ 查看审计日志
- ✅ 导出报表
- ❌ 无任何修改权限

**数量限制**：建议 1-2 人

---

## 三、权限矩阵

### 3.1 功能模块权限表

| 功能模块 | 系统管理员 | 场景管理员 | 数据标注员 | 审计员 |
|---------|-----------|-----------|-----------|--------|
| **用户管理** |
| 查看用户列表 | ✅ | ❌ | ❌ | ✅ |
| 创建用户 | ✅ | ❌ | ❌ | ❌ |
| 编辑用户 | ✅ | ❌ | ❌ | ❌ |
| 删除用户 | ✅ | ❌ | ❌ | ❌ |
| 分配角色 | ✅ | ❌ | ❌ | ❌ |
| 分配场景 | ✅ | ❌ | ❌ | ❌ |
| 配置权限 | ✅ | ❌ | ❌ | ❌ |
| **场景管理** |
| 查看所有场景 | ✅ | 🔸自己的 | 🔸分配的 | ✅ |
| 创建场景 | ✅ | ❌ | ❌ | ❌ |
| 编辑场景基本信息 | ✅ | 🔸可配置 | ❌ | ❌ |
| 删除场景 | ✅ | ❌ | ❌ | ❌ |
| **全局配置** |
| 元数据标签管理 | ✅ | ❌ | ❌ | ✅只读 |
| 全局敏感词管理 | ✅ | ❌ | ❌ | ✅只读 |
| 全局默认规则 | ✅ | ❌ | ❌ | ✅只读 |
| **场景配置** |
| 场景敏感词管理 | ✅ | 🔸可配置 | ❌ | ✅只读 |
| 场景规则管理 | ✅ | 🔸可配置 | ❌ | ✅只读 |
| **智能标注** |
| 查看标注任务 | ✅ | 🔸自己场景 | 🔸分配场景 | ✅ |
| 认领任务 | ✅ | ✅ | ✅ | ❌ |
| 提交标注 | ✅ | ✅ | ✅ | ❌ |
| 同步到正式库 | ✅ | ✅ | ❌ | ❌ |
| **统计分析** |
| 标注统计 | ✅ | 🔸自己场景 | 🔸自己的 | ✅ |
| 性能统计 | ✅ | 🔸可配置 | ❌ | ✅ |
| **测试功能** |
| 输入测试 | ✅ | 🔸可配置 | ❌ | ❌ |
| 性能测试 | ✅ | 🔸可配置 | ❌ | ❌ |
| **审计日志** |
| 查看审计日志 | ✅ | 🔸自己操作 | 🔸自己操作 | ✅ |

**图例**：
- ✅ 完全权限
- ❌ 无权限
- 🔸 条件权限（根据配置或范围限制）

---

## 四、数据模型设计

### 4.1 用户表（users）- 扩展

```sql
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    hashed_password VARCHAR(128) NOT NULL,
    role VARCHAR(32) NOT NULL,  -- SYSTEM_ADMIN, SCENARIO_ADMIN, ANNOTATOR, AUDITOR
    display_name VARCHAR(128),  -- 显示名称
    email VARCHAR(128),         -- 邮箱
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(36),     -- 创建人
    INDEX idx_role (role),
    INDEX idx_is_active (is_active)
);
```

### 4.2 用户场景关联表（user_scenario_assignments）- 新增

```sql
CREATE TABLE user_scenario_assignments (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    scenario_id VARCHAR(64) NOT NULL,
    role VARCHAR(32) NOT NULL,  -- SCENARIO_ADMIN, ANNOTATOR
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36),
    UNIQUE KEY uk_user_scenario (user_id, scenario_id),
    INDEX idx_user_id (user_id),
    INDEX idx_scenario_id (scenario_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 4.3 场景管理员权限配置表（scenario_admin_permissions）- 新增

```sql
CREATE TABLE scenario_admin_permissions (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    scenario_id VARCHAR(64) NOT NULL,

    -- 细粒度权限
    scenario_basic_info BOOLEAN DEFAULT TRUE,
    scenario_keywords BOOLEAN DEFAULT TRUE,
    scenario_policies BOOLEAN DEFAULT FALSE,
    playground BOOLEAN DEFAULT TRUE,
    performance_test BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(36),

    UNIQUE KEY uk_user_scenario_perm (user_id, scenario_id),
    INDEX idx_user_id (user_id),
    INDEX idx_scenario_id (scenario_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 4.4 审计日志表（audit_logs）- 新增

```sql
CREATE TABLE audit_logs (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    username VARCHAR(64) NOT NULL,
    action VARCHAR(64) NOT NULL,        -- CREATE, UPDATE, DELETE, VIEW, EXPORT
    resource_type VARCHAR(64) NOT NULL, -- USER, SCENARIO, KEYWORD, POLICY, etc.
    resource_id VARCHAR(64),
    scenario_id VARCHAR(64),            -- 关联的场景（如果有）
    details JSON,                       -- 操作详情
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_resource_type (resource_type),
    INDEX idx_scenario_id (scenario_id),
    INDEX idx_created_at (created_at)
);
```

---

## 五、API 设计

### 5.1 用户管理 API

#### 5.1.1 创建用户
```
POST /api/v1/users/
权限: SYSTEM_ADMIN
请求体:
{
  "username": "string",
  "password": "string",
  "role": "SCENARIO_ADMIN | ANNOTATOR | AUDITOR",
  "display_name": "string",
  "email": "string"
}
```

#### 5.1.2 分配场景
```
POST /api/v1/users/{user_id}/scenarios
权限: SYSTEM_ADMIN
请求体:
{
  "scenario_id": "string",
  "role": "SCENARIO_ADMIN | ANNOTATOR"
}
```

#### 5.1.3 配置场景管理员权限
```
PUT /api/v1/users/{user_id}/scenarios/{scenario_id}/permissions
权限: SYSTEM_ADMIN
请求体:
{
  "scenario_basic_info": true,
  "scenario_keywords": true,
  "scenario_policies": false,
  "playground": true,
  "performance_test": false
}
```

### 5.2 权限检查 API

#### 5.2.1 获取当前用户权限
```
GET /api/v1/auth/permissions
返回:
{
  "role": "SCENARIO_ADMIN",
  "scenarios": [
    {
      "scenario_id": "app001",
      "scenario_name": "客服场景",
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

#### 5.2.2 检查特定权限
```
GET /api/v1/auth/check-permission?scenario_id=app001&permission=scenario_keywords
返回:
{
  "has_permission": true
}
```

### 5.3 审计日志 API

#### 5.3.1 查询审计日志
```
GET /api/v1/audit-logs?user_id=xxx&action=CREATE&resource_type=KEYWORD&start_date=xxx&end_date=xxx
权限: SYSTEM_ADMIN, AUDITOR
```

---

## 六、前端设计

### 6.1 菜单权限控制

根据用户角色和权限动态生成菜单：

```typescript
// 系统管理员：所有菜单
const systemAdminMenu = [
  '用户管理',
  '场景管理',
  '元数据标签',
  '全局敏感词',
  '全局规则',
  '智能标注',
  '标注统计',
  '审计日志'
];

// 场景管理员：根据权限配置
const scenarioAdminMenu = [
  '智能标注',
  '标注统计',
  '场景配置' // 子菜单根据权限动态生成
];

// 数据标注员：仅标注
const annotatorMenu = [
  '智能标注'
];
```

### 6.2 页面权限控制

```typescript
// 路由守卫
const ProtectedRoute = ({ requiredRole, requiredPermission }) => {
  const userRole = getUserRole();
  const userPermissions = getUserPermissions();

  if (!hasRequiredRole(userRole, requiredRole)) {
    return <Navigate to="/403" />;
  }

  if (requiredPermission && !hasPermission(userPermissions, requiredPermission)) {
    return <Navigate to="/403" />;
  }

  return <Outlet />;
};
```

### 6.3 操作按钮权限控制

```typescript
// 按钮级别权限
<Button
  disabled={!hasPermission('scenario_keywords', 'create')}
  onClick={handleCreate}
>
  新增敏感词
</Button>
```

---

## 七、实施计划

### 7.1 第一阶段：数据库和后端基础（1-2天）

**任务**：
1. ✅ 创建数据库迁移脚本
   - 扩展 users 表
   - 创建 user_scenario_assignments 表
   - 创建 scenario_admin_permissions 表
   - 创建 audit_logs 表

2. ✅ 实现后端 Model 层
   - UserScenarioAssignment
   - ScenarioAdminPermission
   - AuditLog

3. ✅ 实现后端 Repository 层
   - 用户场景关联查询
   - 权限配置查询
   - 审计日志记录

4. ✅ 实现后端 Service 层
   - 权限检查服务
   - 审计日志服务

### 7.2 第二阶段：权限中间件和 API（2-3天）

**任务**：
1. ✅ 实现权限装饰器
   ```python
   @require_role("SYSTEM_ADMIN")
   @require_permission("scenario_keywords")
   @audit_log(action="CREATE", resource_type="KEYWORD")
   ```

2. ✅ 实现用户管理 API
   - 创建用户
   - 分配场景
   - 配置权限

3. ✅ 实现权限查询 API
   - 获取用户权限
   - 检查权限

4. ✅ 实现审计日志 API

### 7.3 第三阶段：前端权限控制（2-3天）

**任务**：
1. ✅ 实现权限上下文
   ```typescript
   const PermissionContext = createContext();
   ```

2. ✅ 实现菜单权限控制

3. ✅ 实现页面权限控制

4. ✅ 实现操作按钮权限控制

5. ✅ 实现用户管理页面
   - 用户列表
   - 创建/编辑用户
   - 分配场景
   - 配置权限

### 7.4 第四阶段：测试和优化（1-2天）

**任务**：
1. ✅ 单元测试
2. ✅ 集成测试
3. ✅ 权限测试
4. ✅ 性能优化
5. ✅ 文档完善

---

## 八、需求补充和待确认事项

### 8.1 需要确认的问题

1. **用户与场景的关系**
   - ❓ 一个场景管理员可以管理多个场景吗？
   - ✅ 建议：可以，通过 user_scenario_assignments 表支持多对多关系

2. **权限继承**
   - ❓ 场景管理员的权限是否可以继承？
   - ✅ 建议：不继承，每个场景独立配置权限

3. **默认权限**
   - ❓ 新创建的场景管理员默认有哪些权限？
   - ✅ 建议：默认只有基本信息和敏感词管理权限

4. **权限变更影响**
   - ❓ 修改权限后是否立即生效？
   - ✅ 建议：立即生效，前端需要刷新权限缓存

5. **数据标注员的场景分配**
   - ❓ 数据标注员可以看到所有场景的标注任务吗？
   - ✅ 建议：只能看到分配给自己的场景

6. **审计日志保留期**
   - ❓ 审计日志保留多久？
   - ✅ 建议：默认保留 90 天，可配置

7. **密码策略**
   - ❓ 是否需要密码复杂度要求？
   - ✅ 建议：最少 8 位，包含字母和数字

8. **会话管理**
   - ❓ Token 过期时间？
   - ✅ 建议：8 天（当前配置），可配置

### 8.2 功能增强建议

1. **权限模板**
   - 预定义常用权限组合
   - 快速分配权限

2. **批量操作**
   - 批量分配场景
   - 批量配置权限

3. **权限申请流程**
   - 用户申请权限
   - 管理员审批

4. **操作审批**
   - 敏感操作需要审批
   - 双人确认机制

5. **权限有效期**
   - 临时权限
   - 自动过期

---

## 九、风险和注意事项

### 9.1 安全风险

1. **权限提升攻击**
   - 风险：用户尝试访问未授权资源
   - 缓解：严格的后端权限检查，不依赖前端

2. **会话劫持**
   - 风险：Token 被窃取
   - 缓解：HTTPS、短期 Token、刷新机制

3. **SQL 注入**
   - 风险：权限查询中的 SQL 注入
   - 缓解：使用 ORM、参数化查询

### 9.2 性能风险

1. **权限查询性能**
   - 风险：每次请求都查询权限
   - 缓解：权限缓存、Redis

2. **审计日志写入**
   - 风险：大量日志影响性能
   - 缓解：异步写入、批量写入

### 9.3 兼容性风险

1. **现有数据迁移**
   - 风险：现有用户角色迁移
   - 缓解：提供迁移脚本

2. **API 兼容性**
   - 风险：现有 API 调用失败
   - 缓解：向后兼容、版本控制

---

## 十、总结

本需求文档定义了完整的 RBAC 系统，包括：
- ✅ 4 种角色定义（系统管理员、场景管理员、数据标注员、审计员）
- ✅ 细粒度权限控制（场景级别、功能级别）
- ✅ 完整的数据模型设计
- ✅ API 设计
- ✅ 前端权限控制方案
- ✅ 实施计划
- ✅ 风险评估

**下一步**：
1. 确认待定事项
2. 评审需求文档
3. 开始实施第一阶段

---

## 附录

### A. 术语表

- **RBAC**: Role-Based Access Control，基于角色的访问控制
- **场景**: 即应用（Application），业务场景的配置单元
- **细粒度权限**: 功能级别的权限控制
- **审计日志**: 记录用户操作的日志

### B. 参考资料

- [OWASP Access Control Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Access_Control_Cheat_Sheet.html)
- [NIST RBAC Model](https://csrc.nist.gov/projects/role-based-access-control)
