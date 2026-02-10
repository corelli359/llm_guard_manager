<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ScenarioKeywordsTab from '../components/ScenarioKeywordsTab.vue'
import ScenarioRulesTab from '../components/ScenarioRulesTab.vue'
import { usePermissionStore } from '../stores/permission'

const route = useRoute()
const router = useRouter()
const permStore = usePermissionStore()
const appId = computed(() => route.params.appId as string)

const currentScenarioId = ref('')
const searchScenarioId = ref('')
const activeMode = ref<'custom' | 'super'>('custom')
const activeTab = ref('keywords')

onMounted(() => {
  if (appId.value) { currentScenarioId.value = appId.value; searchScenarioId.value = appId.value }
  const modeParam = route.query.mode as string
  if (modeParam === 'custom' || modeParam === 'super') activeMode.value = modeParam
  const tabParam = route.query.tab as string
  if (tabParam) activeTab.value = tabParam
})

function handleSearch() {
  if (searchScenarioId.value.trim()) currentScenarioId.value = searchScenarioId.value.trim()
  else ElMessage.warning('请输入场景 ID')
}

const canKeywords = computed(() => currentScenarioId.value
  ? permStore.hasPermission('scenario_keywords') || permStore.hasScenarioPermission(currentScenarioId.value, 'scenario_keywords')
  : false)
const canPolicies = computed(() => currentScenarioId.value
  ? permStore.hasPermission('scenario_policies') || permStore.hasScenarioPermission(currentScenarioId.value, 'scenario_policies')
  : false)
const hasAnyAccess = computed(() => canKeywords.value || canPolicies.value)

watch([currentScenarioId, canKeywords, canPolicies], () => {
  if (currentScenarioId.value && !route.query.tab) {
    if (canKeywords.value) activeTab.value = 'keywords'
    else if (canPolicies.value) activeTab.value = 'rules'
  }
})
</script>

<template>
  <div style="padding: 24px">
    <el-button v-if="appId" @click="router.push(`/apps/${appId}`)" style="margin-bottom:16px">返回应用概览</el-button>
    <h2>场景策略管理 {{ appId ? `- ${appId}` : '' }}</h2>

    <el-card v-if="!appId" style="margin-bottom:16px">
      <template #header>选择场景</template>
      <div style="display:flex;gap:8px;align-items:center">
        <span>场景 ID:</span>
        <el-input v-model="searchScenarioId" placeholder="请输入场景 ID" style="flex:1" @keyup.enter="handleSearch" />
        <el-button type="primary" @click="handleSearch">加载策略</el-button>
      </div>
    </el-card>

    <el-result v-if="currentScenarioId && !hasAnyAccess" icon="warning" title="权限不足" sub-title="您没有该场景的敏感词管理或策略管理权限">
      <template #extra><el-button v-if="appId" type="primary" @click="router.back()">返回</el-button></template>
    </el-result>

    <el-tabs v-if="currentScenarioId && hasAnyAccess" v-model="activeMode" type="card">
      <el-tab-pane label="自定义模式管理" name="custom">
        <el-tabs v-model="activeTab">
          <el-tab-pane v-if="canKeywords" label="敏感词管理（黑名单/白名单）" name="keywords">
            <ScenarioKeywordsTab :scenario-id="currentScenarioId" mode="custom" />
          </el-tab-pane>
          <el-tab-pane v-if="canPolicies" label="规则管理" name="rules">
            <ScenarioRulesTab :scenario-id="currentScenarioId" :rule-mode="1" mode-name="自定义模式" />
          </el-tab-pane>
        </el-tabs>
      </el-tab-pane>
      <el-tab-pane label="超级模式管理" name="super">
        <el-tabs v-model="activeTab">
          <el-tab-pane v-if="canKeywords" label="敏感词管理（黑名单/白名单）" name="keywords">
            <ScenarioKeywordsTab :scenario-id="currentScenarioId" mode="super" />
          </el-tab-pane>
          <el-tab-pane v-if="canPolicies" label="规则管理" name="rules">
            <ScenarioRulesTab :scenario-id="currentScenarioId" :rule-mode="0" mode-name="超级模式" />
          </el-tab-pane>
        </el-tabs>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
