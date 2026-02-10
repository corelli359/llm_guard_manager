import axios from 'axios'
import type {
  MetaTag, GlobalKeyword, ScenarioKeyword, RuleScenarioPolicy,
  RuleGlobalDefault, ScenarioApp
} from '../types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_role')
      localStorage.removeItem('current_app_id')
      const base = import.meta.env.VITE_BASE_PATH || '/'
      window.location.href = `${base}login`
    }
    return Promise.reject(error)
  }
)

export function getErrorMessage(error: any, fallback = '操作失败'): string {
  if (!error.response) return '网络连接失败，请检查网络'
  const status = error.response.status
  const detail = error.response.data?.detail
  switch (status) {
    case 400: return detail || '请求参数错误'
    case 401: return '登录已过期，请重新登录'
    case 403: {
      if (detail?.includes('Missing permission')) {
        const match = detail.match(/Missing permission: (\w+) for scenario: (.+)/)
        if (match) {
          const permLabels: Record<string, string> = {
            scenario_keywords: '场景敏感词管理', scenario_policies: '场景策略管理',
            scenario_basic_info: '场景基本信息', playground: '输入试验场', performance_test: '性能测试',
          }
          return `权限不足：您没有「${permLabels[match[1]] || match[1]}」的权限`
        }
      }
      if (detail?.includes('No access to scenario')) return '权限不足：您没有该场景的访问权限'
      if (detail?.includes('Not authorized')) return '权限不足：您无权执行此操作'
      return detail ? `权限不足：${detail}` : '权限不足：您无权执行此操作'
    }
    case 404: return detail || '请求的资源不存在'
    case 409: return detail || '数据冲突，请刷新后重试'
    case 422: return '数据格式错误，请检查输入'
    case 500: return '服务器内部错误，请稍后重试'
    default: return detail || fallback
  }
}

export const metaTagsApi = {
  getAll: () => api.get<MetaTag[]>('/tags/'),
  create: (data: Omit<MetaTag, 'id'>) => api.post<MetaTag>('/tags/', data),
  update: (id: string, data: Partial<MetaTag>) => api.put<MetaTag>(`/tags/${id}`, data),
  delete: (id: string) => api.delete(`/tags/${id}`),
}

export const globalKeywordsApi = {
  getAll: (skip = 0, limit = 100, q?: string, tag?: string) =>
    api.get<GlobalKeyword[]>('/keywords/global/', { params: { skip, limit, q, tag } }),
  create: (data: Omit<GlobalKeyword, 'id'>) => api.post<GlobalKeyword>('/keywords/global/', data),
  update: (id: string, data: Partial<GlobalKeyword>) => api.put<GlobalKeyword>(`/keywords/global/${id}`, data),
  delete: (id: string) => api.delete(`/keywords/global/${id}`),
}

export const scenarioKeywordsApi = {
  getByScenario: (scenarioId: string, ruleMode?: number) =>
    api.get<ScenarioKeyword[]>(`/keywords/scenario/${scenarioId}`, { params: { rule_mode: ruleMode } }),
  create: (data: Omit<ScenarioKeyword, 'id'>) => api.post<ScenarioKeyword>('/keywords/scenario/', data),
  update: (id: string, data: Partial<ScenarioKeyword>) => api.put<ScenarioKeyword>(`/keywords/scenario/${id}`, data),
  delete: (id: string) => api.delete(`/keywords/scenario/${id}`),
}

export const rulePoliciesApi = {
  getByScenario: (scenarioId: string) => api.get<RuleScenarioPolicy[]>(`/policies/scenario/${scenarioId}`),
  create: (data: Omit<RuleScenarioPolicy, 'id'>) => api.post<RuleScenarioPolicy>('/policies/scenario/', data),
  update: (id: string, data: Partial<RuleScenarioPolicy>) => api.put<RuleScenarioPolicy>(`/policies/scenario/${id}`, data),
  delete: (id: string) => api.delete(`/policies/scenario/${id}`),
}

export const globalPoliciesApi = {
  getAll: (skip = 0, limit = 100) => api.get<RuleGlobalDefault[]>('/policies/defaults/', { params: { skip, limit } }),
  create: (data: Omit<RuleGlobalDefault, 'id'>) => api.post<RuleGlobalDefault>('/policies/defaults/', data),
  update: (id: string, data: Partial<RuleGlobalDefault>) => api.put<RuleGlobalDefault>(`/policies/defaults/${id}`, data),
  delete: (id: string) => api.delete(`/policies/defaults/${id}`),
}

export const scenariosApi = {
  getAll: () => api.get<ScenarioApp[]>('/apps/'),
  getByAppId: (appId: string) => api.get<ScenarioApp>(`/apps/${appId}`),
  create: (data: Omit<ScenarioApp, 'id'>) => api.post<ScenarioApp>('/apps/', data),
  update: (id: string, data: Partial<ScenarioApp>) => api.put<ScenarioApp>(`/apps/${id}`, data),
  delete: (id: string) => api.delete(`/apps/${id}`),
}

export const playgroundApi = {
  testInput: (data: any) => api.post('/playground/input', data),
  getHistory: (params: { page?: number; size?: number; playground_type?: string; app_id?: string }) => {
    const { page = 1, size = 20, playground_type, app_id } = params
    let url = `/playground/history?page=${page}&size=${size}`
    if (playground_type) url += `&playground_type=${playground_type}`
    if (app_id) url += `&app_id=${app_id}`
    return api.get(url)
  },
}

