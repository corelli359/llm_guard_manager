# RBAC 系统开发计划

## 一、项目概述

基于 RBAC_REQUIREMENTS.md 的需求，为 LLM Guard Manager 实现完整的角色权限管理系统。

### 核心目标
1. 实现 4 种角色：SYSTEM_ADMIN、SCENARIO_ADMIN、ANNOTATOR、AUDITOR
2. 支持场景级别的权限隔离
3. 细粒度权限控制（场景管理员的 5 种权限项）
4. 完整的审计日志系统
5. 支持双版本架构（V1 独立版本 + V2 门户集成版本）

### 技术栈
- 后端：FastAPI + SQLAlchemy 2.0 (async) + MySQL
- 前端：React 18 + TypeScript + Ant Design 5
- 认证：JWT (V1) / SSO (V2)

---

## 二、现有架构分析

### 2.1 后端分层架构
- **Model 层**: `/backend/app/models/db_meta.py` - SQLAlchemy ORM 定义
- **Repository 层**: `/backend/app/repositories/` - 继承 BaseRepository，提供 CRUD
- **Service 层**: `/backend/app/services/` - 业务逻辑和验证
- **API 层**: `/backend/app/api/v1/endpoints/` - FastAPI 路由端点

### 2.2 现有认证系统
- **JWT 实现**: `/backend/app/core/security.py` - Token 生成和密码验证
- **依赖注入**: `/backend/app/api/v1/deps.py` - `get_current_user` 返回用户名
- **登录 API**: `/backend/app/api/v1/endpoints/auth.py` - 支持硬编码管理员和数据库用户
- **用户模型**: 已有 User 表，包含 username, hashed_password, role, is_active

### 2.3 前端认证
- **登录页面**: `/frontend/src/pages/LoginPage.tsx`
- **API 客户端**: `/frontend/src/api.ts` - Axios 拦截器自动添加 Bearer Token
- **路由保护**: `/frontend/src/App.tsx` - AuthLayout 检查 localStorage 中的 token
- **权限控制**: 基于 localStorage 的 user_role 控制菜单显示

---

## 三、数据库设计

### 3.1 需要扩展的表

#### users 表（扩展现有表）
```sql
ALTER TABLE users
ADD COLUMN display_name VARCHAR(128),
ADD COLUMN email VARCHAR(128),
ADD COLUMN created_by VARCHAR(36),
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- 更新 role 字段支持新角色
-- 现有: ADMIN, AUDITOR
-- 新增: SYSTEM_ADMIN, SCENARIO_ADMIN, ANNOTATOR
```

### 3.2 新增表

#### user_scenario_assignments（用户场景关联表）
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

