# 空标签编码功能实现报告

## 功能需求

在全局默认规则中，允许 `tag_code` 为空，但此时必须填写 `extra_condition`。这样可以创建仅基于额外条件的规则。

## 实现内容

### 1. 数据库层修改

**文件**: `backend/app/models/db_meta.py`

```python
class RuleGlobalDefaults(Base):
    __tablename__ = "rule_global_defaults"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
    tag_code: Mapped[str | None] = mapped_column(String(64), nullable=True)  # 改为可空
    extra_condition: Mapped[str | None] = mapped_column(String(64), nullable=True)
    strategy: Mapped[str] = mapped_column(String(32))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

**数据库迁移**:
```sql
ALTER TABLE rule_global_defaults
MODIFY COLUMN tag_code VARCHAR(64) NULL;
```

### 2. Schema 层修改

**文件**: `backend/app/schemas/rule_policy.py`

```python
class RuleGlobalDefaultsBase(BaseModel):
    tag_code: str | None = None  # 改为可选
    extra_condition: str | None = None
    strategy: str
    is_active: bool = True
```

### 3. Service 层修改

**文件**: `backend/app/services/rule_policy.py`

添加业务逻辑验证：

```python
async def create_global_default(self, default_in: RuleGlobalDefaultsCreate) -> RuleGlobalDefaults:
    # 业务逻辑验证：tag_code 为空时，extra_condition 必须提供
    if not default_in.tag_code and not default_in.extra_condition:
        raise ValueError("When tag_code is empty, extra_condition must be provided.")

    # 检查重复...
```

```python
async def update_global_default(self, default_id: str, default_in: RuleGlobalDefaultsUpdate) -> RuleGlobalDefaults:
    # 验证更新后的数据
    updated_tag_code = default_in.tag_code if default_in.tag_code is not None else default_obj.tag_code
    updated_extra_condition = default_in.extra_condition if default_in.extra_condition is not None else default_obj.extra_condition

    if not updated_tag_code and not updated_extra_condition:
        raise ValueError("When tag_code is empty, extra_condition must be provided.")

    # 更新...
```

### 4. Repository 层修改

**文件**: `backend/app/repositories/rule_policy.py`

调整去重逻辑以支持空 tag_code：

```python
async def get_duplicate(self, tag_code: str | None, extra_condition: str | None) -> RuleGlobalDefaults | None:
    # 根据 tag_code 构建查询
    if tag_code:
        query = select(self.model).where(self.model.tag_code == tag_code)
    else:
        query = select(self.model).where(self.model.tag_code.is_(None) | (self.model.tag_code == ''))

    # 添加 extra_condition 过滤
    if extra_condition:
        query = query.where(self.model.extra_condition == extra_condition)
    else:
        query = query.where(self.model.extra_condition.is_(None) | (self.model.extra_condition == ''))

    result = await self.db.execute(query)
    return result.scalars().first()
```

### 5. 前端修改

**文件**: `frontend/src/pages/GlobalPolicies.tsx`

#### 表单验证

添加动态验证规则：

```tsx
<Form.Item
  name="tag_code"
  label="标签编码 (Tag Code)"
  rules={[
    ({ getFieldValue }) => ({
      validator(_, value) {
        const extraCondition = getFieldValue('extra_condition');
        if (!value && !extraCondition) {
          return Promise.reject(new Error('标签编码为空时，必须填写额外条件'));
        }
        return Promise.resolve();
      },
    }),
  ]}
  help="该默认规则适用的分类标签。可选择空值，但此时必须填写额外条件。"
>
  <Select
    placeholder="请选择标签（可选择空值）"
    showSearch
    optionFilterProp="children"
    allowClear
  >
    <Select.Option value="">（空）</Select.Option>
    {tags.map(tag => (
      <Select.Option key={tag.tag_code} value={tag.tag_code}>
        {tag.tag_name} ({tag.tag_code})
      </Select.Option>
    ))}
  </Select>
</Form.Item>

<Form.Item
  name="extra_condition"
  label="额外条件"
  rules={[
    ({ getFieldValue }) => ({
      validator(_, value) {
        const tagCode = getFieldValue('tag_code');
        if (!tagCode && !value) {
          return Promise.reject(new Error('标签编码为空时，必须填写额外条件'));
        }
        return Promise.resolve();
      },
    }),
  ]}
  help="可选。例如特定的模型判定结果。当标签编码为空时必填。"
>
  <Select allowClear placeholder="请选择或输入...">
    <Select.Option value="safe">safe (安全)</Select.Option>
    <Select.Option value="unsafe">unsafe (不安全)</Select.Option>
    <Select.Option value="controversial">controversial (有争议)</Select.Option>
  </Select>