export const performanceApi = {
  dryRun: (config: any) => api.post('/performance/dry-run', config),
  start: (data: any) => api.post('/performance/start', data),
  stop: () => api.post('/performance/stop'),
  getStatus: () => api.get('/performance/status'),
  getHistoryList: () => api.get('/performance/history'),
  getHistoryDetail: (id: string) => api.get(`/performance/history/${id}`),
  deleteHistory: (id: string) => api.delete(`/performance/history/${id}`),
}

export const usersApi = {
  list: () => api.get('/users/'),
  updateRole: (id: string, role: string) => api.put(`/users/${id}/role`, { role }),
  updateStatus: (id: string, active: boolean) => api.patch(`/users/${id}/status`, { is_active: active }),
  delete: (id: string) => api.delete(`/users/${id}`),
}

export const rolesApi = {
  list: () => api.get('/roles/'),
  create: (data: any) => api.post('/roles/', data),
  update: (id: string, data: any) => api.put(`/roles/${id}`, data),
  delete: (id: string) => api.delete(`/roles/${id}`),
  getPermissions: (id: string) => api.get(`/roles/${id}/permissions`),
  updatePermissions: (id: string, permissionIds: string[]) => api.put(`/roles/${id}/permissions`, { permission_ids: permissionIds }),
  listAllPermissions: () => api.get('/roles/permissions/all'),
}

export const userRolesApi = {
  getUserRoles: (userId: string) => api.get(`/users/${userId}/roles`),
  assignRole: (userId: string, data: { role_id: string; scenario_id?: string }) => api.post(`/users/${userId}/roles`, data),
  removeRole: (userId: string, assignmentId: string) => api.delete(`/users/${userId}/roles/${assignmentId}`),
  getMyPermissions: () => api.get('/users/me/permissions'),
}

export const stagingApi = {
  listKeywords: (status?: string, myTasks?: boolean) => {
    let url = '/staging/keywords'
    const params = new URLSearchParams()
    if (status) params.append('status', status)
    if (myTasks) params.append('my_tasks', 'true')
    if (params.toString()) url += `?${params.toString()}`
    return api.get(url)
  },
  reviewKeyword: (id: string, data: any) => api.patch(`/staging/keywords/${id}`, data),
  deleteKeyword: (id: string) => api.delete(`/staging/keywords/${id}`),
  syncKeywords: (ids: string[]) => api.post('/staging/keywords/sync', { ids }),
  batchReviewKeywords: (items: any[]) => api.post('/staging/keywords/batch-review', { items }),
  listRules: (status?: string, myTasks?: boolean) => {
    let url = '/staging/rules'
    const params = new URLSearchParams()
    if (status) params.append('status', status)
    if (myTasks) params.append('my_tasks', 'true')
    if (params.toString()) url += `?${params.toString()}`
    return api.get(url)
  },
  reviewRule: (id: string, data: any) => api.patch(`/staging/rules/${id}`, data),
  deleteRule: (id: string) => api.delete(`/staging/rules/${id}`),
  syncRules: (ids: string[]) => api.post('/staging/rules/sync', { ids }),
  batchReviewRules: (items: any[]) => api.post('/staging/rules/batch-review', { items }),
  claimBatch: (batchSize: number, taskType: string) => api.post('/staging/claim', { batch_size: batchSize, task_type: taskType }),
  releaseExpired: () => api.post('/staging/release-expired'),
  getAnnotatorStats: (taskType: string) => api.get(`/staging/stats/annotators?task_type=${taskType}`),
  getMyTasksStats: (taskType: string) => api.get(`/staging/my-tasks/stats?task_type=${taskType}`),
  getTaskOverview: (taskType: string) => api.get(`/staging/overview?task_type=${taskType}`),
}

export const permissionsApi = {
  getMyPermissions: () => api.get('/permissions/me'),
  checkPermission: (scenarioId: string, permission: string) =>
    api.get('/permissions/check', { params: { scenario_id: scenarioId, permission } }),
}

export const userScenariosApi = {
  assignScenario: (userId: string, data: any) => api.post(`/users/${userId}/scenarios`, data),
  configurePermissions: (userId: string, scenarioId: string, permissions: any) =>
    api.put(`/users/${userId}/scenarios/${scenarioId}/permissions`, permissions),
  getUserScenarios: (userId: string) => api.get(`/users/${userId}/scenarios`),
  removeScenarioAssignment: (userId: string, scenarioId: string) =>
    api.delete(`/users/${userId}/scenarios/${scenarioId}`),
}

export const auditLogsApi = {
  queryLogs: (params: any) => api.get('/audit-logs/', { params }),
}

export const ssoApi = {
  login: (ticket: string) => api.post<{
    access_token: string; token_type: string; expires_in: number; user_id: string; role: string
  }>('/sso/login', { ticket }),
  getUserInfo: () => api.get('/sso/user-info'),
  getUsersBatch: (userIds: string[]) => api.post('/sso/users/batch', { user_ids: userIds }),
  health: () => api.get('/sso/health'),
}

export default api
