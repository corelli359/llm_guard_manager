# LLM Guard Manager - 需求文档 (PRD)

## 1. 项目概述
本项目旨在构建一个前后端分离的 **LLM 安全管控管理平台 (LLM Guard Manager)**。
该平台用于可视化的管理大模型应用中的敏感词、内容分类标签、场景策略以及全局规则，帮助管理员灵活地配置内容过滤与合规策略。

## 2. 核心功能模块

基于现有的数据库模型设计，系统分为以下四大核心模块：

### 2.1 元数据标签管理 (Meta Tags Management)
**对应模型:** `MetaTags`
**功能描述:** 管理内容分类标签，支持层级结构，用于后续的关键词归类和规则匹配。

*   **功能点:**
    *   **标签列表展示:** 展示标签编码、名称、层级、父级标签。
    *   **新建标签:** 输入 Tag Code (唯一), Tag Name, Parent Code (可选), Level。
    *   **编辑标签:** 修改名称、层级、启用/禁用状态。
    *   **删除标签:** 软删除或物理删除（需校验是否被关键词引用）。
    *   **层级视图:** (可选) 以树形结构展示标签体系。

### 2.2 全局关键词库 (Global Keywords Library)
**对应模型:** `GlobalKeywords`
**功能描述:** 维护全局通用的敏感词库。这些词汇通常适用于所有场景。

*   **功能点:**
    *   **关键词检索:** 支持按关键词模糊搜索、按 Tag 筛选、按风险等级筛选。
    *   **新增关键词:** 录入 Keyword, 关联 Tag Code, 设置 Risk Level (如 High/Medium/Low)。
    *   **状态管理:** 启用/禁用关键词。
    *   **批量导入/导出:** (建议) 支持 CSV/Excel 格式导入大量关键词。

### 2.3 场景关键词库 (Scenario Keywords Library)
**对应模型:** `ScenarioKeywords`
**功能描述:** 针对特定业务场景（Scenario）维护的专用词库，支持黑名单和白名单模式。

*   **功能点:**
    *   **场景筛选:** 选择特定 `scenario_id` 查看该场景下的词库。
    *   **关键词管理:** 新增/编辑/删除场景关键词。
    *   **名单类型:** 设置是 **黑名单 (Block)** 还是 **白名单 (Allow/White)** (`category` 字段: 0=白, 1=黑)。
    *   **属性配置:** 关联 Tag Code, 风险等级。

### 2.4 规则与策略配置 (Rule & Policy Configuration)
该模块决定了系统如何根据命中的关键词或标签进行处置（拦截、放行、重写等）。

#### A. 场景策略配置 (Scenario Policy)
**对应模型:** `RuleScenarioPolicy`
**功能描述:** 定义特定场景下的精细化处置规则。

*   **功能点:**
    *   **策略列表:** 展示各场景的配置规则。
    *   **新增规则:**
        *   指定 `scenario_id`。
        *   选择匹配类型 (`match_type`): 命中具体的 **KEYWORD** 还是命中某个 **TAG**。
        *   输入匹配值 (`match_value`): 具体的词或 Tag Code。
        *   选择处置策略 (`strategy`): BLOCK (拦截) / PASS (放行) / REWRITE (重写)。
    *   **优先级/模式:** 设置 `rule_mode` 和 `extra_condition`。

#### B. 全局默认规则 (Global Defaults)
**对应模型:** `RuleGlobalDefaults`
**功能描述:** 当场景策略未覆盖时，基于标签的全局兜底处置规则。

*   **功能点:**
    *   **配置默认策略:** 针对特定的 `tag_code` 设置默认动作 (`strategy`)。
    *   **例如:** 所有标记为 "Politically Sensitive" (Tag) 的内容，全局默认 "BLOCK"。

## 3. 非功能性需求
*   **架构:** 前后端分离。
    *   **前端:** 建议使用 React/Vue + Ant Design/Element Plus 等组件库构建管理后台。
    *   **后端:** Python (基于现有 SQLAlchemy 模型，建议 FastAPI/Flask)。
*   **性能:** 关键词匹配可能涉及高性能需求，管理端主要关注 CRUD 的响应速度。
*   **扩展性:** `scenario_id` 目前为字符串，未来可能需要一张独立的 `Scenarios` 表来维护场景元数据。

## 4. 接口规划 (API Draft)
*   `GET /api/tags`: 获取标签树/列表
*   `POST /api/tags`: 创建标签
*   `PUT /api/tags/{id}`: 更新标签
*   `DELETE /api/tags/{id}`: 删除标签
*   `GET /api/keywords/global`: 搜索全局关键词
*   `POST /api/keywords/global`: 添加全局关键词
*   `GET /api/keywords/scenario`: 获取场景关键词
*   `POST /api/keywords/scenario`: 添加场景关键词
*   `GET /api/policy/scenario`: 获取场景策略
*   `POST /api/policy/scenario`: 配置场景规则
*   `GET /api/policy/defaults`: 获取全局默认规则
*   `POST /api/policy/defaults`: 配置全局默认规则