#### scenario_admin_permissions（场景管理员权限配置表）
```sql
CREATE TABLE scenario_admin_permissions (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    scenario_id VARCHAR(64) NOT NULL,

    -- 5 种细粒度权限
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

#### audit_logs（审计日志表）
```sql
CREATE TABLE audit_logs (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    username VARCHAR(64) NOT NULL,
    action VARCHAR(64) NOT NULL,        -- CREATE, UPDATE, DELETE, VIEW, EXPORT
    resource_type VARCHAR(64) NOT NULL, -- USER, SCENARIO, KEYWORD, POLICY, etc.
    resource_id VARCHAR(64),
    scenario_id VARCHAR(64),
    details JSON,
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

## 四、实施阶段规划

### 阶段 1：数据库和 Model 层（第 1 天）

#### 1.1 数据库迁移脚本
**文件**: `/backend/migrations/add_rbac_tables.sql`

**任务**:
1. 创建迁移脚本，包含：
   - ALTER TABLE users 添加新字段
   - CREATE TABLE user_scenario_assignments
   - CREATE TABLE scenario_admin_permissions
   - CREATE TABLE audit_logs
2. 编写回滚脚本
3. 测试迁移脚本

#### 1.2 扩展 ORM Model
**文件**: `/backend/app/models/db_meta.py`

**任务**:
1. 扩展 User 模型：
   ```python
   class User(Base):
       __tablename__ = "users"

       id: Mapped[str] = mapped_column(CHAR(36), primary_key=True)
       username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
       hashed_password: Mapped[str] = mapped_column(String(128))
       role: Mapped[str] = mapped_column(String(32), default="ANNOTATOR")
       display_name: Mapped[Optional[str]] = mapped_column(String(128))
       email: Mapped[Optional[str]] = mapped_column(String(128))
       is_active: Mapped[bool] = mapped_column(Boolean, default=True)
       created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
       updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
       created_by: Mapped[Optional[str]] = mapped_column(String(36))
   ```

2. 新增 UserScenarioAssignment 模型
3. 新增 ScenarioAdminPermission 模型
4. 新增 AuditLog 模型

#### 1.3 Repository 层
**新增文件**:
- `/backend/app/repositories/user_scenario_assignment.py`
- `/backend/app/repositories/scenario_admin_permission.py`
- `/backend/app/repositories/audit_log.py`

**任务**:
1. 继承 BaseRepository
2. 实现特定查询方法：
   - `get_user_scenarios(user_id)` - 获取用户的所有场景
   - `get_scenario_users(scenario_id)` - 获取场景的所有用户
   - `get_user_permissions(user_id, scenario_id)` - 获取用户在特定场景的权限
   - `search_audit_logs(filters)` - 审计日志查询

---

### 阶段 2：权限服务和装饰器（第 2-3 天）

#### 2.1 权限检查服务
**新增文件**: `/backend/app/services/permission.py`

**核心功能**:
```python
class PermissionService:
    async def check_role(self, user_id: str, required_role: str) -> bool:
        """检查用户是否拥有指定角色"""

    async def check_scenario_access(self, user_id: str, scenario_id: str) -> bool:
        """检查用户是否有权访问指定场景"""

    async def check_scenario_permission(
        self, user_id: str, scenario_id: str, permission: str
    ) -> bool:
        """检查用户在指定场景是否有特定权限"""

    async def get_user_permissions(self, user_id: str) -> Dict:
        """获取用户的完整权限信息"""
```

#### 2.2 审计日志服务
**新增文件**: `/backend/app/services/audit.py`

**核心功能**:
```python
class AuditService:
    async def log(
        self,
        user_id: str,
        username: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        scenario_id: Optional[str] = None,
        details: Optional[Dict] = None,
        request: Optional[Request] = None
    ):
        """记录审计日志"""
```

#### 2.3 权限装饰器和依赖
**修改文件**: `/backend/app/api/v1/deps.py`

**新增依赖**:
```python
# 现有: get_current_user -> 返回 username (str)

# 新增: get_current_user_full -> 返回完整用户对象
async def get_current_user_full(
    token: str = Depends(reusable_oauth2),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取完整的用户对象"""

# 新增: 角色检查依赖
def require_role(allowed_roles: List[str]):
    async def role_checker(
        current_user: User = Depends(get_current_user_full)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# 新增: 场景权限检查依赖
def require_scenario_permission(permission: str):
    async def permission_checker(
        scenario_id: str,
        current_user: User = Depends(get_current_user_full),
        db: AsyncSession = Depends(get_db)
    ):
        perm_service = PermissionService(db)
        has_perm = await perm_service.check_scenario_permission(
            current_user.id, scenario_id, permission
        )
        if not has_perm:
            raise HTTPException(status_code=403, detail=f"Missing permission: {permission}")
        return current_user
    return permission_checker
```

### 阶段 3：用户管理和权限 API（第 3-4 天）

#### 3.1 扩展用户管理 API
**修改文件**: `/backend/app/api/v1/endpoints/users.py`

**新增端点**:
```python
# 1. 分配场景给用户
@router.post("/{user_id}/scenarios")
async def assign_scenario(
    user_id: str,
    assignment: UserScenarioAssignmentCreate,
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"])),
    db: AsyncSession = Depends(get_db)
):
    """系统管理员分配场景给用户"""

# 2. 配置场景管理员权限
@router.put("/{user_id}/scenarios/{scenario_id}/permissions")
async def configure_permissions(
    user_id: str,
    scenario_id: str,
    permissions: ScenarioPermissionsUpdate,
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"])),
    db: AsyncSession = Depends(get_db)
):
    """系统管理员配置场景管理员的细粒度权限"""

# 3. 获取用户的场景列表
@router.get("/{user_id}/scenarios")
async def get_user_scenarios(
    user_id: str,
    current_user: User = Depends(get_current_user_full),
    db: AsyncSession = Depends(get_db)
):
    """获取用户被分配的所有场景"""

# 4. 移除用户的场景分配
@router.delete("/{user_id}/scenarios/{scenario_id}")
async def remove_scenario_assignment(
    user_id: str,
    scenario_id: str,
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"])),
    db: AsyncSession = Depends(get_db)
):
    """系统管理员移除用户的场景分配"""
```

#### 3.2 权限查询 API
**新增文件**: `/backend/app/api/v1/endpoints/permissions.py`

```python
# 1. 获取当前用户权限
@router.get("/me")
async def get_my_permissions(
    current_user: User = Depends(get_current_user_full),
    db: AsyncSession = Depends(get_db)
):
    """返回当前用户的完整权限信息"""
    # 返回格式参考 RBAC_REQUIREMENTS.md 5.2.1

# 2. 检查特定权限
@router.get("/check")
async def check_permission(
    scenario_id: str,
    permission: str,
    current_user: User = Depends(get_current_user_full),
    db: AsyncSession = Depends(get_db)
):
    """检查当前用户是否有特定权限"""
```

#### 3.3 审计日志 API
**新增文件**: `/backend/app/api/v1/endpoints/audit_logs.py`

```python
@router.get("/")
async def query_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    scenario_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role(["SYSTEM_ADMIN", "AUDITOR"])),
    db: AsyncSession = Depends(get_db)
):
    """查询审计日志（仅系统管理员和审计员）"""
```

#### 3.4 注册新路由
**修改文件**: `/backend/app/api/v1/api.py`

```python
from app.api.v1.endpoints import permissions, audit_logs

api_router.include_router(permissions.router, prefix="/permissions", tags=["permissions"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["audit-logs"])
```

---

### 阶段 4：现有 API 权限改造（第 4-5 天）

#### 4.1 全局配置 API 权限控制
**需要修改的文件**:
- `/backend/app/api/v1/endpoints/meta_tags.py`
- `/backend/app/api/v1/endpoints/global_keywords.py`
- `/backend/app/api/v1/endpoints/rule_policy.py` (全局默认规则部分)

**改造方案**:
```python
# 示例：meta_tags.py
@router.post("/", response_model=MetaTagsResponse)
async def create_tag(
    tag_in: MetaTagsCreate,
    current_user: User = Depends(require_role(["SYSTEM_ADMIN"])),
    db: AsyncSession = Depends(get_db)
):
    """创建标签（仅系统管理员）"""
    # 添加审计日志
    audit_service = AuditService(db)
    await audit_service.log(
        user_id=current_user.id,
        username=current_user.username,
        action="CREATE",
        resource_type="META_TAG",
        details={"tag_code": tag_in.tag_code}
    )
    # 原有逻辑...
```

#### 4.2 场景配置 API 权限控制
**需要修改的文件**:
- `/backend/app/api/v1/endpoints/scenarios.py`
- `/backend/app/api/v1/endpoints/scenario_keywords.py`
- `/backend/app/api/v1/endpoints/rule_policy.py` (场景策略部分)

**改造方案**:
```python
# 示例：scenario_keywords.py
@router.post("/{scenario_id}/keywords")
async def create_scenario_keyword(
    scenario_id: str,
    keyword_in: ScenarioKeywordsCreate,
    current_user: User = Depends(get_current_user_full),
    db: AsyncSession = Depends(get_db)
):
    """创建场景敏感词"""
    # 权限检查
    perm_service = PermissionService(db)

    # SYSTEM_ADMIN 有全部权限
    if current_user.role == "SYSTEM_ADMIN":
        pass
    # SCENARIO_ADMIN 需要检查场景权限
    elif current_user.role == "SCENARIO_ADMIN":
        has_perm = await perm_service.check_scenario_permission(
            current_user.id, scenario_id, "scenario_keywords"
        )
        if not has_perm:
            raise HTTPException(status_code=403, detail="No permission for this scenario")
    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # 审计日志
    # 原有逻辑...
```

#### 4.3 智能标注 API 权限控制
**需要修改的文件**:
- `/backend/app/api/v1/endpoints/staging.py`

**改造方案**:
```python
# 列表查询：根据角色过滤数据
@router.get("/keywords")
async def list_staging_keywords(
    status: Optional[str] = None,
    scenario_id: Optional[str] = None,
    current_user: User = Depends(get_current_user_full),
    db: AsyncSession = Depends(get_db)
):
    """查询标注任务"""
    stmt = select(StagingGlobalKeywords)

    # SYSTEM_ADMIN: 查看所有
    if current_user.role == "SYSTEM_ADMIN":
        pass
    # SCENARIO_ADMIN: 只能看自己管理的场景
    elif current_user.role == "SCENARIO_ADMIN":
        user_scenarios = await get_user_scenario_ids(current_user.id, db)
        if scenario_id:
            if scenario_id not in user_scenarios:
                raise HTTPException(status_code=403)
            stmt = stmt.where(StagingGlobalKeywords.scenario_id == scenario_id)
        else:
            stmt = stmt.where(StagingGlobalKeywords.scenario_id.in_(user_scenarios))
    # ANNOTATOR: 只能看分配给自己的场景
    elif current_user.role == "ANNOTATOR":
        user_scenarios = await get_user_scenario_ids(current_user.id, db)
        if scenario_id:
            if scenario_id not in user_scenarios:
                raise HTTPException(status_code=403)
            stmt = stmt.where(StagingGlobalKeywords.scenario_id == scenario_id)
        else:
            stmt = stmt.where(StagingGlobalKeywords.scenario_id.in_(user_scenarios))
        # 进一步过滤：只看自己的任务
        if status in ["REVIEWED", "IGNORED"]:
            stmt = stmt.where(StagingGlobalKeywords.annotator == current_user.username)
    # AUDITOR: 只读权限
    elif current_user.role == "AUDITOR":
        pass

    # 执行查询...
```

#### 4.4 测试功能权限控制
**需要修改的文件**:
- `/backend/app/api/v1/endpoints/playground.py`
- `/backend/app/api/v1/endpoints/performance.py`

**改造方案**:
```python
# playground.py
@router.post("/input")
async def run_input_check(
    payload: PlaygroundInputRequest,
    current_user: User = Depends(get_current_user_full),
    db: AsyncSession = Depends(get_db)
):
    """输入测试"""
    # 权限检查
    if current_user.role == "SYSTEM_ADMIN":
        pass
    elif current_user.role == "SCENARIO_ADMIN":
        # 检查是否有 playground 权限
        perm_service = PermissionService(db)
        has_perm = await perm_service.check_scenario_permission(
            current_user.id, payload.app_id, "playground"
        )
        if not has_perm:
            raise HTTPException(status_code=403)
    else:
        raise HTTPException(status_code=403, detail="No access to playground")

    # 原有逻辑...
```

---

### 阶段 5：前端权限控制（第 5-7 天）

#### 5.1 权限上下文和 Hooks
**新增文件**: `/frontend/src/contexts/PermissionContext.tsx`

```typescript
interface PermissionContextType {
  userRole: string;
  userPermissions: UserPermissions;
  loading: boolean;
  refreshPermissions: () => Promise<void>;
  hasRole: (roles: string[]) => boolean;
  hasScenarioAccess: (scenarioId: string) => boolean;
  hasScenarioPermission: (scenarioId: string, permission: string) => boolean;
}

export const PermissionProvider: React.FC<{children: React.ReactNode}> = ({children}) => {
  const [userPermissions, setUserPermissions] = useState<UserPermissions | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPermissions();
  }, []);

  const fetchPermissions = async () => {
    try {
      const response = await api.get('/permissions/me');
      setUserPermissions(response.data);
    } catch (error) {
      console.error('Failed to fetch permissions', error);
    } finally {
      setLoading(false);
    }
  };

  // 实现权限检查方法...
};
```

**新增文件**: `/frontend/src/hooks/usePermission.ts`

```typescript
export const usePermission = () => {
  const context = useContext(PermissionContext);
  if (!context) {
    throw new Error('usePermission must be used within PermissionProvider');
  }
  return context;
};
```

#### 5.2 修改 API 客户端
**修改文件**: `/frontend/src/api.ts`

```typescript
// 添加响应拦截器处理 401/403
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token 过期，清除本地存储并跳转登录
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_role');
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      message.error('您没有权限执行此操作');
    }
    return Promise.reject(error);
  }
);

// 新增权限相关 API
export const permissionsApi = {
  getMyPermissions: () => api.get('/permissions/me'),
  checkPermission: (scenarioId: string, permission: string) =>
    api.get('/permissions/check', { params: { scenario_id: scenarioId, permission } }),
};

// 新增用户场景分配 API
export const userScenariosApi = {
  assignScenario: (userId: string, data: any) =>
    api.post(`/users/${userId}/scenarios`, data),
  configurePermissions: (userId: string, scenarioId: string, permissions: any) =>
    api.put(`/users/${userId}/scenarios/${scenarioId}/permissions`, permissions),
  getUserScenarios: (userId: string) =>
    api.get(`/users/${userId}/scenarios`),
  removeScenarioAssignment: (userId: string, scenarioId: string) =>
    api.delete(`/users/${userId}/scenarios/${scenarioId}`),
};

// 新增审计日志 API
export const auditLogsApi = {
  queryLogs: (params: any) => api.get('/audit-logs', { params }),
};
```

#### 5.3 修改主应用路由
**修改文件**: `/frontend/src/App.tsx`

```typescript
function App() {
  return (
    <PermissionProvider>
      <Router basename={import.meta.env.BASE_URL}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<AuthLayout />}>
            <Route path="/*" element={<AppLayout />} />
          </Route>
        </Routes>
      </Router>
    </PermissionProvider>
  );
}

// AppLayout 中根据权限动态生成菜单
const AppLayout: React.FC = () => {
  const { userRole, userPermissions, hasRole } = usePermission();

  const menuItems = useMemo(() => {
    const items: MenuProps['items'] = [];

    // 智能标注 - 所有角色
    items.push({
      key: '/smart-labeling',
      icon: <AuditOutlined />,
      label: <Link to="/smart-labeling">智能标注</Link>,
    });

    // 标注统计 - SYSTEM_ADMIN, SCENARIO_ADMIN, AUDITOR
    if (hasRole(['SYSTEM_ADMIN', 'SCENARIO_ADMIN', 'AUDITOR'])) {
      items.push({
        key: '/annotator-stats',
        icon: <BarChartOutlined />,
        label: <Link to="/annotator-stats">标注统计</Link>,
      });
    }

    // 系统管理 - 仅 SYSTEM_ADMIN
    if (hasRole(['SYSTEM_ADMIN'])) {
      items.push({
        type: 'group',
        label: '系统管理',
        children: [
          {
            key: '/users',
            icon: <UserOutlined />,
            label: <Link to="/users">用户管理</Link>,
          },
          {
            key: '/audit-logs',
            icon: <FileTextOutlined />,
            label: <Link to="/audit-logs">审计日志</Link>,
          },
        ],
      });

      // 全局配置组...
      // 测试工具组...
    }

    // 场景管理员的场景列表
    if (hasRole(['SCENARIO_ADMIN'])) {
      const myScenarios = userPermissions?.scenarios || [];
      if (myScenarios.length > 0) {
        items.push({
          type: 'group',
          label: '我的场景',
          children: myScenarios.map(s => ({
            key: `/scenarios/${s.scenario_id}`,
            label: <Link to={`/scenarios/${s.scenario_id}`}>{s.scenario_name}</Link>,
          })),
        });
      }
    }

    return items;
  }, [userRole, userPermissions]);

  // 渲染菜单...
};
```

#### 5.4 用户管理页面增强
**修改文件**: `/frontend/src/pages/Users.tsx`

**新增功能**:
1. 用户列表显示角色标签
2. 创建用户时选择角色（SYSTEM_ADMIN, SCENARIO_ADMIN, ANNOTATOR, AUDITOR）
3. 为用户分配场景（弹窗选择场景和角色）
4. 配置场景管理员权限（5 个权限开关）
5. 查看用户的场景列表

**UI 组件**:
- `UserListTable` - 用户列表表格
- `CreateUserModal` - 创建用户弹窗
- `AssignScenarioModal` - 分配场景弹窗
- `ConfigurePermissionsModal` - 配置权限弹窗
- `UserScenariosDrawer` - 用户场景抽屉

#### 5.5 审计日志页面
**新增文件**: `/frontend/src/pages/AuditLogs.tsx`

**功能**:
1. 审计日志列表（表格）
2. 高级筛选：
   - 用户筛选
   - 操作类型筛选（CREATE, UPDATE, DELETE, VIEW, EXPORT）
   - 资源类型筛选（USER, SCENARIO, KEYWORD, POLICY, etc.）
   - 场景筛选
   - 时间范围筛选
3. 查看详情（JSON 展示）
4. 导出功能

#### 5.6 场景管理员视图
**新增文件**: `/frontend/src/pages/MyScenarios.tsx`

**功能**:
1. 显示分配给当前用户的场景列表
2. 每个场景显示权限标签（哪些权限可用）
3. 点击场景进入场景详情页
4. 根据权限显示/隐藏操作按钮

#### 5.7 权限控制组件
**新增文件**: `/frontend/src/components/PermissionGuard.tsx`

```typescript
interface PermissionGuardProps {
  roles?: string[];
  scenarioId?: string;
  permission?: string;
  fallback?: React.ReactNode;
  children: React.ReactNode;
}

export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  roles,
  scenarioId,
  permission,
  fallback = null,
  children,
}) => {
  const { hasRole, hasScenarioPermission } = usePermission();

  // 角色检查
  if (roles && !hasRole(roles)) {
    return <>{fallback}</>;
  }

  // 场景权限检查
  if (scenarioId && permission && !hasScenarioPermission(scenarioId, permission)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};
```

**使用示例**:
```typescript
<PermissionGuard roles={['SYSTEM_ADMIN', 'SCENARIO_ADMIN']}>
  <Button onClick={handleCreate}>新增敏感词</Button>
</PermissionGuard>

<PermissionGuard scenarioId={scenarioId} permission="scenario_keywords">
  <Button onClick={handleEdit}>编辑</Button>
</PermissionGuard>
```

---

### 阶段 6：测试和验证（第 7-8 天）

#### 6.1 后端单元测试
**新增测试文件**:
- `/backend/tests/services/test_permission.py` - 权限服务测试
- `/backend/tests/services/test_audit.py` - 审计日志服务测试
- `/backend/tests/api/v1/test_permissions.py` - 权限 API 测试
- `/backend/tests/api/v1/test_audit_logs.py` - 审计日志 API 测试
- `/backend/tests/api/v1/test_user_scenarios.py` - 用户场景分配测试

**测试用例**:
```python
# test_permission.py
async def test_system_admin_has_all_permissions():
    """系统管理员拥有所有权限"""

async def test_scenario_admin_has_assigned_scenarios():
    """场景管理员只能访问分配的场景"""

async def test_scenario_admin_permissions():
    """场景管理员的细粒度权限检查"""

async def test_annotator_can_only_see_assigned_scenarios():
    """标注员只能看到分配的场景"""

async def test_auditor_read_only():
    """审计员只有只读权限"""
```

#### 6.2 API 集成测试
**测试场景**:
1. 创建不同角色的用户
2. 分配场景给用户
3. 配置场景管理员权限
4. 测试权限检查（正向和反向）
5. 测试审计日志记录
6. 测试权限变更后立即生效

#### 6.3 前端测试
**手动测试清单**:
- [ ] 系统管理员登录，验证所有菜单可见
- [ ] 场景管理员登录，验证只能看到分配的场景
- [ ] 标注员登录，验证只能看到智能标注
- [ ] 审计员登录，验证只读权限
- [ ] 测试权限不足时的错误提示
- [ ] 测试 401 自动跳转登录
- [ ] 测试 403 错误提示

#### 6.4 端到端测试流程
**测试流程**:
1. 系统管理员创建场景管理员用户
2. 系统管理员分配场景给场景管理员
3. 系统管理员配置场景管理员权限（部分权限）
4. 场景管理员登录，验证只能看到分配的场景
5. 场景管理员尝试访问无权限的功能，验证被拒绝
6. 场景管理员在有权限的场景中操作，验证成功
7. 系统管理员查看审计日志，验证所有操作被记录
8. 系统管理员修改权限，场景管理员刷新后权限立即生效

---

### 阶段 7：双版本架构支持（第 8-9 天）

#### 7.1 配置文件区分
**修改文件**: `/backend/app/core/config.py`

```python
class Settings(BaseSettings):
    # 现有配置...

    # 新增：版本配置
    VERSION: str = "V1"  # V1: 独立版本, V2: 门户集成版本

    # V2 版本配置
    PORTAL_SSO_ENABLED: bool = False
    PORTAL_TOKEN_VERIFY_URL: Optional[str] = None
    PORTAL_USER_INFO_URL: Optional[str] = None

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env"
    )
```

#### 7.2 可插拔认证模块
**新增文件**: `/backend/app/core/auth_provider.py`

```python
class AuthProvider(ABC):
    @abstractmethod
    async def verify_token(self, token: str) -> Dict:
        """验证 Token 并返回用户信息"""

class V1AuthProvider(AuthProvider):
    """V1 版本：本地 JWT 认证"""
    async def verify_token(self, token: str) -> Dict:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return {"username": payload.get("sub")}

class V2AuthProvider(AuthProvider):
    """V2 版本：门户 SSO 认证"""
    async def verify_token(self, token: str) -> Dict:
        # 调用门户 API 验证 Token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.PORTAL_TOKEN_VERIFY_URL,
                headers={"Authorization": f"Bearer {token}"}
            )
            return response.json()

def get_auth_provider() -> AuthProvider:
    if settings.VERSION == "V1":
        return V1AuthProvider()
    else:
        return V2AuthProvider()
```

**修改文件**: `/backend/app/api/v1/deps.py`

```python
async def get_current_user_full(
    token: str = Depends(reusable_oauth2),
    db: AsyncSession = Depends(get_db)
) -> User:
    # 使用可插拔的认证提供者
    auth_provider = get_auth_provider()
    user_info = await auth_provider.verify_token(token)
    username = user_info["username"]

    # 查询数据库获取完整用户信息
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    return user
```

#### 7.3 场景创建流程区分
**修改文件**: `/backend/app/api/v1/endpoints/scenarios.py`

```python
@router.post("/")
async def create_scenario(
    scenario_in: ScenarioCreate,
    current_user: User = Depends(get_current_user_full),
    db: AsyncSession = Depends(get_db)
):
    """创建场景"""
    # V1 版本：系统管理员直接创建
    if settings.VERSION == "V1":
        if current_user.role != "SYSTEM_ADMIN":
            raise HTTPException(status_code=403, detail="Only SYSTEM_ADMIN can create scenarios")

    # V2 版本：通过门户注册后创建（需要验证来源）
    elif settings.VERSION == "V2":
        # 验证请求来自门户系统
        # 可以通过特殊的 API Key 或签名验证
        pass

    # 创建场景逻辑...
```

#### 7.4 环境变量配置
**新增文件**: `/backend/.env.v1` (V1 版本配置)

```env
VERSION=V1
PORTAL_SSO_ENABLED=false
```

**新增文件**: `/backend/.env.v2` (V2 版本配置)

```env
VERSION=V2
PORTAL_SSO_ENABLED=true
PORTAL_TOKEN_VERIFY_URL=https://portal.example.com/api/auth/verify
PORTAL_USER_INFO_URL=https://portal.example.com/api/users/me
```

---

## 五、关键文件清单

### 后端新增文件
- `/backend/migrations/add_rbac_tables.sql` - 数据库迁移脚本
- `/backend/app/repositories/user_scenario_assignment.py` - 用户场景关联 Repository
- `/backend/app/repositories/scenario_admin_permission.py` - 场景权限 Repository
- `/backend/app/repositories/audit_log.py` - 审计日志 Repository
- `/backend/app/services/permission.py` - 权限检查服务
- `/backend/app/services/audit.py` - 审计日志服务
- `/backend/app/api/v1/endpoints/permissions.py` - 权限查询 API
- `/backend/app/api/v1/endpoints/audit_logs.py` - 审计日志 API
- `/backend/app/core/auth_provider.py` - 可插拔认证模块
- `/backend/app/schemas/user_scenario_assignment.py` - 用户场景关联 Schema
- `/backend/app/schemas/scenario_admin_permission.py` - 场景权限 Schema
- `/backend/app/schemas/audit_log.py` - 审计日志 Schema

### 后端修改文件
- `/backend/app/models/db_meta.py` - 扩展 User 模型，新增 3 个模型
- `/backend/app/api/v1/deps.py` - 新增权限检查依赖
- `/backend/app/api/v1/api.py` - 注册新路由
- `/backend/app/api/v1/endpoints/users.py` - 扩展用户管理 API
- `/backend/app/api/v1/endpoints/meta_tags.py` - 添加权限检查
- `/backend/app/api/v1/endpoints/global_keywords.py` - 添加权限检查
- `/backend/app/api/v1/endpoints/scenario_keywords.py` - 添加权限检查
- `/backend/app/api/v1/endpoints/rule_policy.py` - 添加权限检查
- `/backend/app/api/v1/endpoints/scenarios.py` - 添加权限检查
- `/backend/app/api/v1/endpoints/staging.py` - 添加权限检查
- `/backend/app/api/v1/endpoints/playground.py` - 添加权限检查
- `/backend/app/api/v1/endpoints/performance.py` - 添加权限检查
- `/backend/app/core/config.py` - 添加版本配置

### 前端新增文件
- `/frontend/src/contexts/PermissionContext.tsx` - 权限上下文
- `/frontend/src/hooks/usePermission.ts` - 权限 Hook
- `/frontend/src/components/PermissionGuard.tsx` - 权限守卫组件
- `/frontend/src/pages/AuditLogs.tsx` - 审计日志页面
- `/frontend/src/pages/MyScenarios.tsx` - 我的场景页面

### 前端修改文件
- `/frontend/src/App.tsx` - 集成权限上下文，动态菜单
- `/frontend/src/api.ts` - 添加响应拦截器，新增 API
- `/frontend/src/pages/Users.tsx` - 增强用户管理功能
- `/frontend/src/types.ts` - 添加权限相关类型定义

---

## 六、验证清单

### 数据库验证
- [ ] 成功执行迁移脚本
- [ ] 所有表和索引创建成功
- [ ] 外键约束正常工作

### 后端验证
- [ ] 所有单元测试通过
- [ ] 权限检查正确工作
- [ ] 审计日志正确记录
- [ ] API 返回正确的权限信息
- [ ] 401/403 错误正确返回

### 前端验证
- [ ] 权限上下文正确加载
- [ ] 菜单根据角色动态显示
- [ ] 权限守卫组件正确工作
- [ ] 401 自动跳转登录
- [ ] 403 显示错误提示
- [ ] 用户管理页面功能完整
- [ ] 审计日志页面正常显示

### 集成验证
- [ ] 完整的用户创建和分配流程
- [ ] 权限修改立即生效
- [ ] 不同角色的访问控制正确
- [ ] 审计日志完整记录所有操作

### 双版本验证
- [ ] V1 版本本地认证正常
- [ ] V2 版本门户认证正常（如果有门户环境）
- [ ] 配置文件切换正常
- [ ] 场景创建流程区分正确

---

## 七、风险和注意事项

### 7.1 数据迁移风险
- **风险**: 现有用户数据迁移可能失败
- **缓解**:
  - 先在测试环境验证迁移脚本
  - 生产环境迁移前备份数据库
  - 提供回滚脚本

### 7.2 权限检查遗漏
- **风险**: 某些 API 端点可能遗漏权限检查
- **缓解**:
  - 系统性地检查所有端点
  - 编写权限测试用例覆盖所有场景
  - Code Review 重点关注权限检查

### 7.3 性能影响
- **风险**: 每次请求都查询权限可能影响性能
- **缓解**:
  - 考虑使用 Redis 缓存权限信息
  - 优化数据库查询（使用索引）
  - 批量查询减少数据库往返

### 7.4 前端权限绕过
- **风险**: 前端权限控制可以被绕过
- **缓解**:
  - 后端必须进行权限检查（不依赖前端）
  - 前端权限控制仅用于 UI 优化
  - 所有敏感操作都在后端验证

### 7.5 审计日志性能
- **风险**: 大量审计日志写入影响性能
- **缓解**:
  - 考虑异步写入审计日志
  - 定期归档旧日志
  - 使用批量插入

---

## 八、实施建议

### 8.1 分阶段上线
1. **第一阶段**: 数据库和基础服务（不影响现有功能）
2. **第二阶段**: 后端 API 权限控制（灰度发布）
3. **第三阶段**: 前端权限控制（逐步替换）
4. **第四阶段**: 双版本架构支持

### 8.2 向后兼容
- 保留现有的硬编码管理员 (llm_guard)
- 现有用户自动迁移为 SYSTEM_ADMIN 角色
- 现有 API 保持兼容，逐步添加权限检查

### 8.3 文档更新
- 更新 API 文档，标注权限要求
- 编写用户手册，说明角色和权限
- 编写运维手册，说明双版本部署

---

## 九、总结

本计划基于现有架构，采用渐进式改造方式实现完整的 RBAC 系统：

**核心特性**:
1. 4 种角色：SYSTEM_ADMIN, SCENARIO_ADMIN, ANNOTATOR, AUDITOR
2. 场景级别权限隔离
3. 场景管理员的 5 种细粒度权限
4. 完整的审计日志系统
5. 双版本架构支持（V1 独立 + V2 门户集成）

**技术亮点**:
1. 继承现有分层架构，保持代码一致性
2. 使用依赖注入实现权限检查，代码简洁
3. React Context 管理前端权限状态
4. 可插拔认证模块支持双版本
5. 完整的测试覆盖

**实施周期**: 预计 8-9 天完成全部功能。

