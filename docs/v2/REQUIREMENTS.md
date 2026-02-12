# LLM Guard Manager V2 — 需求文档

## 版本信息
- **版本**: V2.3
- **更新时间**: 2026-02-11
- **变更说明**: 基于实际代码实现，全面补充功能细节、API 端点、权限模型

---

## 一、项目概述

LLM Guard Manager 是一个 LLM 安全策略管理平台，用于配置敏感词库、分类标签、过滤规则，并测试内容过滤效果。

### 1.1 V2 核心变化

| 维度 | V1 | V2 |
|------|----|----|
| 前端 | React + Ant Design | Vue 3 + Element Plus + Vite |
| 后端 | Python FastAPI | Java Spring Boot 3.2.5 |
| 认证 | 直接 JWT 登录 | SSO 门户 + Ticket + JWT |
| 权限 | 无 | RBAC（全局角色 + 场景级权限） |
| 审计 | 无 | 全操作审计日志 |
| 标注 | 基础标注 | 智能标注（领取/审核/同步/统计） |
| 性能测试 | 无 | 阶梯负载 + 疲劳负载 + 实时监控 |
| 部署 | Docker 容器 | K8s (Minikube) + hostPath 挂载 |

### 1.2 技术栈

- **前端**: Vue 3.4 + TypeScript 5.2 + Element Plus 2.5 + Pinia 2.1 + Vue Router 4.2 + ECharts 5.5 + Axios + Vite 5.1
- **后端**: Spring Boot 3.2.5 + Spring Security + Spring Data JPA + MySQL + JJWT + Java 17
- **部署**: Minikube K8s + hostPath 挂载 + Nginx Ingress

---

## 二、SSO 登录流程

### 2.1 系统角色

| 系统 | 职责 | 实现 |
|------|------|------|
| Portal 门户 | 统一登录入口，跳转分发 | `portal/main.py` |
| Mock-USAP | 模拟企业认证中心（用户认证、Ticket 颁发） | `mock-usap/` |
| 安全管理平台 | 业务系统（Vue 前端 + Java 后端） | `frontend-vue/` + `backend-java/` |

### 2.2 完整登录链路

```
1. 用户访问 /portal/ → 输入用户名密码
2. Portal 调用 Mock-USAP POST /api/auth/login → 获取 session_id
3. 用户点击"LLM安全管理平台" → Portal 调用 Mock-USAP POST /api/auth/ticket → 获取 ticket
4. 重定向到 /web-manager/sso/login?ticket=TK_xxx
5. Vue 前端 SSOLogin 组件调用 Java 后端 POST /sso/login {ticket}
6. Java 后端调用 Mock-USAP POST /api/auth/validate-ticket 验证 ticket
7. 验证成功 → 同步/创建本地用户 → 生成 JWT Token（8天有效期）
8. 前端存储 token → 拉取用户权限 → 跳转到主页
```

### 2.3 双 Token 机制

| Token | 颁发方 | 有效期 | 用途 |
|-------|--------|--------|------|
| Ticket | Mock-USAP | 5 分钟，一次性 | SSO 跳转认证 |
| JWT Token | Java 后端 | 8 天 | 后续所有 API 调用的身份凭证 |

### 2.4 直接登录（管理员后门）

通过 `/web-manager/login` 页面，使用硬编码管理员账号直接登录（不经过 SSO），用于紧急管理。

---

## 三、功能模块

### 3.1 首页仪表盘（Dashboard）

- **路由**: `/`
- **功能**: 系统欢迎页，展示平台概览信息
- **权限**: 登录即可访问

### 3.2 标签管理（MetaTags）

- **路由**: `/tags`
- **功能**: 管理内容分类标签的层级体系
- **核心字段**:
  - `tag_code`: 标签编码，全局唯一
  - `tag_name`: 标签名称
  - `parent_code`: 父标签编码（支持层级关系）
  - `level`: 层级深度
  - `is_active`: 启用/禁用
- **操作**: 查看列表、创建、编辑、删除
- **权限**: SYSTEM_ADMIN 可增删改，其他角色只读

### 3.3 全局敏感词库（GlobalKeywords）

- **路由**: `/global-keywords`
- **功能**: 集中管理全平台共享的敏感词
- **核心字段**:
  - `keyword`: 敏感词，全局唯一
  - `tag_code`: 关联的分类标签
  - `risk_level`: 风险等级（High / Medium / Low）
  - `is_active`: 启用/禁用
