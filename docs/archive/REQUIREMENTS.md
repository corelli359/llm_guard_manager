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
    *   **属性配置:**
        *   **关联 Tag Code:**
            *   **可选字段:** Tag Code 为可选项（`tag_code: Optional[str] = None`），黑名单和白名单均不强制要求关联 Tag Code。
        *   风险等级 (Risk Level)，可选。

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
    │   │       ├─ tag_code: 关联的标签编码 (可选)
    │   │       ├─ risk_level: 风险等级(High/Medium/Low)，可选
    │   │       └─ is_active: 启用/禁用状态│   │
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
   - **强制校验:** 新增/编辑黑名单时，**Tag Code 为可选项**，后端模型和 Schema 均允许 `tag_code` 为 `None`。

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
    *   **标签约束:** 场景敏感词的标签 (`tag_code`) 为可选字段，允许为空。

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

## 2.7 性能测试 (Performance Testing)
**目标:** 提供轻量级的压力测试工具，帮助管理员在策略变更后验证服务的性能表现（QPS、延迟）及稳定性，确保配置更新不会导致服务不可用或响应过慢。

### 2.7.1 业务流程
1.  **准备阶段 (Setup):** 用户配置目标请求参数（复用输入试验场的逻辑），并执行连通性测试 (Dry Run)。仅当连通性测试通过后，才允许配置压测参数。
2.  **配置阶段 (Configuration):** 用户选择测试模式并设置参数。
    *   **阶梯测试 (Step Load):** 模拟流量逐渐攀升。
    *   **疲劳测试 (Fatigue/Soak):** 模拟长时间恒定压力。
3.  **运行阶段 (Execution):** 后端异步执行压测任务，前端通过轮询获取实时指标并绘制图表。
4.  **报告阶段 (Report):** 测试结束后生成简报，包含总请求数、成功率、RPS 峰值、平均延迟等。

### 2.7.2 详细功能设计

#### 1. 前端界面
*   **目标配置区:** 复用 `InputPlayground` 的表单（App ID, Prompt, 开关等）。增加【连通性测试】按钮。
*   **策略配置区 (Tabs):**
    *   **阶梯测试:**
        *   初始并发数 (Initial Users)
        *   步长 (Step Size: 每轮增加多少用户)
        *   步长间隔 (Step Duration: 每轮持续秒数)
        *   最大并发数 (Max Users)
    *   **疲劳测试:**
        *   并发数 (Concurrency)
        *   持续时间 (Duration)
*   **监控面板:**
    *   **实时指标:** 运行状态、运行时长、实时 RPS、实时平均延迟、错误数。
    *   **可视化图表:** 吞吐量趋势图 (RPS over Time)、延迟趋势图 (Latency over Time)。

#### 2. 后端逻辑
*   **核心模块:** 基于 `asyncio` 和高并发 HTTP 客户端 (`httpx`/`aiohttp`) 实现的轻量级压测执行器。
*   **API 接口:**
    *   `POST /api/v1/performance/dry-run`: 单次执行，验证配置有效性。
    *   `POST /api/v1/performance/start`: 启动压测任务 (Background Task)。
    *   `POST /api/v1/performance/stop`: 强制停止当前任务。
    *   `GET /api/v1/performance/status`: 获取实时统计数据。
    *   `GET /api/v1/performance/history`: 获取历史性能测试列表。
    *   `GET /api/v1/performance/history/{test_id}`: 获取历史性能测试详情。
    *   `DELETE /api/v1/performance/history/{test_id}`: 删除性能测试历史记录（仅 SYSTEM_ADMIN）。

## 2.8 试验场历史记录 (Playground History)
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

## 2.9 性能测试历史 (Performance Test History)
**目标:** 对性能测试结果进行本地持久化，支持回溯和复盘。
**存储策略:** 采用文件系统存储 (File-based Storage)，每次测试生成独立的 JSON 记录文件，而非数据库存储。前端在查看详情时，动态读取 JSON 数据并实时重绘图表。

