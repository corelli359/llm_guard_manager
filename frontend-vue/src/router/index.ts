import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginPage.vue'),
    meta: { public: true },
  },
  {
    path: '/sso/login',
    name: 'SSOLogin',
    component: () => import('../views/SSOLogin.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('../layout/Layout.vue'),
    children: [
      { path: '', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'tags', name: 'MetaTags', component: () => import('../views/MetaTags.vue') },
      { path: 'global-keywords', name: 'GlobalKeywords', component: () => import('../views/GlobalKeywords.vue') },
      { path: 'global-policies', name: 'GlobalPolicies', component: () => import('../views/GlobalPolicies.vue') },
      { path: 'apps', name: 'Apps', component: () => import('../views/Apps.vue') },
      { path: 'apps/:appId', name: 'AppDashboard', component: () => import('../views/AppDashboard.vue') },
      { path: 'apps/:appId/keywords', name: 'ScenarioKeywords', component: () => import('../views/ScenarioKeywords.vue') },
      { path: 'apps/:appId/policies', name: 'ScenarioPolicies', component: () => import('../views/ScenarioPolicies.vue') },
      { path: 'playground', name: 'InputPlayground', component: () => import('../views/InputPlayground.vue') },
      { path: 'performance', name: 'PerformanceTest', component: () => import('../views/PerformanceTest.vue') },
      { path: 'users', name: 'UsersPage', component: () => import('../views/UsersPage.vue') },
      { path: 'roles', name: 'RolesPage', component: () => import('../views/RolesPage.vue') },
      { path: 'audit-logs', name: 'AuditLogs', component: () => import('../views/AuditLogs.vue') },
      { path: 'smart-labeling', name: 'SmartLabeling', component: () => import('../views/SmartLabeling.vue') },
      { path: 'annotator-stats', name: 'AnnotatorStats', component: () => import('../views/AnnotatorStats.vue') },
      { path: 'my-scenarios', name: 'MyScenarios', component: () => import('../views/MyScenarios.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_BASE_PATH || '/web-vue/'),
  routes,
})

router.beforeEach((to, _from, next) => {
  if (to.meta.public) return next()
  const token = localStorage.getItem('access_token')
  if (!token) return next({ name: 'Login' })
  next()
})

export default router
