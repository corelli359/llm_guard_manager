# 前端权限控制使用指南

## 1. 权限上下文使用

### 在组件中使用权限Hook

```tsx
import { usePermission } from '../hooks/usePermission';

const MyComponent: React.FC = () => {
  const { userRole, userPermissions, hasRole, hasScenarioAccess, hasScenarioPermission } = usePermission();

  // 检查用户角色
  if (hasRole(['SYSTEM_ADMIN'])) {
    // 系统管理员专属功能
  }

  // 检查场景访问权限
  if (hasScenarioAccess('scenario_001')) {
    // 用户可以访问该场景
  }

  // 检查场景细粒度权限
  if (hasScenarioPermission('scenario_001', 'scenario_keywords')) {
    // 用户可以管理该场景的敏感词
  }

  return <div>...</div>;
};
```

## 2. 权限守卫组件使用

### 基于角色的权限控制

```tsx
import { PermissionGuard } from '../components/PermissionGuard';

// 只有系统管理员可以看到
<PermissionGuard roles={['SYSTEM_ADMIN']}>
  <Button type="primary">创建全局配置</Button>
</PermissionGuard>

// 系统管理员和场景管理员可以看到
<PermissionGuard roles={['SYSTEM_ADMIN', 'SCENARIO_ADMIN']}>
  <Button>编辑场景</Button>
</PermissionGuard>

// 权限不足时显示fallback内容
<PermissionGuard roles={['SYSTEM_ADMIN']} fallback={<span>权限不足</span>}>
  <Button danger>删除</Button>
</PermissionGuard>
```

### 基于场景权限的控制

```tsx
// 检查用户是否有场景敏感词管理权限
<PermissionGuard scenarioId="scenario_001" permission="scenario_keywords">
  <Button>新增敏感词</Button>
</PermissionGuard>

// 检查用户是否有场景策略管理权限
<PermissionGuard scenarioId="scenario_001" permission="scenario_policies">
  <Button>配置策略</Button>
</PermissionGuard>

// 检查用户是否有测试工具访问权限
<PermissionGuard scenarioId="scenario_001" permission="playground">
  <Button>进入测试</Button>
</PermissionGuard>
```

## 3. 动态菜单配置

菜单会根据用户角色自动显示/隐藏:

### SYSTEM_ADMIN (系统管理员)
- ✅ 智能标注
- ✅ 标注统计
- ✅ 系统管理 (用户管理、审计日志)
- ✅ 全局配置 (应用管理、标签管理、全局敏感词、全局默认规则)
- ✅ 测试工具 (输入试验场、性能测试)
- ✅ 当前应用 (应用概览、场景策略管理)

### SCENARIO_ADMIN (场景管理员)
- ✅ 智能标注
- ✅ 标注统计
- ✅ 我的场景 (显示分配的场景列表)

### ANNOTATOR (标注员)
- ✅ 智能标注
- ✅ 我的场景 (显示分配的场景列表)

### AUDITOR (审计员)
- ✅ 智能标注
- ✅ 标注统计
- ✅ 审计日志 (只读)

## 4. API调用示例

### 获取当前用户权限

```tsx
import { permissionsApi } from '../api';

const fetchPermissions = async () => {
  try {
    const res = await permissionsApi.getMyPermissions();
    console.log('用户权限:', res.data);
    // {
    //   user_id: "xxx",
    //   username: "admin",
    //   role: "SYSTEM_ADMIN",
    //   scenarios: [...]
    // }
  } catch (error) {
    console.error('获取权限失败', error);
  }
};
```

### 检查特定权限

```tsx
import { permissionsApi } from '../api';

const checkPermission = async (scenarioId: string, permission: string) => {
  try {
    const res = await permissionsApi.checkPermission(scenarioId, permission);
    console.log('权限检查结果:', res.data);
  } catch (error) {
    console.error('权限检查失败', error);
  }
};
```

### 为用户分配场景

```tsx
import { userScenariosApi } from '../api';

const assignScenario = async (userId: string) => {
  try {
    await userScenariosApi.assignScenario(userId, {
      scenario_id: 'scenario_001',
      role: 'SCENARIO_ADMIN'
    });
    message.success('场景分配成功');
  } catch (error) {
    message.error('分配失败');
  }
};
```

### 配置场景管理员权限

```tsx
import { userScenariosApi } from '../api';

const configurePermissions = async (userId: string, scenarioId: string) => {
  try {
    await userScenariosApi.configurePermissions(userId, scenarioId, {
      scenario_basic_info: true,
      scenario_keywords: true,
      scenario_policies: false,
      playground: true,
      performance_test: false
    });
    message.success('权限配置成功');
  } catch (error) {
    message.error('配置失败');
  }
};
```