- **操作**: 分页列表（支持搜索、标签筛选）、创建、编辑、删除
- **权限**: SYSTEM_ADMIN 可增删改，其他角色只读

### 3.4 场景管理（Scenarios/Apps）

- **路由**: `/apps`（列表）、`/apps/:appId`（详情）
- **功能**: 定义和管理应用场景
- **核心字段**:
  - `app_id`: 场景标识，全局唯一
  - `app_name`: 场景名称
  - `description`: 场景描述
  - `is_active`: 启用/禁用
  - `enable_whitelist`: 启用白名单
  - `enable_blacklist`: 启用黑名单
  - `enable_customize_policy`: 启用自定义策略
- **场景详情页（AppDashboard）**: 展示场景基本信息、功能开关状态，提供跳转到场景敏感词和场景策略的入口
- **权限**: SYSTEM_ADMIN 可增删改，SCENARIO_ADMIN 可查看已分配的场景

### 3.5 我的场景（MyScenarios）

- **路由**: `/my-scenarios`
- **功能**: 展示当前用户被分配的场景列表，快速进入场景管理
- **权限**: SCENARIO_ADMIN 角色可见

### 3.6 场景敏感词（ScenarioKeywords）

- **路由**: `/apps/:appId/keywords`
- **功能**: 管理场景级别的敏感词，支持两种模式
- **核心字段**:
  - `keyword`: 敏感词
  - `scenario_id`: 所属场景
  - `tag_code`: 关联标签
  - `rule_mode`: 规则模式（0=超级模式 / 1=自定义模式）
  - `category`: 分类（0=白名单 / 1=黑名单）
  - `risk_level`: 风险等级（High / Medium / Low）
  - `is_active`: 启用/禁用
- **唯一约束**: `keyword` + `scenario_id` + `rule_mode` 联合唯一
- **UI 结构**: 使用 Tab 页分别展示超级模式和自定义模式的关键词
- **操作**: 按分类筛选、搜索、创建、编辑、删除
- **权限**: 需要场景级 `scenario_keywords` 权限

### 3.7 规则策略

#### 3.7.1 场景策略（ScenarioPolicies）

- **路由**: `/apps/:appId/policies`
- **功能**: 配置场景级别的内容过滤规则
- **核心字段**:
  - `scenario_id`: 所属场景
  - `match_type`: 匹配类型（KEYWORD / TAG）
  - `match_value`: 匹配值（具体关键词或标签编码）
  - `rule_mode`: 规则模式（0=超级模式 / 1=自定义模式）
  - `extra_condition`: 附加条件
  - `strategy`: 处置策略（BLOCK / PASS / REWRITE）
  - `is_active`: 启用/禁用
- **UI 结构**: 使用 Tab 页分别展示超级模式和自定义模式的规则
- **权限**: 需要场景级 `scenario_policies` 权限

#### 3.7.2 全局默认策略（GlobalPolicies）

- **路由**: `/global-policies`
- **功能**: 配置全局兜底规则，当场景策略未匹配时生效
- **核心字段**:
  - `tag_code`: 匹配的标签编码
  - `extra_condition`: 附加条件
  - `strategy`: 处置策略（BLOCK / PASS / REWRITE）
  - `is_active`: 启用/禁用
- **权限**: SYSTEM_ADMIN 可增删改

### 3.8 输入试验场（Playground）

- **路由**: `/playground`
- **功能**: 测试内容过滤效果，验证策略配置是否正确
- **工作流程**:
  1. 选择目标场景（app_id）
  2. 输入测试文本
  3. 调用外部护栏服务进行检测
  4. 展示检测结果（决策、评分、延迟）
- **外部服务**: `http://127.0.0.1:8000/api/input/instance/rule/run`
- **决策评分体系**:
  - 0 = Pass（通过）
  - 50 = Rewrite（改写）
  - 100 = Block（拦截）
  - 1000 = Manual Review（人工审核）
- **历史记录**: 支持分页查询历史测试记录，可按 app_id 和 playground_type 筛选
- **权限**: 需要场景级 `playground` 权限

### 3.9 性能测试（PerformanceTest）

- **路由**: `/performance`
- **功能**: 对护栏服务进行压力测试，评估性能表现
- **测试模式**:
  - **疲劳负载（Fatigue）**: 固定并发数持续请求
  - **阶梯负载（Step）**: 逐步增加并发数，观察性能拐点
- **实时监控**: 通过轮询（1秒间隔）获取实时指标
  - RPS（每秒请求数）
  - 平均延迟、P95、P99 延迟
  - 当前并发用户数
  - 成功/失败计数