### 2.9.1 数据结构
在后端根目录 `performance_history/` 下，按测试 ID (UUID) 创建子目录：
*   `meta.json`: 测试元数据（时间、状态、耗时、App ID），用于列表展示。
*   `config.json`: 完整的输入配置和压测参数配置，用于复现。
*   `stats.json`: 最终统计结果（总请求、Avg Latency、Max RPS、错误率）。
*   `history.json`: 完整的时序数据点（Timestamp, RPS, Latency, Users），用于图表回放。

### 2.9.2 功能交互
1.  **自动保存:** 每次性能测试结束（自然完成或手动停止），后端自动将内存中的数据序列化并保存到本地文件。
2.  **历史列表:** 在“性能测试”页面提供入口，展示历史测试记录列表（读取所有 `meta.json`）。
3.  **详情回溯:** 点击某条记录，前端请求该记录的所有 JSON 文件，并在浏览器中重新渲染配置表单和监控图表（只读模式）。
4.  **管理:** 支持删除单条历史记录（删除对应的文件夹）。

## 3. 智能标注与审核系统 (Smart Labeling & Audit System)
**目标:** 解决模型生成的“脏数据”入库问题，引入“人机回环”流程。构建一个中间态（Staging Area），允许审核员对模型预测的敏感词和规则进行人工校对、修正，确认无误后再同步到生产环境。

### 3.1 角色与权限 (Roles & Permissions)
系统引入多角色管理，以支持多人协作审核。

*   **系统管理员 (SYSTEM_ADMIN):**
    *   **权限:** 拥有系统所有权限。
    *   **特权:** 创建/管理用户账号、管理角色和权限、执行数据"入库同步"、管理全局配置、查看审计日志。
*   **场景管理员 (SCENARIO_ADMIN):**
    *   **权限:** 管理被分配的场景，包括场景基本信息、场景关键词、场景策略、试验场、性能测试（根据细粒度权限配置）。
    *   **职责:** 管理特定场景的配置和测试。
*   **审核员 (AUDITOR):**
    *   **权限:** 查看审计日志。
    *   **职责:** 审计系统操作记录。
*   **标注员 (ANNOTATOR):**
    *   **权限:** 仅限访问"智能标注"模块。
    *   **职责:** 认领待审核数据，进行标签/策略修正，标记为"已审核"。不可直接执行入库操作。
    *   **账号来源:** 由管理员创建并分发。

### 3.2 用户管理功能
*   **创建用户:** 管理员可创建用户并分配角色（SYSTEM_ADMIN, SCENARIO_ADMIN, ANNOTATOR, AUDITOR）。
*   **SSO 自动创建:** 通过 SSO 登录的用户会自动在本地创建用户记录。
*   **登录方式:** 支持用户名密码登录和 SSO 单点登录两种方式。
*   **角色分配:** 管理员可为用户分配全局角色或场景级别角色，场景角色需指定 scenario_id。

### 3.3 数据流转状态机
中间态数据 (`staging_global_keywords`, `staging_global_rules`) 拥有以下生命周期：
1.  **PENDING (待审核):** 模型生成后的初始状态。
2.  **CLAIMED (已认领):** 标注员通过批量认领接口领取任务后的状态。记录 `claimed_by` (认领人)、`claimed_at` (认领时间)、`batch_id` (批次ID)。认领超时（30分钟）后自动释放回 PENDING。
3.  **REVIEWED (已审核):** 人工确认或修改后的状态。记录 `annotator` (审核人) 和 `is_modified` (是否修改)。
4.  **SYNCED (已入库):** 数据已被管理员同步到生产环境表 (`GlobalKeywords` 等)。
5.  **IGNORED (已忽略):** 判定为无效数据，不予入库。