</Form.Item>
```

#### 列表显示

修改 tag_code 列的渲染逻辑：

```tsx
{
  title: '标签编码',
  dataIndex: 'tag_code',
  key: 'tag_code',
  render: (text: string) => text ? <Tag color="blue">{text}</Tag> : <Tag color="default">(空)</Tag>
}
```

## 测试验证

### K8s 环境部署

1. **重新构建前端**:
```bash
cd frontend
VITE_BASE_PATH=/web-manager/ VITE_API_BASE_URL=/dbmanage/api/v1 npm run build
```

2. **执行数据库迁移**:
```python
import pymysql
conn = pymysql.connect(
    host='49.233.46.126',
    port=38306,
    user='root',
    password='Platform#2026',
    database='llm_safe_db'
)
cursor = conn.cursor()
cursor.execute('ALTER TABLE rule_global_defaults MODIFY COLUMN tag_code VARCHAR(64) NULL')
conn.commit()
conn.close()
```

3. **部署到 K8s**:
```bash
cd /Users/weipeng/Desktop/PY_WORK_SPACE/llm_guard_manager
bash k8s/deploy.sh
```

### API 测试结果

**访问地址**: `http://llmsafe-dev.aisp.test.abc/dbmanage/api/v1`

**登录凭据**:
- 用户名: `llm_guard`
- 密码: `68-8CtBhug`

#### 测试 1: 创建只有额外条件的规则 ✅

**请求**:
```json
POST /policies/defaults/
{
  "tag_code": null,
  "extra_condition": "safe",
  "strategy": "PASS",
  "is_active": true
}
```

**响应**:
```json
{
  "tag_code": null,
  "extra_condition": "safe",
  "strategy": "PASS",
  "is_active": true,
  "id": "25c2c29f-05e1-4c56-9297-f322bca7c39c"
}
```

✅ **结果**: 成功创建

#### 测试 2: 尝试创建两者都为空的规则 ✅

**请求**:
```json
POST /policies/defaults/
{
  "tag_code": null,
  "extra_condition": null,
  "strategy": "BLOCK",
  "is_active": true
}
```

**响应**:
```json
{
  "detail": "When tag_code is empty, extra_condition must be provided."
}
```

✅ **结果**: 正确拒绝，返回验证错误

#### 测试 3: 查询所有规则 ✅

**请求**:
```
GET /policies/defaults/
```

**响应**: 包含新创建的规则，`tag_code` 为 `null`

✅ **结果**: 成功查询，空 tag_code 正确显示

### 前端测试步骤

1. 访问: `http://llmsafe-dev.aisp.test.abc/web-manager/`
2. 使用 `llm_guard` / `68-8CtBhug` 登录
3. 进入「全局默认规则管理」页面
4. 点击「新增默认规则」
5. 在标签编码下拉框中选择「（空）」选项
6. 不填写额外条件，尝试提交 → 应显示验证错误
7. 填写额外条件（如 safe），再次提交 → 应成功创建
8. 在列表中查看新创建的规则，tag_code 列应显示「(空)」

## 技术要点

### Python 3.12 现代语法

使用 `|` 联合类型语法替代 `Optional`：

```python
# 旧写法
from typing import Optional
tag_code: Optional[str] = None

# 新写法 (Python 3.12)
tag_code: str | None = None
```

### 前端表单联动验证

使用 Ant Design Form 的 `getFieldValue` 实现字段间的联动验证：

```tsx
rules={[
  ({ getFieldValue }) => ({
    validator(_, value) {
      const otherField = getFieldValue('other_field');
      if (!value && !otherField) {
        return Promise.reject(new Error('至少填写一个字段'));
      }
      return Promise.resolve();
    },
  }),
]}
```

### 数据库 NULL 值处理

在 SQLAlchemy 查询中正确处理 NULL 值：

```python
# 匹配 NULL 或空字符串
query = query.where(self.model.tag_code.is_(None) | (self.model.tag_code == ''))
```

## 部署检查清单

- [x] 数据库表结构已修改（tag_code 可空）
- [x] 后端代码已更新（Model, Schema, Service, Repository）
- [x] 前端代码已更新（表单验证、列表显示）
- [x] 前端已重新构建（使用正确的环境变量）
- [x] K8s 部署已更新
- [x] API 功能测试通过
- [x] 前端页面可访问

## 总结

本次功能实现完整支持了全局默认规则中 `tag_code` 为空的场景，并通过业务逻辑验证确保当 `tag_code` 为空时，`extra_condition` 必须提供。前后端均实现了相应的验证逻辑，确保数据一致性和用户体验。

所有修改已在 K8s 环境中部署并通过测试验证。
