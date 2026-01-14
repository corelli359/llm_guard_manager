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
**对应模型:** `RuleScenarioPolicy` (规则), `ScenarioKeywords` (敏感词)
**功能描述:** 定义特定场景下的精细化处置规则和敏感词管理。

**页面结构设计:**

场景策略管理页面采用两层Tab结构，清晰区分不同模式和管理内容：

```
场景策略管理页面
├─ Tab 1: 自定义模式管理
│   ├─ 子Tab 1.1: 敏感词管理（黑名单/白名单）
│   │   ├─ 数据来源：ScenarioKeywords 表
│   │   ├─ 功能：
│   │   │   ├─ 列表展示：黑名单(category=1)和白名单(category=0)混合显示
│   │   │   ├─ 过滤器：按类型筛选（全部/仅黑名单/仅白名单）
│   │   │   ├─ 搜索：支持按关键词内容模糊搜索
│   │   │   ├─ 标识：用不同颜色Tag区分黑名单/白名单
│   │   │   └─ CRUD：新增/编辑/删除敏感词
│   │   └─ 字段说明：
│   │       ├─ keyword: 敏感词内容
│   │       ├─ category: 0=白名单, 1=黑名单
│   │       ├─ tag_code: 关联的标签编码
│   │       ├─ risk_level: 风险等级(High/Medium/Low)
│   │       └─ is_active: 启用/禁用状态
│   │
│   └─ 子Tab 1.2: 规则管理
│       ├─ 数据来源：RuleScenarioPolicy 表（rule_mode = "自定义模式"）
│       ├─ 功能：
│       │   ├─ 列表展示：展示规则的匹配类型、匹配值、策略动作等
│       │   ├─ 搜索：支持按匹配值、策略类型搜索
│       │   └─ CRUD：新增/编辑/删除规则
│       ├─ 新增/编辑规则字段：
│       │   ├─ match_type: 匹配类型（KEYWORD/TAG）
│       │   ├─ match_value: 匹配值（具体的词或Tag Code）
│       │   ├─ strategy: 处置策略（BLOCK/PASS/REWRITE）
│       │   └─ extra_condition: 额外条件（可选）
│       └─ 注意：不再包含敏感词设置选项（敏感词在"敏感词管理"中配置）
│
└─ Tab 2: 超级模式管理
    ├─ 子Tab 2.1: 敏感词管理（黑名单/白名单）
    │   ├─ 数据来源：ScenarioKeywords 表
    │   ├─ 功能：同自定义模式的敏感词管理
    │   │   ├─ 列表展示：黑白名单混合显示
    │   │   ├─ 过滤器：按类型筛选（全部/仅黑名单/仅白名单）
    │   │   ├─ 搜索：支持按关键词内容模糊搜索
    │   │   ├─ 标识：用不同颜色Tag区分黑名单/白名单
    │   │   └─ CRUD：新增/编辑/删除敏感词
    │   └─ 说明：自定义模式和超级模式共享同一套敏感词库
    │
    └─ 子Tab 2.2: 规则管理
        ├─ 数据来源：RuleScenarioPolicy 表（rule_mode = "超级模式"）
        ├─ 功能：同自定义模式的规则管理
        │   ├─ 列表展示：展示规则配置
        │   ├─ 搜索：支持按匹配值、策略类型搜索
        │   └─ CRUD：新增/编辑/删除规则
        └─ 注意：不再包含敏感词设置选项（敏感词在"敏感词管理"中配置）
```

**关键改进点:**

1. **清晰的层级结构:**
   - 第一层Tab：自定义模式 vs 超级模式（通过 `rule_mode` 字段区分）
   - 第二层子Tab：敏感词管理 vs 规则管理（分别对应不同的数据表）

2. **敏感词管理特性:**
   - 黑名单和白名单在同一列表中展示，通过 `category` 字段区分
   - 提供过滤器/分组功能：全部/仅黑名单(category=1)/仅白名单(category=0)
   - 支持关键词内容的模糊搜索
   - 列表中用不同颜色的Tag标识黑名单/白名单（如：黑名单用红色Tag，白名单用绿色Tag）
   - 支持启用/禁用状态切换

3. **规则管理特性:**
   - 自定义模式和超级模式的规则通过 `rule_mode` 字段区分，分开展示
   - 新增/编辑规则时，**移除敏感词设置选项**（敏感词已在"敏感词管理"中配置）
   - 规则配置只关注：匹配类型（KEYWORD/TAG）、匹配值、策略动作（BLOCK/PASS/REWRITE）等
   - 支持按匹配值、策略类型等条件搜索
   - 当 `match_type` 为 KEYWORD 时，匹配的是"敏感词管理"中配置的敏感词