### 3.4 核心流程
1.  **认领:** 标注员通过批量认领接口领取一批 `PENDING` 数据（默认50条），状态变为 `CLAIMED`，30分钟超时自动释放。
2.  **标注:** 审核员对 `CLAIMED` 数据进行操作（通过/修改/忽略），支持单条和批量审核。
3.  **审计:** 系统自动记录每条数据的 `annotator` (操作人) 和 `annotated_at` (操作时间)。
4.  **同步 (Sync):** 管理员选择 `REVIEWED` 状态的数据，执行批量入库。
    *   **冲突策略:** 若正式库已存在相同 Key，**覆盖**旧数据。
    *   **留痕:** 入库成功的数据在 Staging 表中保留，状态更为 `SYNCED`。

### 3.5 数据库设计 (Schema Draft)
*   **`users`**: `id`, `user_id` (USAP UserID, 可选), `username`, `hashed_password`, `role` (SYSTEM_ADMIN/SCENARIO_ADMIN/ANNOTATOR/AUDITOR), `display_name`, `email`, `is_active`, `created_at`, `updated_at`, `created_by`.
*   **`roles`**: `id`, `role_code` (唯一), `role_name`, `role_type` (GLOBAL/SCENARIO), `description`, `is_system`, `is_active`.
*   **`permissions`**: `id`, `permission_code` (唯一), `permission_name`, `permission_type` (MENU/ACTION), `scope` (GLOBAL/SCENARIO), `parent_code`, `sort_order`, `description`, `is_active`.
*   **`role_permissions`**: `id`, `role_id`, `permission_id` - 角色-权限关联表。
*   **`user_scenario_roles`**: `id`, `user_id`, `scenario_id` (NULL=全局角色), `role_id`, `created_by` - 用户-场景-角色关联表。
*   **`scenario_admin_permissions`**: `id`, `user_id`, `scenario_id`, `scenario_basic_info`, `scenario_keywords`, `scenario_policies`, `playground`, `performance_test` - 场景管理员细粒度权限。
*   **`audit_logs`**: `id`, `user_id`, `username`, `action`, `resource_type`, `resource_id`, `scenario_id`, `details` (JSON), `ip_address`, `user_agent`, `created_at`.
*   **`staging_global_keywords`**: `id`, `keyword`, `predicted_tag`, `predicted_risk`, `final_tag`, `final_risk`, `status` (PENDING/CLAIMED/REVIEWED/SYNCED/IGNORED), `is_modified`, `claimed_by`, `claimed_at`, `batch_id`, `annotator`, `annotated_at`, `created_at`.
*   **`staging_global_rules`**: `id`, `tag_code`, `predicted_strategy`, `final_strategy`, `extra_condition`, `status` (PENDING/CLAIMED/REVIEWED/SYNCED/IGNORED), `is_modified`, `claimed_by`, `claimed_at`, `batch_id`, `annotator`, `annotated_at`, `created_at`.

### 3.6 SSO 单点登录 (SSO Authentication)
**功能描述:** 支持通过 USAP (统一安全认证平台) 进行单点登录，用户使用 USAP 颁发的 Ticket 换取本地 JWT Token。

*   **功能点:**
    *   **Ticket 登录:** 前端将 USAP 颁发的 Ticket 发送到后端，后端验证 Ticket 后创建或更新本地用户记录，返回 JWT Token。
    *   **用户信息查询:** 从 USAP 获取用户基本信息（姓名、邮箱、部门等），结合本地权限信息返回。
    *   **批量用户查询:** 支持批量从 USAP 获取用户信息，用于列表页面显示。
    *   **健康检查:** 检查 USAP 服务是否可用。
    *   **配置:** 通过 `SSO_ENABLED`、`USAP_BASE_URL`、`USAP_CLIENT_ID`、`USAP_CLIENT_SECRET` 等环境变量配置。