- **可视化**: 使用 ECharts 绘制实时性能曲线
- **操作**: 连通性测试（dry-run）、启动测试、停止测试、查看历史、删除历史
- **权限**: SYSTEM_ADMIN / SCENARIO_ADMIN 可启动测试

### 3.10 RBAC 权限系统（V2 新增）

#### 3.10.1 角色体系

| 角色 | 编码 | 说明 |
|------|------|------|
| 系统管理员 | SYSTEM_ADMIN | 全局最高权限，管理所有资源 |
| 场景管理员 | SCENARIO_ADMIN | 管理被分配的场景及其下属资源 |
| 标注员 | ANNOTATOR | 领取和审核标注任务 |
| 审计员 | AUDITOR | 查看审计日志 |

#### 3.10.2 权限层级

**全局权限**（由角色自动获得）:
- 标签管理、全局敏感词管理、全局策略管理
- 场景创建/删除
- 用户管理、角色管理
- 审计日志查看
- 标注任务同步到生产

**场景级权限**（按场景逐一分配）:
- `scenario_basic_info`: 查看/编辑场景基本信息
- `scenario_keywords`: 管理场景敏感词
- `scenario_policies`: 管理场景策略
- `playground`: 使用输入试验场
- `performance_test`: 执行性能测试

#### 3.10.3 权限检查机制

- 前端: Pinia store 缓存权限，`hasPermission()` / `hasScenarioPermission()` 控制 UI 渲染
- 后端: Spring Security `@PreAuthorize` + `PermissionService.checkScenarioPermission()` 双重校验
- 菜单: 根据权限动态显示/隐藏侧边栏菜单项

### 3.11 用户管理（UsersPage，V2 新增）

- **路由**: `/users`
- **功能**: 管理平台用户
- **操作**:
  - 查看用户列表
  - 分配/移除全局角色
  - 分配/移除场景（用户-场景关联）
  - 配置场景级细粒度权限
  - 启用/禁用用户
  - 删除用户
- **用户来源**: SSO 首次登录自动创建，管理员后续分配权限
- **权限**: SYSTEM_ADMIN 专属

### 3.12 角色管理（RolesPage，V2 新增）

- **路由**: `/roles`
- **功能**: 管理角色定义和角色-权限映射
- **操作**:
  - 查看角色列表
  - 创建/编辑/删除角色
  - 查看角色关联的权限项
  - 编辑角色权限（勾选权限项）
  - 查看所有可用权限项
- **系统角色**: 系统预置角色不可删除（`is_system = true`）
- **权限**: SYSTEM_ADMIN 专属

### 3.13 审计日志（AuditLogs，V2 新增）

- **路由**: `/audit-logs`
- **功能**: 查看系统操作审计轨迹
- **记录内容**:
  - `user_id` / `username`: 操作人
  - `action`: 操作类型（CREATE / UPDATE / DELETE 等）
  - `resource_type`: 资源类型（TAG / KEYWORD / SCENARIO / POLICY 等）
  - `resource_id`: 资源 ID
  - `scenario_id`: 关联场景
  - `details`: 操作详情（JSON）
  - `ip_address`: 客户端 IP
  - `user_agent`: 客户端标识
  - `created_at`: 操作时间
- **查询条件**: 按用户、操作类型、资源类型、场景、时间范围筛选
- **权限**: SYSTEM_ADMIN / AUDITOR 可查看

### 3.14 智能标注（SmartLabeling，V2 新增）

- **路由**: `/smart-labeling`
- **功能**: 标注员审核 AI 预标注的敏感词和规则

#### 3.14.1 任务类型

| 类型 | 暂存表 | 审核内容 |
|------|--------|---------|
| 关键词标注 | `staging_global_keywords` | 预测标签、预测风险等级 → 确认/修改最终标签和风险等级 |
| 规则标注 | `staging_global_rules` | 预测策略 → 确认/修改最终策略和附加条件 |

#### 3.14.2 任务状态流转

```
PENDING → CLAIMED → CONFIRMED / IGNORED
                         ↓
                    SYNCED（同步到生产表）
```

#### 3.14.3 工作流程

1. **领取任务**: 标注员点击"领取"，系统分配一批任务（50条），设置 30 分钟超时
2. **审核任务**: 逐条或批量审核（确认/忽略），可修改预测结果
3. **超时释放**: 超过 30 分钟未完成的任务自动释放回待领取池
4. **同步生产**: SYSTEM_ADMIN 将已确认的标注结果同步到全局敏感词库/规则库

