<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePermissionStore } from '../stores/permission'

const router = useRouter()
const permStore = usePermissionStore()

const PERMISSION_LABELS: Record<string, string> = {
  scenario_keywords: '敏感词管理',
  scenario_policies: '策略管理',
  scenario_playground: '测试工具',
  scenario_performance: '性能测试',
  scenario_basic_info: '基本信息',
}

const scenarioEntries = computed(() => {
  if (!permStore.userPermissions?.scenario_permissions) return []
  return Object.entries(permStore.userPermissions.scenario_permissions)
})

function goToScenario(appId: string) {
  localStorage.setItem('current_app_id', appId)
  router.push(`/apps/${appId}`)
}
</script>

<template>
  <div style="padding: 24px">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span style="font-size: 18px; font-weight: bold">我的场景</span>
          <el-tag type="primary">{{ scenarioEntries.length }} 个场景</el-tag>
        </div>
      </template>

      <el-empty v-if="permStore.loading" description="加载中..." />
      <el-empty v-else-if="scenarioEntries.length === 0" description="您还没有被分配任何场景" />

      <el-row v-else :gutter="16">
        <el-col v-for="[scenarioId, permissions] in scenarioEntries" :key="scenarioId" :xs="24" :sm="12" :lg="8" :xl="6" style="margin-bottom: 16px">
          <el-card shadow="hover" class="scenario-card" @click="goToScenario(scenarioId)">
            <div style="margin-bottom: 16px; display: flex; align-items: center; gap: 8px">
              <el-icon :size="24" color="#409eff"><Monitor /></el-icon>
              <span style="font-weight: bold; font-size: 16px">{{ scenarioId }}</span>
            </div>
            <div v-if="permissions.length > 0">
              <div style="font-size: 12px; color: #666; margin-bottom: 8px">权限:</div>
              <div style="display: flex; flex-wrap: wrap; gap: 4px">
                <el-tag v-for="perm in permissions" :key="perm" type="success" size="small">
                  {{ PERMISSION_LABELS[perm] || perm }}
                </el-tag>
              </div>
            </div>
            <div style="margin-top: 16px; text-align: right">
              <el-link type="primary">进入管理 →</el-link>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<style scoped>
.scenario-card { cursor: pointer; height: 100%; }
</style>