*   **前端页面:** `SSOLogin.tsx` - SSO 登录页面，处理 USAP 回调和 Ticket 交换。

### 3.7 用户管理 (User Management)
**功能描述:** 系统管理员可管理所有用户的角色、状态和权限分配。

*   **功能点:**
    *   **用户列表:** 展示所有用户（仅 SYSTEM_ADMIN 可访问）。
    *   **角色修改:** 修改用户角色（SYSTEM_ADMIN, SCENARIO_ADMIN, ANNOTATOR, AUDITOR），不可修改自己的角色。
    *   **状态管理:** 启用/禁用用户，不可禁用自己。
    *   **用户删除:** 删除用户，不可删除自己。
    *   **角色分配:** 为用户分配场景级别或全局级别的角色（全局角色不需要 scenario_id，场景角色需要）。
    *   **权限查询:** 用户可查询自己的权限列表。

*   **前端页面:** `UsersPage.tsx` - 用户管理页面。

### 3.8 角色与权限管理 (RBAC - Role-Based Access Control)
**功能描述:** 标准 RBAC 模型，支持角色定义、权限配置和角色-权限关联。

#### A. 角色管理 (Roles)
*   **功能点:**
    *   **角色列表:** 展示所有角色及其权限数量。
    *   **创建角色:** 输入角色编码（唯一）、名称、类型（GLOBAL/SCENARIO）、描述。
    *   **更新角色:** 修改角色名称、类型、描述、启用状态。
    *   **删除角色:** 系统预置角色（`is_system=True`）不可删除。
    *   **角色权限配置:** 为角色分配权限列表。

*   **前端页面:** `RolesPage.tsx` - 角色管理页面。

#### B. 权限查询 (Permissions)
*   **功能点:**
    *   **我的权限:** 获取当前用户的完整权限信息（包括角色和所有场景的权限配置）。
    *   **权限检查:** 检查当前用户是否有特定场景的特定权限。
    *   **权限列表:** 获取系统中所有可用权限。

*   **前端组件:** `PermissionGuard.tsx` - 权限守卫组件，用于前端权限控制。

### 3.9 审计日志 (Audit Logs)
**功能描述:** 记录系统中所有关键操作的审计日志，支持多维度查询和统计。

*   **功能点:**
    *   **日志查询:** 支持按用户ID、用户名、操作类型（CREATE/UPDATE/DELETE/VIEW/EXPORT）、资源类型（USER/SCENARIO/KEYWORD/POLICY 等）、场景ID、时间范围筛选。
    *   **日志统计:** 统计符合条件的日志数量。
    *   **自动记录:** 系统在用户管理、角色分配、性能测试等关键操作时自动写入审计日志，记录操作人、IP 地址、User-Agent 等信息。
    *   **权限:** 仅 SYSTEM_ADMIN 和 AUDITOR 可查看审计日志。

*   **数据模型 (`AuditLog`):**
    *   `id`, `user_id`, `username`, `action`, `resource_type`, `resource_id`, `scenario_id`, `details` (JSON), `ip_address`, `user_agent`, `created_at`

*   **前端页面:** `AuditLogs.tsx` - 审计日志查询页面。

### 3.10 我的场景 (My Scenarios)
**功能描述:** 场景管理员 (SCENARIO_ADMIN) 查看自己被分配管理的场景列表。

*   **前端页面:** `MyScenarios.tsx` - 我的场景页面，展示当前用户有权限管理的场景。

## 4. 非功能性需求
*   **架构:** 前后端分离。
    *   **前端:** 建议使用 React/Vue + Ant Design/Element Plus 等组件库构建管理后台。
    *   **后端:** Python (基于现有 SQLAlchemy 模型，建议 FastAPI/Flask)。
*   **性能:** 关键词匹配可能涉及高性能需求，管理端主要关注 CRUD 的响应速度。
*   **扩展性:** `scenario_id` 目前为字符串，未来可能需要一张独立的 `Scenarios` 表来维护场景元数据。

