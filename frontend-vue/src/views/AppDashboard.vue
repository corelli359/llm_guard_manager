<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { ScenarioApp } from '../types'
import { scenariosApi, getErrorMessage } from '../api'
import { usePermissionStore } from '../stores/permission'

const route = useRoute()
const router = useRouter()
const permStore = usePermissionStore()
const appId = computed(() => route.params.appId as string)
const appData = ref<ScenarioApp | null>(null)
const loading = ref(true)

onMounted(() => { if (appId.value) fetchApp(appId.value) })

async function fetchApp(id: string) {
  try { appData.value = (await scenariosApi.getByAppId(id)).data }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '未找到该应用')) }
  finally { loading.value = false }
}

const canManagePolicies = computed(() => {
  if (!appId.value) return false
  return permStore.hasPermission('scenario_policies') || permStore.hasPermission('scenario_keywords')
    || permStore.hasScenarioPermission(appId.value, 'scenario_policies')
    || permStore.hasScenarioPermission(appId.value, 'scenario_keywords')
})
const isGlobalAdmin = computed(() => permStore.hasPermission('app_management'))
</script>

<template>
  <div style="padding: 24px">
    <div v-if="loading" v-loading="true" style="height: 200px" />
    <div v-else-if="!appData">应用未找到</div>
    <template v-else>
      <el-button @click="router.push(isGlobalAdmin ? '/apps' : '/my-scenarios')" style="margin-bottom: 16px">
        {{ isGlobalAdmin ? '返回应用列表' : '返回我的场景' }}
      </el-button>

      <el-card>
        <template #header>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span>应用详情: {{ appData.app_name }}</span>
            <el-tag :type="appData.is_active ? 'success' : 'info'">{{ appData.is_active ? '运行中' : '已停用' }}</el-tag>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="应用 ID (App ID)">{{ appData.app_id }}</el-descriptions-item>
          <el-descriptions-item label="描述">{{ appData.description || '-' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <h3 style="margin-top: 24px">功能模块配置</h3>
      <el-card>
        <template #header>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span>场景策略配置</span>
            <el-button v-if="canManagePolicies" type="primary" @click="router.push(`/apps/${appData!.app_id}/policies`)">进入配置</el-button>
            <el-tag v-else type="info">无权限</el-tag>
          </div>
        </template>
        <el-row :gutter="16" style="text-align: center">
          <el-col :span="8">
            <div style="margin-bottom: 8px; font-size: 24px" :style="{ color: appData.enable_blacklist ? '#f56c6c' : '#dcdfe6' }">!</div>
            <div>敏感词黑名单</div>
            <el-tag :type="appData.enable_blacklist ? 'success' : 'info'" size="small" style="margin-top:8px">{{ appData.enable_blacklist ? '已启用' : '未启用' }}</el-tag>
          </el-col>
          <el-col :span="8">
            <div style="margin-bottom: 8px; font-size: 24px" :style="{ color: appData.enable_whitelist ? '#67c23a' : '#dcdfe6' }">&#10003;</div>
            <div>敏感词白名单</div>
            <el-tag :type="appData.enable_whitelist ? 'success' : 'info'" size="small" style="margin-top:8px">{{ appData.enable_whitelist ? '已启用' : '未启用' }}</el-tag>
          </el-col>
          <el-col :span="8">
            <div style="margin-bottom: 8px; font-size: 24px" :style="{ color: appData.enable_custom_policy ? '#409eff' : '#dcdfe6' }">&#9881;</div>
            <div>自定义规则</div>
            <el-tag :type="appData.enable_custom_policy ? 'success' : 'info'" size="small" style="margin-top:8px">{{ appData.enable_custom_policy ? '已启用' : '未启用' }}</el-tag>
          </el-col>
        </el-row>
      </el-card>
    </template>
  </div>
</template>
