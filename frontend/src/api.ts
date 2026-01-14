import axios from 'axios';
import { MetaTag, GlobalKeyword, ScenarioKeyword, RuleScenarioPolicy, ScenarioApp, PlaygroundHistory } from './types';

const api = axios.create({
  baseURL: '/api/v1', // Vite proxy will handle this
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
  testInput: (data: import('./types').PlaygroundRequest) => api.post<import('./types').PlaygroundResponse>('/playground/input', data),
  getHistory: (params: { page?: number; size?: number; playground_type?: string; app_id?: string }) => 
    api.get<PlaygroundHistory[]>('/playground/history', { params }),
};

export default api;