## 5. 接口规划 (API Draft)

**Base URL:** `/api/v1`

### 5.1 认证 (Authentication)
*   `POST /api/v1/login/access-token`: 用户名密码登录，获取 JWT Token

### 5.2 SSO 单点登录 (SSO)
*   `POST /api/v1/sso/login`: SSO 单点登录（使用 USAP Ticket 换取 JWT Token）
*   `GET /api/v1/sso/user-info`: 获取当前 SSO 用户完整信息（从 USAP 获取基本信息 + 本地权限）
*   `POST /api/v1/sso/users/batch`: 批量获取用户信息（从 USAP 批量查询）
*   `GET /api/v1/sso/health`: SSO 服务健康检查（检查 USAP 服务可用性）

### 5.3 用户管理 (Users)
*   `GET /api/v1/users/`: 获取用户列表（仅 SYSTEM_ADMIN）
*   `PUT /api/v1/users/{user_id}/role`: 修改用户角色（仅 SYSTEM_ADMIN）
*   `PATCH /api/v1/users/{user_id}/status`: 启用/禁用用户（仅 SYSTEM_ADMIN）
*   `DELETE /api/v1/users/{user_id}`: 删除用户（仅 SYSTEM_ADMIN）
*   `GET /api/v1/users/{user_id}/roles`: 获取用户所有角色分配
*   `POST /api/v1/users/{user_id}/roles`: 分配角色给用户（仅 SYSTEM_ADMIN）
*   `DELETE /api/v1/users/{user_id}/roles/{assignment_id}`: 移除用户角色分配（仅 SYSTEM_ADMIN）
*   `GET /api/v1/users/me/permissions`: 获取当前用户权限

### 5.4 角色管理 (Roles)
*   `GET /api/v1/roles/`: 获取角色列表
*   `POST /api/v1/roles/`: 创建角色（仅 SYSTEM_ADMIN）
*   `PUT /api/v1/roles/{role_id}`: 更新角色（仅 SYSTEM_ADMIN）
*   `DELETE /api/v1/roles/{role_id}`: 删除角色（系统预置角色不可删，仅 SYSTEM_ADMIN）
*   `GET /api/v1/roles/{role_id}/permissions`: 获取角色权限
*   `PUT /api/v1/roles/{role_id}/permissions`: 更新角色权限（仅 SYSTEM_ADMIN）
*   `GET /api/v1/roles/permissions/all`: 获取所有权限列表

### 5.5 权限查询 (Permissions)
*   `GET /api/v1/permissions/me`: 获取当前用户完整权限信息
*   `POST /api/v1/permissions/check`: 检查当前用户是否有特定权限（传入 scenario_id 和 permission）

### 5.6 审计日志 (Audit Logs)
*   `GET /api/v1/audit-logs/`: 查询审计日志（仅 SYSTEM_ADMIN 和 AUDITOR，支持按用户、操作类型、资源类型、场景、时间范围筛选）
*   `GET /api/v1/audit-logs/count`: 统计审计日志数量（仅 SYSTEM_ADMIN 和 AUDITOR）

### 5.7 元数据标签 (Meta Tags)
*   `GET /api/v1/tags/`: 获取标签树/列表
*   `POST /api/v1/tags/`: 创建标签
*   `PUT /api/v1/tags/{id}`: 更新标签
*   `DELETE /api/v1/tags/{id}`: 删除标签

### 5.8 全局关键词 (Global Keywords)
*   `GET /api/v1/keywords/global/`: 搜索全局关键词
*   `POST /api/v1/keywords/global/`: 添加全局关键词
*   `PUT /api/v1/keywords/global/{id}`: 更新全局关键词
*   `DELETE /api/v1/keywords/global/{id}`: 删除全局关键词

