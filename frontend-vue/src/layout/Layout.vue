<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePermissionStore } from '../stores/permission'

const route = useRoute()
const router = useRouter()
const permStore = usePermissionStore()
const isCollapse = ref(false)

onMounted(() => { permStore.fetchPermissions() })

const activeMenu = computed(() => route.path)
const userId = computed(() => localStorage.getItem('user_id') || 'Unknown')
const currentAppId = computed(() => localStorage.getItem('current_app_id') || '')

const showSmartLabeling = computed(() =>
  permStore.hasPermission('smart_labeling') || permStore.hasRole(['ANNOTATOR'])
)
const showAnnotatorStats = computed(() =>
  permStore.hasPermission('annotator_stats') || permStore.hasRole(['SYSTEM_ADMIN'])
)
const showSystemMgmt = computed(() =>
  permStore.hasPermission('user_management') || permStore.hasPermission('audit_logs')
)
const showGlobalConfig = computed(() =>
  permStore.hasPermission('app_management') || permStore.hasPermission('tag_management') ||
  permStore.hasPermission('keyword_management') || permStore.hasPermission('policy_management')
)
const showMyScenarios = computed(() =>
  permStore.hasRole(['SCENARIO_ADMIN', 'ANNOTATOR'])
)
const showCurrentApp = computed(() => !!currentAppId.value)

function selectApp(appId: string) {
  localStorage.setItem('current_app_id', appId)
  router.push(`/apps/${appId}`)
}

function logout() {
  localStorage.clear()
  window.location.href = 'https://llmsafe.kkrrc-359.top/portal/'
}
</script>

<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo">
        <span v-if="!isCollapse">LLM Guard</span>
        <span v-else>LG</span>
      </div>
      <el-menu router :default-active="activeMenu" :collapse="isCollapse"
        background-color="#001529" text-color="rgba(255,255,255,0.65)" active-text-color="#fff">

        <!-- Smart Labeling -->
        <el-menu-item v-if="showSmartLabeling" index="/smart-labeling">
          <el-icon><EditPen /></el-icon><span>智能标注</span>
        </el-menu-item>
        <el-menu-item v-if="showAnnotatorStats" index="/annotator-stats">
          <el-icon><DataAnalysis /></el-icon><span>标注统计</span>
        </el-menu-item>

        <!-- System Management -->
        <el-sub-menu v-if="showSystemMgmt" index="sys">
          <template #title><el-icon><Setting /></el-icon><span>系统管理</span></template>
          <el-menu-item v-if="permStore.hasPermission('user_management')" index="/users">用户管理</el-menu-item>
          <el-menu-item v-if="permStore.hasPermission('user_management')" index="/roles">角色管理</el-menu-item>
          <el-menu-item v-if="permStore.hasPermission('audit_logs')" index="/audit-logs">审计日志</el-menu-item>
        </el-sub-menu>

        <!-- Global Config -->
        <el-sub-menu v-if="showGlobalConfig" index="global">
          <template #title><el-icon><Grid /></el-icon><span>全局配置</span></template>
          <el-menu-item index="/apps">场景管理</el-menu-item>
          <el-menu-item index="/tags">标签管理</el-menu-item>
          <el-menu-item index="/global-keywords">全局敏感词</el-menu-item>
          <el-menu-item index="/global-policies">全局策略</el-menu-item>
        </el-sub-menu>

        <!-- Testing Tools -->
        <el-sub-menu index="tools">
          <template #title><el-icon><Cpu /></el-icon><span>测试工具</span></template>
          <el-menu-item index="/playground">输入试验场</el-menu-item>
          <el-menu-item index="/performance">性能测试</el-menu-item>
        </el-sub-menu>

        <!-- My Scenarios -->
        <el-menu-item v-if="showMyScenarios" index="/my-scenarios">
          <el-icon><Folder /></el-icon><span>我的场景</span>
        </el-menu-item>

        <!-- Current App -->
        <template v-if="showCurrentApp">
          <el-divider style="margin: 8px 0; border-color: rgba(255,255,255,0.15)" />
          <el-sub-menu index="current-app">
            <template #title><el-icon><Monitor /></el-icon><span>{{ currentAppId }}</span></template>
            <el-menu-item :index="`/apps/${currentAppId}`">应用概览</el-menu-item>
            <el-menu-item :index="`/apps/${currentAppId}/keywords`">场景敏感词</el-menu-item>
            <el-menu-item :index="`/apps/${currentAppId}/policies`">场景策略</el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <el-icon class="collapse-btn" @click="isCollapse = !isCollapse"><Fold v-if="!isCollapse" /><Expand v-else /></el-icon>
        <div class="header-right">
          <span style="margin-right: 16px; color: #666">{{ userId }}</span>
          <el-button link type="primary" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout-container { height: 100vh; }
.aside { background-color: #001529; overflow-y: auto; transition: width 0.3s; }
.logo { height: 60px; line-height: 60px; text-align: center; font-size: 18px; font-weight: bold; color: #fff; background: #002140; }
.header { background: #fff; border-bottom: 1px solid #e8e8e8; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; }
.header-right { display: flex; align-items: center; }
.collapse-btn { cursor: pointer; font-size: 20px; }
</style>
