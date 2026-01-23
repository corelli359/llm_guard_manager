import axios from 'axios';
import { MetaTag, GlobalKeyword, ScenarioKeyword, RuleScenarioPolicy, ScenarioApp } from './types';

// 获取 base path（如果部署在子路径下）
const basePath = import.meta.env.BASE_URL || '/';
const apiBasePath = basePath === '/' ? '' : basePath.replace(/\/$/, '');

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || `${apiBasePath}/api/v1`,
});

// Request interceptor to add the authorization token to headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const metaTagsApi = {
  getAll: () => api.get<MetaTag[]>('/tags/'),
  create: (data: Omit<MetaTag, 'id'>) => api.post<MetaTag>('/tags/', data),
  update: (id: string, data: Partial<MetaTag>) => api.put<MetaTag>(`/tags/${id}`, data),
  delete: (id: string) => api.delete<MetaTag>(`/tags/${id}`),
};

export const globalKeywordsApi = {
  getAll: (skip = 0, limit = 100, q?: string, tag?: string) => api.get<GlobalKeyword[]>('/keywords/global/', { params: { skip, limit, q, tag } }),
  create: (data: Omit<GlobalKeyword, 'id'>) => api.post<GlobalKeyword>('/keywords/global/', data),
  update: (id: string, data: Partial<GlobalKeyword>) => api.put<GlobalKeyword>(`/keywords/global/${id}`, data),
  delete: (id: string) => api.delete<GlobalKeyword>(`/keywords/global/${id}`),
};

export const scenarioKeywordsApi = {
  getByScenario: (scenarioId: string, ruleMode?: number) => api.get<ScenarioKeyword[]>(`/keywords/scenario/${scenarioId}`, { params: { rule_mode: ruleMode } }),
  create: (data: Omit<ScenarioKeyword, 'id'>) => api.post<ScenarioKeyword>('/keywords/scenario/', data),
  update: (id: string, data: Partial<ScenarioKeyword>) => api.put<ScenarioKeyword>(`/keywords/scenario/${id}`, data),
  delete: (id: string) => api.delete<ScenarioKeyword>(`/keywords/scenario/${id}`),
};

export const rulePoliciesApi = {
  getByScenario: (scenarioId: string) => api.get<RuleScenarioPolicy[]>(`/policies/scenario/${scenarioId}`),
  create: (data: Omit<RuleScenarioPolicy, 'id'>) => api.post<RuleScenarioPolicy>('/policies/scenario/', data),
  update: (id: string, data: Partial<RuleScenarioPolicy>) => api.put<RuleScenarioPolicy>(`/policies/scenario/${id}`, data),
  delete: (id: string) => api.delete<RuleScenarioPolicy>(`/policies/scenario/${id}`),
};

export const globalPoliciesApi = {
  getAll: (skip = 0, limit = 100) => api.get<import('./types').RuleGlobalDefault[]>('/policies/defaults/', { params: { skip, limit } }),
  create: (data: Omit<import('./types').RuleGlobalDefault, 'id'>) => api.post<import('./types').RuleGlobalDefault>('/policies/defaults/', data),
  update: (id: string, data: Partial<import('./types').RuleGlobalDefault>) => api.put<import('./types').RuleGlobalDefault>(`/policies/defaults/${id}`, data),
  delete: (id: string) => api.delete<import('./types').RuleGlobalDefault>(`/policies/defaults/${id}`),
};

export const scenariosApi = {
  getAll: () => api.get<ScenarioApp[]>('/apps/'),
  getByAppId: (appId: string) => api.get<ScenarioApp>(`/apps/${appId}`),
  create: (data: Omit<ScenarioApp, 'id'>) => api.post<ScenarioApp>('/apps/', data),
  update: (id: string, data: Partial<ScenarioApp>) => api.put<ScenarioApp>(`/apps/${id}`, data),
  delete: (id: string) => api.delete<ScenarioApp>(`/apps/${id}`),
};

export const playgroundApi = {
  testInput: (data: any) => api.post('/playground/input', data),
  getHistory: (params: { page?: number; size?: number; playground_type?: string; app_id?: string }) => {
      const { page = 1, size = 20, playground_type, app_id } = params;
      let url = `/playground/history?page=${page}&size=${size}`;
      if (playground_type) url += `&playground_type=${playground_type}`;
      if (app_id) url += `&app_id=${app_id}`;
      return api.get(url);
  },
};

export const performanceApi = {
    dryRun: (config: any) => api.post('/performance/dry-run', config),
    start: (data: any) => api.post('/performance/start', data),
    stop: () => api.post('/performance/stop'),
    getStatus: () => api.get('/performance/status'),
    getHistoryList: () => api.get('/performance/history'),
    getHistoryDetail: (id: string) => api.get(`/performance/history/${id}`),
    deleteHistory: (id: string) => api.delete(`/performance/history/${id}`),
};

export const usersApi = {
    list: () => api.get('/users/'),
    create: (data: any) => api.post('/users/', data),
    updateStatus: (id: string, active: boolean) => api.patch(`/users/${id}/status`, { is_active: active }),
    resetPassword: (id: string) => api.post(`/users/${id}/reset-password`),
    delete: (id: string) => api.delete(`/users/${id}`),
};

export const stagingApi = {
    listKeywords: (status?: string) => api.get(`/staging/keywords${status ? `?status=${status}` : ''}`),
    reviewKeyword: (id: string, data: any) => api.patch(`/staging/keywords/${id}`, data),
    deleteKeyword: (id: string) => api.delete(`/staging/keywords/${id}`),
    syncKeywords: (ids: string[]) => api.post('/staging/keywords/sync', { ids }),
    importMock: () => api.post('/staging/keywords/import-mock'),
    
    listRules: (status?: string) => api.get(`/staging/rules${status ? `?status=${status}` : ''}`),
    reviewRule: (id: string, data: any) => api.patch(`/staging/rules/${id}`, data),
    deleteRule: (id: string) => api.delete(`/staging/rules/${id}`),
    syncRules: (ids: string[]) => api.post('/staging/rules/sync', { ids }),
    importMockRules: () => api.post('/staging/rules/import-mock'),
};

export default api;