### 5.9 场景关键词 (Scenario Keywords)
*   `GET /api/v1/keywords/scenario/{scenarioId}`: 获取场景关键词
*   `POST /api/v1/keywords/scenario/{scenarioId}`: 添加场景关键词
*   `PUT /api/v1/keywords/scenario/{scenarioId}/{id}`: 更新场景关键词
*   `DELETE /api/v1/keywords/scenario/{scenarioId}/{id}`: 删除场景关键词

### 5.10 规则策略 (Rule Policies)
*   `GET /api/v1/policies/scenario/{scenarioId}`: 获取场景策略
*   `POST /api/v1/policies/scenario/{scenarioId}`: 配置场景规则
*   `PUT /api/v1/policies/scenario/{scenarioId}/{id}`: 更新场景规则
*   `DELETE /api/v1/policies/scenario/{scenarioId}/{id}`: 删除场景规则
*   `GET /api/v1/policies/defaults/`: 获取全局默认规则
*   `POST /api/v1/policies/defaults/`: 配置全局默认规则
*   `PUT /api/v1/policies/defaults/{id}`: 更新全局默认规则
*   `DELETE /api/v1/policies/defaults/{id}`: 删除全局默认规则

### 5.11 场景/应用管理 (Apps/Scenarios)
*   `GET /api/v1/apps/`: 获取场景列表
*   `POST /api/v1/apps/`: 创建场景
*   `PUT /api/v1/apps/{id}`: 更新场景
*   `DELETE /api/v1/apps/{id}`: 删除场景

### 5.12 试验场 (Playground)
*   `POST /api/v1/playground/input`: 运行输入测试
*   `GET /api/v1/playground/history`: 获取试验场历史记录

### 5.13 性能测试 (Performance)
*   `POST /api/v1/performance/dry-run`: 连通性测试（单次请求）
*   `POST /api/v1/performance/start`: 启动性能测试（后台运行）
*   `POST /api/v1/performance/stop`: 停止当前性能测试
*   `GET /api/v1/performance/status`: 获取运行中测试的实时统计
*   `GET /api/v1/performance/history`: 获取历史性能测试列表
*   `GET /api/v1/performance/history/{test_id}`: 获取历史性能测试详情
*   `DELETE /api/v1/performance/history/{test_id}`: 删除性能测试历史记录（仅 SYSTEM_ADMIN）

### 5.14 智能标注/Staging (Staging)
*   `GET /api/v1/staging/keywords`: 获取智能标注关键词列表
*   `PATCH /api/v1/staging/keywords/{keyword_id}`: 审核关键词
*   `POST /api/v1/staging/keywords/batch-review`: 批量审核关键词
*   `POST /api/v1/staging/keywords/sync`: 同步关键词到正式库（仅 SYSTEM_ADMIN）
*   `POST /api/v1/staging/keywords/import-mock`: 导入模拟关键词数据
*   `DELETE /api/v1/staging/keywords/{keyword_id}`: 删除 Staging 关键词
*   `GET /api/v1/staging/rules`: 获取智能标注规则列表
*   `PATCH /api/v1/staging/rules/{rule_id}`: 审核规则
*   `POST /api/v1/staging/rules/batch-review`: 批量审核规则
*   `POST /api/v1/staging/rules/sync`: 同步规则到正式库（仅 SYSTEM_ADMIN）
*   `POST /api/v1/staging/rules/import-mock`: 导入模拟规则数据
*   `DELETE /api/v1/staging/rules/{rule_id}`: 删除 Staging 规则
*   `POST /api/v1/staging/claim`: 批量认领任务（ANNOTATOR 和 SYSTEM_ADMIN）
*   `POST /api/v1/staging/release-expired`: 释放超时的认领任务
*   `GET /api/v1/staging/stats/annotators`: 获取标注员统计信息
*   `GET /api/v1/staging/my-tasks/stats`: 获取当前用户的任务统计
*   `GET /api/v1/staging/overview`: 获取任务总览统计
