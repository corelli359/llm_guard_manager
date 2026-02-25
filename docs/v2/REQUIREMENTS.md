# LLM Guard Manager V2 — 需求文档

## 版本信息
- **版本**: V2.2
- **更新时间**: 2026-02-10

---

## 一、项目概述

LLM Guard Manager 是一个 LLM 安全策略管理平台，用于配置敏感词库、分类标签、过滤规则，并测试内容过滤效果。

V2 版本核心变化：
1. **后端从 Python FastAPI 迁移到 Java Spring Boot**
2. **前端从 React 迁移到 Vue 3**
3. **登录方式从直接登录改为 SSO 门户登录**
4. **新增 RBAC 权限系统、审计日志、智能标注等功能**

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
8. 前端存储 token，跳转到主页
```

### 2.3 双 Token 机制

- **Ticket**：USAP 颁发，一次性使用，5 分钟有效
- **JWT Token**：Java 后端颁发，8 天有效，用于后续所有 API 调用

---

## 三、功能模块

### 3.1 标签管理（MetaTags）
- 层级分类标签体系（parent_code 支持父子关系）
- tag_code 全局唯一

### 3.2 全局敏感词（GlobalKeywords）
- 集中管理敏感词库
- 关联标签、风险等级（High/Medium/Low）
- keyword 全局唯一

### 3.3 场景管理（Scenarios/Apps）
- 定义应用场景，app_id 全局唯一
- 支持白名单/黑名单/自定义策略开关

### 3.4 场景敏感词（ScenarioKeywords）
- 场景级敏感词，支持白名单(0)/黑名单(1)分类
- keyword + scenario_id 联合唯一

### 3.5 规则策略
- **场景策略**：按场景配置，支持 KEYWORD/TAG 匹配
- **全局默认策略**：场景策略未匹配时的兜底规则

### 3.6 输入试验场（Playground）
- 测试内容过滤效果
- 记录请求/响应、评分、延迟

### 3.7 性能测试（Performance）
- 支持阶梯负载和疲劳负载模式
- 实时状态监控和历史记录

### 3.8 RBAC 权限系统（V2 新增）
- **角色**：SYSTEM_ADMIN、SCENARIO_ADMIN、ANNOTATOR、AUDITOR
- **场景级权限**：每个用户可分配不同场景的不同权限
- **权限项**：scenario_keywords、scenario_policies、playground、performance_test 等

### 3.9 用户管理（V2 新增）
- 用户通过 SSO 首次登录自动创建
- 管理员可分配角色、场景权限、启用/禁用用户

### 3.10 审计日志（V2 新增）
- 记录所有关键操作
- 支持按时间、用户、操作类型查询

### 3.11 智能标注（V2 新增）
- 标注员领取批次任务
- 支持关键词标注和规则标注
- 批次倒计时、统计面板

### 3.12 自动化测评（V2 新增）

批量验证安全围栏策略有效性的测评系统，核心流程：导入测评题 → 批量跑围栏 → 大模型二次评判 → 统计指标。

#### 3.12.1 测评题库管理
- 支持 Excel/CSV 批量导入测评话术，字段：话术内容、所属标签（多标签）、风险点、预期结果（合规/违规）
- 支持单条新增/编辑/删除
- 单条测评题可匹配多个标签（如同时匹配「歧义话术 + 日常沟通」）
- 支持按标签、预期结果、关键词筛选

#### 3.12.2 批量测评执行
- 选择测评场景（app_id），可按标签/预期结果筛选题目范围
- 队列机制：批量提交后自动加入任务队列，支持查看进度（待执行/执行中/已完成/失败）
- 并发控制：支持配置并发数（1-20），避免服务过载
- 支持取消运行中的任务

#### 3.12.3 智能技术测评（大模型评判）
- 调用大模型对围栏判定结果进行二次评判
- 输入：测评题话术 + 所属标签 + 预期结果 + 围栏判定结果
- 输出：最终风险判定（合规/违规）、判定原因、置信度
- 当前为 Mock 实现：约 80% 与围栏一致，20% 不一致，模拟真实场景

#### 3.12.4 指标统计分析

| 指标名称 | 定义 | 用途 |
|----------|------|------|
| 拦截率 | 被围栏拦截的样本数 / 总样本数 | 衡量围栏拦截力度 |
| 漏检率 | 违规样本中被放行的数量 / 总违规样本数 | 衡量策略未拦截的风险漏洞 |
| 误检率 | 合规样本中被拦截的数量 / 总合规样本数 | 衡量策略过度拦截的合规问题 |
| 合格率 | 正确判定样本数 / 总样本数 | 整体衡量策略有效性 |

- 支持全维度和按标签维度统计
- 可视化展示：柱状图（各标签指标对比）、饼图（风险类型分布）
- 详细指标表格

#### 3.12.5 后续规划（未实现）
- 人工抽检校正：支持抽检率配置、专家校正操作、校正记录
- 基线校验与上线联动：按标签维度设置指标基线，自动校验是否达标
- 报告生成：自动生成测评报告，支持导出 PDF/Excel

#### 3.12.6 数据库表

| 表名 | 说明 |
|------|------|
| `eval_test_cases` | 测评题库（话术内容、标签、预期结果） |
| `eval_tasks` | 测评任务（场景、状态、进度、指标） |
| `eval_task_results` | 单条测评结果（围栏结果、LLM判定、正确性） |

---

## 四、API 端点汇总

Base URL: `/dbmanage/api/v1`（经 Ingress 转发后为 `/api/v1`）

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | `POST /login/access-token` | 直接登录（管理员） |
| SSO | `POST /sso/login` | Ticket 登录 |
| SSO | `GET /sso/user-info` | 获取当前用户信息 |
| SSO | `POST /sso/users/batch` | 批量获取用户信息 |
| SSO | `GET /sso/health` | USAP 健康检查 |
| 标签 | `GET/POST /tags/` | 标签列表/创建 |
| 标签 | `PUT/DELETE /tags/{id}` | 标签更新/删除 |
| 全局词 | `GET/POST /keywords/global/` | 全局敏感词列表/创建 |
| 场景词 | `GET /keywords/scenario/{id}` | 场景敏感词列表 |
| 场景策略 | `GET/POST /policies/scenario/{id}` | 场景策略 |
| 全局策略 | `GET/POST /policies/defaults/` | 全局默认策略 |
| 场景 | `GET/POST /apps/` | 场景列表/创建 |
| 试验场 | `POST /playground/input` | 测试内容过滤 |
| 试验场 | `GET /playground/history` | 测试历史 |
| 性能 | `POST /performance/start` | 启动性能测试 |
| 用户 | `GET /users/` | 用户列表 |
| 角色 | `GET/POST /roles/` | 角色管理 |
| 权限 | `GET /permissions/me` | 当前用户权限 |
| 审计 | `GET /audit-logs/` | 审计日志查询 |
| 标注 | `POST /staging/claim` | 领取标注任务 |
| 测评 | `GET /evaluation/test-cases` | 测评题库列表 |
| 测评 | `POST /evaluation/test-cases` | 新增测评题 |
| 测评 | `POST /evaluation/test-cases/import` | 批量导入测评题 |
| 测评 | `GET /evaluation/test-cases/count` | 按条件统计题数 |
| 测评 | `POST /evaluation/tasks` | 创建并启动测评任务 |
| 测评 | `GET /evaluation/tasks` | 测评任务列表 |
| 测评 | `GET /evaluation/tasks/{id}` | 任务详情（含进度） |
| 测评 | `GET /evaluation/tasks/{id}/results` | 单条结果列表 |
| 测评 | `GET /evaluation/tasks/{id}/metrics` | 指标统计 |
| 测评 | `POST /evaluation/tasks/{id}/cancel` | 取消任务 |
| 健康 | `GET /actuator/health` | 后端健康检查 |

---

## 五、账号密码

### 5.1 Portal 门户登录（Mock USAP 账号）

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

### 5.2 直接登录（硬编码管理员）

通过 `/web-manager/login` 直接登录（Java 后端 AuthController）。

| 用户名 | 密码 | 角色 |
|--------|------|------|
| llm_guard | 68-8CtBhug | SYSTEM_ADMIN |

### 5.3 数据库

| 项目 | 值 |
|------|-----|
| Host | 49.233.46.126:38306 |
| Database | llm_safe_db |
| User | root |
| Password | Platform#2026 |