4. **数据模型说明:**
   - 敏感词存储在 `ScenarioKeywords` 表，自定义模式和超级模式共享同一套敏感词库
   - 规则存储在 `RuleScenarioPolicy` 表，通过 `rule_mode` 字段区分自定义模式和超级模式
   - 敏感词和规则是独立管理的，规则通过 `match_type=KEYWORD` 和 `match_value` 引用敏感词

#### B. 全局默认规则 (Global Defaults)
**对应模型:** `RuleGlobalDefaults`
**功能描述:** 当场景策略未覆盖时，基于标签的全局兜底处置规则。

*   **功能点:**
    *   **配置默认策略:** 针对特定的 `tag_code` 设置默认动作 (`strategy`)。
    *   **例如:** 所有标记为 "Politically Sensitive" (Tag) 的内容，全局默认 "BLOCK"。
    *   **搜索功能:** 支持按 `tag_code` 或 `strategy` 搜索过滤。

### 2.5 数据一致性与唯一性校验 (Data Consistency & Uniqueness)
**目标:** 确保系统中的关键配置数据不重复，避免逻辑冲突。

*   **全局敏感词校验 (Global Keywords):**
    *   **校验规则:** 系统中同一个敏感词内容 (`keyword`) 必须唯一。
    *   **行为:** 新增或编辑时，若检测到重复词汇，系统应拒绝并报错。

*   **场景敏感词校验 (Scenario Keywords):**
    *   **校验规则:** 同一个场景 (`scenario_id`) 下，同一个敏感词内容 (`keyword`) 必须唯一。
    *   **互斥性:** 同一个词在同一场景下不能既是白名单又是黑名单，也不能重复定义为黑/白名单。

*   **场景策略校验 (Scenario Policy):**
    *   **校验规则:** 同一场景下，针对同一模式 (`rule_mode`)、同一匹配类型 (`match_type`) 和同一匹配值 (`match_value`) 的策略必须唯一。
    *   **行为:** 避免同一条件触发多条冲突策略。

*   **全局默认策略校验 (Global Defaults):**
    *   **校验规则:** 针对同一标签 (`tag_code`) 和同一额外条件 (`extra_condition`) 的默认策略必须唯一。

## 2.6 试验场
要构建三快内容，输入试验场、输出试验场和全流程试验场
### 2.6.1 输入试验场 (Input Playground)
**目标:** 提供一个交互式界面，允许用户选择特定场景 (`app_id`) 并输入测试文本，调用后端的围栏服务 (Guardrail Service) 实时检测内容合规性。

#### 1. 业务流程
1.  **配置阶段:** 用户在前端选择已有的场景 (`scenario_id` 即 `app_id`)，输入待检测文本，并配置检测参数（如是否启用白名单、VIP策略等）。
2.  **请求中转:** 后端接收请求，注入系统生成的 `request_id` 和配置的 `apikey`，将请求转发至内部围栏服务。
3.  **结果展示:** 前端接收围栏服务的返回结果，并根据 `final_decision.score` 进行可视化展示。

#### 2. 技术细节

*   **后端转发服务:**
    *   **目标地址:** `http://127.0.0.1:8000/api/input/instance/rule/run` (POST)
    *   **API Key:** 在后端配置中存储（可随机生成用于测试），不对前端暴露。
    *   **Request ID:** 后端自动生成 UUID。

*   **前端界面 (UI/UX):**
    *   **输入区:**
        *   **场景选择:** 下拉框列出当前系统中的所有 Scenario (`app_id`)。
        *   **Prompt 输入:** 多行文本框。
        *   **参数开关 (Switches):**
            *   `use_customize_white` (自定义白名单)
            *   `use_customize_words` (自定义敏感词)
            *   `use_customize_rule` (自定义规则)
            *   `use_vip_black` (VIP黑名单)
            *   `use_vip_white` (VIP白名单)
    *   **结果展示区:**
        *   **决策可视化:** 根据 `final_decision.score` 显示不同颜色/状态：
            *   `0`: **通过 (Pass)** - 绿色
            *   `50`: **改写 (Rewrite)** - 黄色
            *   `100`: **拒答 (Block)** - 红色
            *   `1000`: **转人工 (Manual Review)** - 橙色/紫色
        *   **详细信息:** 展示 `all_decision_dict` 或原始 JSON 以供调试。

