import axios from 'axios';
import { MetaTag, GlobalKeyword, ScenarioKeyword, RuleScenarioPolicy, ScenarioApp } from './types';

const api = axios.create({
  baseURL: '/api/v1', // Vite proxy will handle this
});

export const metaTagsApi = {
  getAll: () => api.get<MetaTag[]>('/tags/'),
  create: (data: Omit<MetaTag, 'id'>) => api.post<MetaTag>('/tags/', data),
  update: (id: string, data: Partial<MetaTag>) => api.put<MetaTag>(`/tags/${id}`, data),
  delete: (id: string) => api.delete<MetaTag>(`/tags/${id}`),
};

export const globalKeywordsApi = {
  getAll: (skip = 0, limit = 100) => api.get<GlobalKeyword[]>('/keywords/global/', { params: { skip, limit } }),
  create: (data: Omit<GlobalKeyword, 'id'>) => api.post<GlobalKeyword>('/keywords/global/', data),
  update: (id: string, data: Partial<GlobalKeyword>) => api.put<GlobalKeyword>(`/keywords/global/${id}`, data),
  delete: (id: string) => api.delete<GlobalKeyword>(`/keywords/global/${id}`),
};

export const scenarioKeywordsApi = {
  getByScenario: (scenarioId: string) => api.get<ScenarioKeyword[]>(`/keywords/scenario/${scenarioId}`),
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

export const scenariosApi = {
  getAll: () => api.get<ScenarioApp[]>('/apps/'),
  getByAppId: (appId: string) => api.get<ScenarioApp>(`/apps/${appId}`),
  create: (data: Omit<ScenarioApp, 'id'>) => api.post<ScenarioApp>('/apps/', data),
  update: (id: string, data: Partial<ScenarioApp>) => api.put<ScenarioApp>(`/apps/${id}`, data),
  delete: (id: string) => api.delete<ScenarioApp>(`/apps/${id}`),
};

export default api;