#### 3.14.4 统计面板

- **标注员统计页**（`/annotator-stats`）: 各标注员的任务完成量、确认率、忽略率
- **我的任务统计**: 当前用户的任务进度
- **总览**: 各状态任务数量分布

### 3.15 标注员统计（AnnotatorStats，V2 新增）

- **路由**: `/annotator-stats`
- **功能**: 展示所有标注员的工作量统计和绩效指标
- **权限**: SYSTEM_ADMIN 可查看

---

## 四、完整 API 端点

Base URL: `/dbmanage/api/v1`（经 Ingress 转发后为 `/api/v1`）

### 4.1 认证

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| POST | `/login/access-token` | 用户名密码登录 | 公开 |

### 4.2 SSO

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| POST | `/sso/login` | Ticket 登录 | 公开 |
| GET | `/sso/user-info` | 获取当前用户信息 | 已登录 |
| POST | `/sso/users/batch` | 批量获取用户信息 | 已登录 |
| GET | `/sso/health` | USAP 健康检查 | 公开 |

### 4.3 标签管理

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/tags/` | 获取所有标签 | 已登录 |
| POST | `/tags/` | 创建标签 | SYSTEM_ADMIN |
| PUT | `/tags/{tagId}` | 更新标签 | SYSTEM_ADMIN |
| DELETE | `/tags/{tagId}` | 删除标签 | SYSTEM_ADMIN |

### 4.4 全局敏感词

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/keywords/global/` | 分页查询（支持 search、tag_code 筛选） | 已登录 |
| POST | `/keywords/global/` | 创建全局敏感词 | SYSTEM_ADMIN |
| PUT | `/keywords/global/{keywordId}` | 更新全局敏感词 | SYSTEM_ADMIN |
| DELETE | `/keywords/global/{keywordId}` | 删除全局敏感词 | SYSTEM_ADMIN |

### 4.5 场景敏感词

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/keywords/scenario/{scenarioId}` | 查询场景敏感词（可选 rule_mode 筛选） | 场景级权限 |
| POST | `/keywords/scenario/` | 创建场景敏感词 | 场景级权限 |
| PUT | `/keywords/scenario/{keywordId}` | 更新场景敏感词 | 场景级权限 |
| DELETE | `/keywords/scenario/{keywordId}` | 删除场景敏感词 | 场景级权限 |

### 4.6 场景策略

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/policies/scenario/{scenarioId}` | 查询场景策略 | 场景级权限 |
| POST | `/policies/scenario/` | 创建场景策略 | 场景级权限 |
| PUT | `/policies/scenario/{policyId}` | 更新场景策略 | 场景级权限 |
| DELETE | `/policies/scenario/{policyId}` | 删除场景策略 | 场景级权限 |

### 4.7 全局默认策略

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/policies/defaults/` | 查询全局默认策略 | 已登录 |
| POST | `/policies/defaults/` | 创建全局默认策略 | SYSTEM_ADMIN |
| PUT | `/policies/defaults/{defaultId}` | 更新全局默认策略 | SYSTEM_ADMIN |
| DELETE | `/policies/defaults/{defaultId}` | 删除全局默认策略 | SYSTEM_ADMIN |

### 4.8 场景管理

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/apps/` | 获取所有场景 | 已登录 |
| POST | `/apps/` | 创建场景 | SYSTEM_ADMIN |
| GET | `/apps/{appId}` | 按 app_id 获取场景 | 已登录 |
| PUT | `/apps/{scenarioId}` | 更新场景 | SYSTEM_ADMIN |
| DELETE | `/apps/{scenarioId}` | 删除场景 | SYSTEM_ADMIN |

### 4.9 输入试验场

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| POST | `/playground/input` | 执行内容过滤测试 | 场景级权限 |
| GET | `/playground/history` | 查询测试历史（分页，支持 app_id/type 筛选） | 已登录 |

### 4.10 性能测试

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| POST | `/performance/dry-run` | 连通性测试（单次请求） | 已登录 |
| POST | `/performance/start` | 启动性能测试 | SYSTEM_ADMIN / SCENARIO_ADMIN |
| POST | `/performance/stop` | 停止正在运行的测试 | 已登录 |
| GET | `/performance/status` | 获取实时测试状态 | 已登录 |
| GET | `/performance/history` | 获取测试历史列表 | 已登录 |
| GET | `/performance/history/{testId}` | 获取测试详情 | 已登录 |
| DELETE | `/performance/history/{testId}` | 删除测试记录 | SYSTEM_ADMIN |