### 查询审计日志

```tsx
import { auditLogsApi } from '../api';

const queryLogs = async () => {
  try {
    const res = await auditLogsApi.queryLogs({
      username: 'admin',
      action: 'CREATE',
      resource_type: 'KEYWORD',
      start_date: '2026-01-01 00:00:00',
      end_date: '2026-12-31 23:59:59',
      skip: 0,
      limit: 20
    });
    console.log('审计日志:', res.data);
  } catch (error) {
    console.error('查询失败', error);
  }
};
```

## 5. 错误处理

### 401 未授权
当token过期或无效时,系统会自动:
1. 清除localStorage中的token和用户信息
2. 跳转到登录页面

### 403 权限不足
当用户没有权限执行某操作时,系统会:
1. 显示错误提示: "您没有权限执行此操作"
2. 不会跳转页面

### 手动处理错误

```tsx
try {
  await someApi.call();
} catch (error: any) {
  if (error.response?.status === 403) {
    message.error('您没有权限执行此操作');
  } else {
    message.error('操作失败');
  }
}
```

## 6. 权限刷新

### 自动刷新
- 用户登录后自动获取权限信息
- 权限信息存储在PermissionContext中

### 手动刷新

```tsx
const { refreshPermissions } = usePermission();

const handleRefresh = async () => {
  await refreshPermissions();
  message.success('权限已刷新');
};
```

## 7. 最佳实践

### 1. 始终在后端验证权限
前端权限控制仅用于UI优化,不能作为安全保障。所有敏感操作必须在后端验证权限。

### 2. 使用权限守卫组件
优先使用`PermissionGuard`组件而不是手动判断,代码更简洁:

```tsx
// ❌ 不推荐
{hasRole(['SYSTEM_ADMIN']) && <Button>删除</Button>}

// ✅ 推荐
<PermissionGuard roles={['SYSTEM_ADMIN']}>
  <Button>删除</Button>
</PermissionGuard>
```

### 3. 合理使用fallback
当需要在权限不足时显示提示信息时,使用fallback:

```tsx
<PermissionGuard
  roles={['SYSTEM_ADMIN']}
  fallback={<Tooltip title="仅系统管理员可操作"><Button disabled>删除</Button></Tooltip>}
>
  <Button danger>删除</Button>
</PermissionGuard>
```

### 4. 避免过度检查
不要在每个组件中都检查权限,合理使用路由级别的权限控制。

### 5. 错误处理
始终为API调用添加错误处理,提供友好的错误提示。

## 8. 调试技巧

### 查看当前用户权限

```tsx
const { userPermissions } = usePermission();
console.log('当前用户权限:', userPermissions);
```

### 查看权限检查结果

```tsx
const { hasRole, hasScenarioPermission } = usePermission();
console.log('是否为管理员:', hasRole(['SYSTEM_ADMIN']));
console.log('是否有敏感词权限:', hasScenarioPermission('scenario_001', 'scenario_keywords'));
```

### 使用React DevTools
在React DevTools中查看PermissionContext的值,确认权限信息是否正确加载。

## 9. 常见问题

### Q: 权限信息没有加载?
A: 检查是否在PermissionProvider内部使用,确保token有效。

### Q: 菜单没有根据角色显示?
A: 检查userRole是否正确,确认hasRole()方法返回值。

### Q: 权限守卫不生效?
A: 确认PermissionContext已正确加载,检查权限参数是否正确。

### Q: 401错误没有自动跳转?
A: 检查api.ts中的响应拦截器是否正确配置。

## 10. 扩展建议

### 添加权限缓存
```tsx
// 使用localStorage缓存权限信息
const cachedPermissions = localStorage.getItem('user_permissions');
if (cachedPermissions) {
  setUserPermissions(JSON.parse(cachedPermissions));
}
```

### 添加权限变更监听
```tsx
// 监听权限变更,自动刷新
useEffect(() => {
  const interval = setInterval(() => {
    refreshPermissions();
  }, 5 * 60 * 1000); // 每5分钟刷新一次

  return () => clearInterval(interval);
}, []);
```

### 添加权限日志
```tsx
// 记录权限检查日志
const hasRole = (roles: string[]) => {
  const result = roles.includes(userPermissions.role);
  console.log(`权限检查: ${roles.join(',')} -> ${result}`);
  return result;
};
```
