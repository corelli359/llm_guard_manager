import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserPermissionsV2 } from '../types'
import { userRolesApi } from '../api'

export const usePermissionStore = defineStore('permission', () => {
  const userPermissions = ref<UserPermissionsV2 | null>(null)
  const loading = ref(true)

  const userRole = computed(() => localStorage.getItem('user_role') || '')

  async function fetchPermissions() {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) { loading.value = false; return }
      const response = await userRolesApi.getMyPermissions()
      userPermissions.value = response.data
    } catch (error: any) {
      console.error('Failed to fetch permissions', error)
      if (error?.response?.status === 401) {
        localStorage.removeItem('access_token')
      }
    } finally {
      loading.value = false
    }
  }

  function hasPermission(permissionCode: string): boolean {
    if (!userPermissions.value) return false
    return userPermissions.value.global_permissions.includes(permissionCode)
  }

  function hasScenarioPermission(scenarioId: string, permissionCode: string): boolean {
    if (!userPermissions.value) return false
    if (userPermissions.value.global_permissions.includes(permissionCode)) return true
    const scenarioPerms = userPermissions.value.scenario_permissions[scenarioId]
    return scenarioPerms ? scenarioPerms.includes(permissionCode) : false
  }

  function hasRole(roles: string[]): boolean {
    if (!userPermissions.value) return false
    if (roles.includes('SYSTEM_ADMIN') && hasPermission('user_management')) return true
    if (roles.includes('SCENARIO_ADMIN') && Object.keys(userPermissions.value.scenario_permissions).length > 0) return true
    if (roles.includes('AUDITOR') && hasPermission('audit_logs') && !hasPermission('user_management')) return true
    if (roles.includes('ANNOTATOR') && hasPermission('smart_labeling')) return true
    return false
  }

  function hasScenarioAccess(scenarioId: string): boolean {
    if (!userPermissions.value) return false
    if (hasPermission('app_management')) return true
    return scenarioId in userPermissions.value.scenario_permissions
  }

  return {
    userPermissions, loading, userRole,
    fetchPermissions, hasPermission, hasScenarioPermission, hasRole, hasScenarioAccess,
  }
})