### 4.11 用户管理

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/users/` | 获取用户列表 | SYSTEM_ADMIN |
| PUT | `/users/{userId}/role` | 更新用户角色 | SYSTEM_ADMIN |
| PATCH | `/users/{userId}/status` | 启用/禁用用户 | SYSTEM_ADMIN |
| DELETE | `/users/{userId}` | 删除用户 | SYSTEM_ADMIN |
| GET | `/users/{userId}/scenarios` | 获取用户的场景分配 | SYSTEM_ADMIN |
| POST | `/users/{userId}/scenarios` | 分配场景给用户 | SYSTEM_ADMIN |
| DELETE | `/users/{userId}/scenarios/{assignmentId}` | 移除场景分配 | SYSTEM_ADMIN |
| PUT | `/users/{userId}/scenarios/{scenarioId}/permissions` | 配置场景级细粒度权限 | SYSTEM_ADMIN |
| GET | `/users/{userId}/roles` | 获取用户的角色分配 | SYSTEM_ADMIN |
| POST | `/users/{userId}/roles` | 分配角色给用户 | SYSTEM_ADMIN |
| DELETE | `/users/{userId}/roles/{assignmentId}` | 移除角色分配 | SYSTEM_ADMIN |
| GET | `/users/me/permissions` | 获取当前用户权限（含场景级） | 已登录 |

### 4.12 角色管理

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/roles/` | 获取所有角色 | 已登录 |
| POST | `/roles/` | 创建角色 | SYSTEM_ADMIN |
| PUT | `/roles/{roleId}` | 更新角色 | SYSTEM_ADMIN |
| DELETE | `/roles/{roleId}` | 删除角色 | SYSTEM_ADMIN |
| GET | `/roles/{roleId}/permissions` | 获取角色权限 | 已登录 |
| PUT | `/roles/{roleId}/permissions` | 更新角色权限 | SYSTEM_ADMIN |
| GET | `/roles/permissions/all` | 获取所有可用权限项 | 已登录 |

### 4.13 权限

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/permissions/me` | 获取当前用户权限 | 已登录 |
| POST | `/permissions/check` | 检查指定权限 | 已登录 |

### 4.14 审计日志

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/audit-logs/` | 查询审计日志（支持多条件筛选） | SYSTEM_ADMIN / AUDITOR |
| GET | `/audit-logs/count` | 统计审计日志数量 | SYSTEM_ADMIN / AUDITOR |

### 4.15 智能标注（Staging）

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/staging/keywords` | 查询暂存关键词（分页，支持 status/my_tasks 筛选） | 已登录 |
| PATCH | `/staging/keywords/{keywordId}` | 审核单条关键词 | 已登录 |
| POST | `/staging/keywords/batch-review` | 批量审核关键词 | 已登录 |
| POST | `/staging/keywords/sync` | 同步已确认关键词到生产表 | SYSTEM_ADMIN |
| POST | `/staging/keywords/import-mock` | 导入模拟关键词数据 | SYSTEM_ADMIN |
| DELETE | `/staging/keywords/{keywordId}` | 删除暂存关键词 | 已登录 |
| GET | `/staging/rules` | 查询暂存规则 | 已登录 |
| PATCH | `/staging/rules/{ruleId}` | 审核单条规则 | 已登录 |
| POST | `/staging/rules/batch-review` | 批量审核规则 | 已登录 |
| POST | `/staging/rules/sync` | 同步已确认规则到生产表 | SYSTEM_ADMIN |
| POST | `/staging/rules/import-mock` | 导入模拟规则数据 | SYSTEM_ADMIN |
| DELETE | `/staging/rules/{ruleId}` | 删除暂存规则 | 已登录 |
| POST | `/staging/claim` | 领取一批标注任务 | 已登录 |
| POST | `/staging/release-expired` | 释放超时未完成的任务 | 已登录 |
| GET | `/staging/stats/annotators` | 获取标注员统计 | SYSTEM_ADMIN |
| GET | `/staging/my-tasks/stats` | 获取当前用户任务统计 | 已登录 |
| GET | `/staging/overview` | 获取标注任务总览 | 已登录 |

### 4.16 健康检查

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/actuator/health` | Spring Boot 健康检查 |

---

## 五、数据模型

### 5.1 核心业务表