#### 3. 数据交互

**前端 -> 后端 (`POST /api/v1/playground/input`):**
```json
{
  "app_id": "selected_scenario_id",
  "input_prompt": "user input...",
  "use_customize_white": true,
  "use_customize_words": true,
  "use_vip_black": false,
  "use_vip_white": false,
  "use_customize_rule": false
}
```

**后端 -> 围栏服务 (Proxy):**
```json
{
  "request_id": "uuid-gen-by-backend",
  "app_id": "...",
  "apikey": "configured-api-key",
  "input_prompt": "...",
  ... // 其他参数透传
}
```

**后端 -> 前端 (Response):**
直接透传围栏服务的 JSON 响应，或进行必要的字段封装。


### 2.6.2 输出试验场
需求待定
### 2.6.3 全流程试验场
需求待定

## 2.7 试验场历史记录 (Playground History)
**目标:** 记录各类试验场（输入、输出、全流程）的每一次交互数据，并提供历史查询功能。鉴于试验场包含多种类型（目前已有输入试验场，未来将扩展输出和全流程），历史记录模块需具备高扩展性以适配不同类型的输入输出结构。

#### 1. 数据模型 (`PlaygroundHistory`)
*   `id`: UUID, 主键。
*   `request_id`: UUID, 交互唯一标识，关联后端的日志或追踪ID。
*   `playground_type`: String, **[关键扩展字段]** 用于区分试验场类型。枚举值:
    *   `INPUT`: 输入试验场
    *   `OUTPUT`: 输出试验场
    *   `FULL`: 全流程试验场
*   `app_id`: String, 场景标识 (Scenario ID)。
*   `input_data`: JSON, **[通用化存储]** 存储请求参数。
    *   对于 *Input Playground*，存储 `{ "input_prompt": "..." }`。
    *   未来支持复杂结构的输入。
*   `config_snapshot`: JSON, 记录请求时的配置快照 (如 `use_vip_black`, `use_customize_white` 等开关状态)，便于回溯当时的策略环境。
*   `output_data`: JSON, **[通用化存储]** 完整记录围栏服务的响应结果 (`all_decision_dict` 等)。若发生错误，记录错误详情。
*   `score`: Integer, 提取核心风险分数 (如 `final_decision.score`)。若发生异常，可设为 -1。
*   `latency`: Integer, **[新增]** 总请求耗时 (毫秒)，指后端接收请求到处理完成的时间。
*   `upstream_latency`: Integer, **[新增]** 上游服务耗时 (毫秒)，指后端调用围栏服务 (Guardrail Service) 的实际耗时。
*   `created_at`: DateTime, 创建时间。

#### 2. 接口规划
*   **写入 (集成在各业务接口):**
    *   修改 `POST /api/v1/playground/input`: 
        *   记录**总开始时间**。
        *   在调用围栏服务前，记录**上游开始时间**。
        *   获取围栏服务响应（或捕获异常），记录**上游结束时间**，计算 `upstream_latency`。
        *   记录**总结束时间**，计算 `latency`。
        *   无论成功失败，尝试写入 `PlaygroundHistory`。
    *   未来 Output/Full 接口同理。
*   **查询 (`GET /api/v1/playground/history`):**
    *   **参数:**
        *   `page`: 页码
        *   `size`: 每页条数
        *   `playground_type`: (必填或可选) 筛选特定类型的历史。
        *   `app_id`: (可选) 筛选特定应用。
        *   `start_time` / `end_time`: (可选) 时间范围。
    *   **返回:** 分页的历史记录列表，包含摘要信息及 `latency`, `upstream_latency`。

#### 3. 前端交互
*   **History 组件:**
    *   在 `InputPlayground` (及未来页面) 增加 "History" 按钮。
    *   点击滑出侧边栏 (Drawer)，自动传递当前页面的 `playground_type` 进行查询。
*   **列表展示:**
    *   显示时间、App ID、摘要 (Input Preview)、结果状态 (Tag/Color)、**总耗时 (ms)**。
    *   错误状态需有明显标识 (如红色 Error Tag)。
*   **功能操作:**
    *   **查看详情:** 展开查看完整的 Request/Response JSON，以及**耗时详情 (Total vs Upstream)**。
    *   **回填/复用 (Restore):** 点击某条记录，将历史的 `input_data` 和 `config_snapshot` 重新填充到当前页面的表单中，以便快速重测。

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