| 表名 | 说明 | 唯一约束 |
|------|------|---------|
| `meta_tags` | 分类标签 | `tag_code` |
| `lib_global_keywords` | 全局敏感词 | `keyword` |
| `lib_scenario_keywords` | 场景敏感词 | `keyword` + `scenario_id` + `rule_mode` |
| `scenarios` | 应用场景 | `app_id` |
| `rule_scenario_policy` | 场景策略 | `scenario_id` + `rule_mode` + `match_type` + `match_value` |
| `rule_global_defaults` | 全局默认策略 | `tag_code` + `extra_condition` |
| `playground_history` | 试验场历史 | 无 |

### 5.2 权限相关表

| 表名 | 说明 |
|------|------|
| `users` | 用户表（SSO 同步 + 硬编码管理员） |
| `roles` | 角色定义 |
| `permissions` | 权限项定义 |
| `role_permissions` | 角色-权限映射 |
| `user_scenario_assignments` | 用户-场景分配 |
| `user_scenario_roles` | 用户-场景-角色映射 |
| `scenario_admin_permissions` | 场景级细粒度权限配置 |

### 5.3 标注相关表

| 表名 | 说明 |
|------|------|
| `staging_global_keywords` | 暂存关键词（待标注） |
| `staging_global_rules` | 暂存规则（待标注） |

### 5.4 审计表

| 表名 | 说明 |
|------|------|
| `audit_logs` | 操作审计日志 |

---

## 六、前端路由总览

| 路由 | 页面组件 | 功能 | 菜单位置 |
|------|---------|------|---------|
| `/login` | LoginPage | 直接登录 | 无（公开） |
| `/sso/login` | SSOLogin | SSO 跳转登录 | 无（公开） |
| `/` | Dashboard | 首页仪表盘 | 首页 |
| `/tags` | MetaTags | 标签管理 | 基础配置 |
| `/global-keywords` | GlobalKeywords | 全局敏感词 | 基础配置 |
| `/global-policies` | GlobalPolicies | 全局默认策略 | 基础配置 |
| `/apps` | Apps | 场景列表 | 场景管理 |
| `/apps/:appId` | AppDashboard | 场景详情 | 场景管理（子页） |
| `/apps/:appId/keywords` | ScenarioKeywords | 场景敏感词 | 场景管理（子页） |
| `/apps/:appId/policies` | ScenarioPolicies | 场景策略 | 场景管理（子页） |
| `/my-scenarios` | MyScenarios | 我的场景 | 场景管理 |
| `/playground` | InputPlayground | 输入试验场 | 测试工具 |
| `/performance` | PerformanceTest | 性能测试 | 测试工具 |
| `/smart-labeling` | SmartLabeling | 智能标注 | 标注管理 |
| `/annotator-stats` | AnnotatorStats | 标注员统计 | 标注管理 |
| `/users` | UsersPage | 用户管理 | 系统管理 |
| `/roles` | RolesPage | 角色管理 | 系统管理 |
| `/audit-logs` | AuditLogs | 审计日志 | 系统管理 |

---

## 七、账号密码

### 7.1 Portal 门户登录（Mock USAP 账号）

通过 `/portal/` 登录，SSO 跳转到安全管理平台。

| 用户名 | 密码 | 姓名 | 部门 | 状态 |
|--------|------|------|------|------|
| admin | Gn1yo0jY | 系统管理员 | IT部 | active |
| zhangsan | Zs3nKx8q | 张三 | 技术部 | active |
| lisi | Ls4wPm7j | 李四 | 产品部 | active |
| wangwu | Ww5tRn2v | 王五 | 运营部 | active |
| zhaoliu | Zl6yHb3k | 赵六 | 技术部 | active |
| sunqi | Sq7cNd4f | 孙七 | 安全部 | active |
| zhouba | Zb8gTe5m | 周八 | 技术部 | **inactive** |
| wujiu | Wj9hXf6p | 吴九 | 产品部 | active |
| zhengshi | Zs0kYg7r | 郑十 | 运营部 | active |
| test | Ts2bMc8w | 测试用户 | 测试部 | active |

### 7.2 直接登录（硬编码管理员）

通过 `/web-manager/login` 直接登录（Java 后端 AuthController）。

| 用户名 | 密码 | 角色 |
|--------|------|------|
| llm_guard | 68-8CtBhug | SYSTEM_ADMIN |

### 7.3 数据库

| 项目 | 值 |
|------|-----|
| Host | 49.233.46.126:38306 |
| Database | llm_safe_db |
| User | root |
| Password | Platform#2026 |
