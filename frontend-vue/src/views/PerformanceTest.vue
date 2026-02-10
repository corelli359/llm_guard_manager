<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { scenariosApi, performanceApi, getErrorMessage } from '../api'
import type { ScenarioApp } from '../types'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

const apps = ref<ScenarioApp[]>([])
const loadingApps = ref(false)
const isRunning = ref(false)
const status = ref<any>(null)
const dryRunPassed = ref(false)
const testType = ref('STEP')

// History
const historyVisible = ref(false)
const historyList = ref<any[]>([])
const historyLoading = ref(false)
const detailVisible = ref(false)
const selectedHistory = ref<any>(null)
const detailLoading = ref(false)

let pollTimer: ReturnType<typeof setInterval> | null = null

const formData = ref({
  app_id: '', input_prompt: '',
  use_customize_white: false, use_customize_words: true, use_customize_rule: true,
  use_vip_black: false, use_vip_white: false,
  step_initial_users: 1, step_size: 5, step_duration: 10, step_max_users: 50,
  fatigue_concurrency: 20, fatigue_duration: 60,
})

const chartData = computed(() => status.value?.history || [])

function makeLatencyOption(data: any[]) {
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Avg 响应时间', 'P95 响应时间', 'P99 响应时间'] },
    grid: { left: 50, right: 20, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: data.map((_: any, i: number) => i), show: false },
    yAxis: { type: 'value', name: 'ms' },
    series: [
      { name: 'Avg 响应时间', type: 'line', data: data.map((d: any) => d.latency), smooth: true, showSymbol: false, lineStyle: { color: '#82ca9d' }, itemStyle: { color: '#82ca9d' } },
      { name: 'P95 响应时间', type: 'line', data: data.map((d: any) => d.p95_latency), smooth: true, showSymbol: false, lineStyle: { color: '#faad14', type: 'dashed' }, itemStyle: { color: '#faad14' } },
      { name: 'P99 响应时间', type: 'line', data: data.map((d: any) => d.p99_latency), smooth: true, showSymbol: false, lineStyle: { color: '#cf1322', type: 'dashed' }, itemStyle: { color: '#cf1322' } },
    ],
  }
}

function makeRpsOption(data: any[]) {
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['总吞吐量 (RPS)'] },
    grid: { left: 50, right: 20, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: data.map((_: any, i: number) => i), show: false },
    yAxis: { type: 'value' },
    series: [
      { name: '总吞吐量 (RPS)', type: 'line', data: data.map((d: any) => d.rps), smooth: true, showSymbol: false, lineStyle: { color: '#8884d8' }, itemStyle: { color: '#8884d8' } },
    ],
  }
}

// PLACEHOLDER_MORE_CHARTS
function makeUsersOption(data: any[]) {
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['虚拟用户数'] },
    grid: { left: 50, right: 20, top: 40, bottom: 30 },
    xAxis: { type: 'category', data: data.map((_: any, i: number) => i), show: false },
    yAxis: { type: 'value' },
    series: [
      { name: '虚拟用户数', type: 'line', data: data.map((d: any) => d.users), step: 'middle', showSymbol: false, lineStyle: { color: '#ff7300' }, itemStyle: { color: '#ff7300' }, areaStyle: { color: 'rgba(255,115,0,0.1)' } },
    ],
  }
}

async function fetchApps() {
  loadingApps.value = true
  try { apps.value = (await scenariosApi.getAll()).data }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '加载应用列表失败')) }
  finally { loadingApps.value = false }
}

function startPolling() { stopPolling(); pollTimer = setInterval(checkStatus, 1000) }
function stopPolling() { if (pollTimer) { clearInterval(pollTimer); pollTimer = null } }

async function checkStatus() {
  try {
    const res = await performanceApi.getStatus()
    status.value = res.data; isRunning.value = res.data.is_running
    if (!res.data.is_running && pollTimer) stopPolling()
  } catch { /* ignore */ }
}

async function handleDryRun() {
  if (!formData.value.app_id || !formData.value.input_prompt) { ElMessage.warning('请填写场景和测试文本'); return }
  const targetConfig = {
    app_id: formData.value.app_id, input_prompt: formData.value.input_prompt,
    use_customize_white: formData.value.use_customize_white, use_customize_words: formData.value.use_customize_words,
    use_customize_rule: formData.value.use_customize_rule, use_vip_black: formData.value.use_vip_black, use_vip_white: formData.value.use_vip_white,
  }
  try {
    const res = await performanceApi.dryRun(targetConfig)
    if (res.data.success) { ElMessage.success(`测试通过! 耗时: ${res.data.latency}ms`); dryRunPassed.value = true }
    else { ElMessage.error(`测试失败: ${res.data.error}`); dryRunPassed.value = false }
  } catch { ElMessage.error('验证失败，请检查表单') }
}

async function handleStart() {
  const targetConfig = {
    app_id: formData.value.app_id, input_prompt: formData.value.input_prompt,
    use_customize_white: formData.value.use_customize_white, use_customize_words: formData.value.use_customize_words,
    use_customize_rule: formData.value.use_customize_rule, use_vip_black: formData.value.use_vip_black, use_vip_white: formData.value.use_vip_white,
  }
  let stepConfig = null, fatigueConfig = null
  if (testType.value === 'STEP') {
    stepConfig = { initial_users: formData.value.step_initial_users, step_size: formData.value.step_size, step_duration: formData.value.step_duration, max_users: formData.value.step_max_users }
  } else {
    fatigueConfig = { concurrency: formData.value.fatigue_concurrency, duration: formData.value.fatigue_duration }
  }
  try {
    await performanceApi.start({ test_type: testType.value, target_config: targetConfig, step_config: stepConfig, fatigue_config: fatigueConfig })
    ElMessage.success('压测任务已启动'); isRunning.value = true; startPolling()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '启动失败')) }
}

async function handleStop() {
  try { await performanceApi.stop(); ElMessage.warning('正在停止...') }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '停止失败')) }
}

async function fetchHistory() {
  historyLoading.value = true
  try { historyList.value = (await performanceApi.getHistoryList()).data }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '获取历史记录失败')) }
  finally { historyLoading.value = false }
}

function openHistory() { historyVisible.value = true; fetchHistory() }

async function handleViewDetail(record: any) {
  detailVisible.value = true; detailLoading.value = true
  try { selectedHistory.value = (await performanceApi.getHistoryDetail(record.test_id)).data }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '加载详情失败')) }
  finally { detailLoading.value = false }
}

async function handleDeleteHistory(testId: string) {
  try { await performanceApi.deleteHistory(testId); ElMessage.success('记录已删除'); fetchHistory() }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '删除失败')) }
}

onMounted(() => { fetchApps(); checkStatus() })
onUnmounted(stopPolling)
</script>

<template>
  <div style="padding: 0 24px">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">性能与疲劳测试</h2>
      <el-button @click="openHistory"><el-icon><Clock /></el-icon>历史记录</el-button>
    </div>

    <el-row :gutter="24">
      <!-- Left Config -->
      <el-col :span="10">
        <el-card>
          <template #header><span>测试配置</span></template>
          <el-form label-position="top">
            <el-divider content-position="left">目标 (Target)</el-divider>
            <el-form-item label="选择场景 (App ID)" required>
              <el-select v-model="formData.app_id" placeholder="选择应用" filterable :loading="loadingApps" :disabled="isRunning" style="width: 100%">
                <el-option v-for="a in apps" :key="a.app_id" :value="a.app_id" :label="`${a.app_name} (${a.app_id})`" />
              </el-select>
            </el-form-item>
            <el-form-item label="测试 Prompt" required>
              <el-input v-model="formData.input_prompt" type="textarea" :rows="3" placeholder="输入用于测试的文本..." :disabled="isRunning" />
            </el-form-item>
            <el-row :gutter="16">
              <el-col :span="12"><el-form-item label="自定义白名单"><el-switch v-model="formData.use_customize_white" :disabled="isRunning" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="VIP 黑名单"><el-switch v-model="formData.use_vip_black" :disabled="isRunning" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="自定义敏感词"><el-switch v-model="formData.use_customize_words" :disabled="isRunning" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="VIP 白名单"><el-switch v-model="formData.use_vip_white" :disabled="isRunning" /></el-form-item></el-col>
            </el-row>
            <el-button style="width: 100%; margin-bottom: 24px" :disabled="isRunning" @click="handleDryRun">
              <el-icon><Connection /></el-icon>连通性测试 (Dry Run)
            </el-button>

            <el-divider content-position="left">策略 (Policy)</el-divider>
            <template v-if="dryRunPassed">
              <el-radio-group v-model="testType" style="margin-bottom: 16px">
                <el-radio-button value="STEP">阶梯测试 (Step Load)</el-radio-button>
                <el-radio-button value="FATIGUE">疲劳测试 (Fatigue)</el-radio-button>
              </el-radio-group>
              <template v-if="testType === 'STEP'">
                <el-row :gutter="16">
                  <el-col :span="12"><el-form-item label="初始并发"><el-input-number v-model="formData.step_initial_users" :min="1" :disabled="isRunning" style="width: 100%" /></el-form-item></el-col>
                  <el-col :span="12"><el-form-item label="最大并发"><el-input-number v-model="formData.step_max_users" :min="1" :disabled="isRunning" style="width: 100%" /></el-form-item></el-col>
                  <el-col :span="12"><el-form-item label="步长 (增加用户/轮)"><el-input-number v-model="formData.step_size" :min="1" :disabled="isRunning" style="width: 100%" /></el-form-item></el-col>
                  <el-col :span="12"><el-form-item label="步长间隔 (秒)"><el-input-number v-model="formData.step_duration" :min="1" :disabled="isRunning" style="width: 100%" /></el-form-item></el-col>
                </el-row>
              </template>
              <template v-else>
                <el-row :gutter="16">
                  <el-col :span="12"><el-form-item label="并发数 (Users)"><el-input-number v-model="formData.fatigue_concurrency" :min="1" :disabled="isRunning" style="width: 100%" /></el-form-item></el-col>
                  <el-col :span="12"><el-form-item label="持续时间 (秒)"><el-input-number v-model="formData.fatigue_duration" :min="1" :disabled="isRunning" style="width: 100%" /></el-form-item></el-col>
                </el-row>
              </template>
              <el-button :type="isRunning ? 'danger' : 'primary'" style="width: 100%" size="large" @click="isRunning ? handleStop() : handleStart()">
                <el-icon><VideoPlay v-if="!isRunning" /><VideoPause v-else /></el-icon>
                {{ isRunning ? '停止测试' : '开始测试' }}
              </el-button>
            </template>
            <div v-else style="text-align: center; color: #999; padding: 20px 0">
              <el-icon :size="24"><CircleClose /></el-icon>
              <p>请先通过连通性测试以解锁压测配置</p>
            </div>
          </el-form>
        </el-card>
      </el-col>

      <!-- Right Monitor -->
      <el-col :span="14">
        <el-card>
          <template #header>
            <div style="display: flex; align-items: center; gap: 8px">
              <span>实时监控</span>
              <el-tag v-if="isRunning" type="primary" size="small" effect="dark">Running</el-tag>
              <el-tag v-else-if="status?.total_requests > 0" type="info" size="small">Stopped</el-tag>
            </div>
          </template>
          <el-row :gutter="16" style="margin-bottom: 24px">
            <el-col :span="4"><el-statistic title="运行时长 (s)" :value="status?.duration || 0" /></el-col>
            <el-col :span="4"><el-statistic title="当前虚拟用户" :value="status?.current_users || 0" :value-style="{ color: '#1890ff' }" /></el-col>
            <el-col :span="4"><el-statistic title="实时 RPS" :value="status?.current_rps || 0" :precision="1" /></el-col>
            <el-col :span="4"><el-statistic title="Avg 响应 (ms)" :value="status?.avg_latency || 0" :precision="1" :value-style="{ color: (status?.avg_latency || 0) > 1000 ? '#cf1322' : '#3f8600' }" /></el-col>
            <el-col :span="4"><el-statistic title="P95 (ms)" :value="status?.p95_latency || 0" :precision="1" :value-style="{ color: '#faad14' }" /></el-col>
            <el-col :span="4"><el-statistic title="P99 (ms)" :value="status?.p99_latency || 0" :precision="1" :value-style="{ color: '#cf1322' }" /></el-col>
          </el-row>
          <el-row :gutter="16" style="margin-bottom: 24px">
            <el-col :span="8"><el-statistic title="总请求量" :value="status?.total_requests || 0" /></el-col>
            <el-col :span="8"><el-statistic title="成功请求数" :value="status?.success_requests || 0" :value-style="{ color: '#3f8600' }" /></el-col>
            <el-col :span="8"><el-statistic title="失败请求数" :value="status?.error_requests || 0" :value-style="{ color: '#cf1322' }" /></el-col>
          </el-row>
          <el-divider />
          <h4>响应时间 (Response Time)</h4>
          <v-chart :option="makeLatencyOption(chartData)" style="height: 200px" autoresize />
          <el-row :gutter="16">
            <el-col :span="12">
              <h4>总吞吐量 (Total Throughput)</h4>
              <v-chart :option="makeRpsOption(chartData)" style="height: 200px" autoresize />
            </el-col>
            <el-col :span="12">
              <h4>虚拟用户数 (Virtual Users)</h4>
              <v-chart :option="makeUsersOption(chartData)" style="height: 200px" autoresize />
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <!-- History List Drawer -->
    <el-drawer v-model="historyVisible" title="测试历史记录" direction="rtl" size="600px">
      <el-table :data="historyList" v-loading="historyLoading" row-key="test_id">
        <el-table-column prop="start_time" label="时间" :formatter="(_r: any, _c: any, v: string) => dayjs(v).format('MM-DD HH:mm')" />
        <el-table-column prop="app_id" label="应用" />
        <el-table-column prop="test_type" label="类型">
          <template #default="{ row }"><el-tag size="small">{{ row.test_type }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时(s)" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }"><el-tag :type="row.status === 'COMPLETED' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag></template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" @click="handleViewDetail(row)"><el-icon><View /></el-icon></el-button>
            <el-popconfirm title="确定删除?" @confirm="handleDeleteHistory(row.test_id)">
              <template #reference><el-button size="small" type="danger"><el-icon><Delete /></el-icon></el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-drawer>

    <!-- History Detail Drawer -->
    <el-drawer v-model="detailVisible" title="测试详情回顾" direction="rtl" size="800px">
      <div v-if="detailLoading" v-loading="true" style="height: 200px" />
      <template v-else-if="selectedHistory">
        <template v-if="selectedHistory.analysis">
          <el-alert :title="`综合评分: ${selectedHistory.analysis.score} 分`" :description="selectedHistory.analysis.conclusion" :type="selectedHistory.analysis.score >= 80 ? 'success' : selectedHistory.analysis.score >= 60 ? 'warning' : 'error'" show-icon style="margin-bottom: 16px" />
          <div v-if="selectedHistory.analysis.suggestions?.length" style="margin-bottom: 16px">
            <h4>优化建议:</h4>
            <ul><li v-for="(s, i) in selectedHistory.analysis.suggestions" :key="i">{{ s }}</li></ul>
          </div>
        </template>
        <el-descriptions title="基础信息" :column="2" border style="margin-bottom: 16px">
          <el-descriptions-item label="Test ID">{{ selectedHistory.meta.test_id }}</el-descriptions-item>
          <el-descriptions-item label="App ID">{{ selectedHistory.meta.app_id }}</el-descriptions-item>
          <el-descriptions-item label="Start Time">{{ dayjs(selectedHistory.meta.start_time).format('YYYY-MM-DD HH:mm:ss') }}</el-descriptions-item>
          <el-descriptions-item label="Duration">{{ selectedHistory.meta.duration }} s</el-descriptions-item>
          <el-descriptions-item label="Total Requests">{{ selectedHistory.stats.total_requests }}</el-descriptions-item>
          <el-descriptions-item label="Max RPS">{{ selectedHistory.stats.max_rps }}</el-descriptions-item>
          <el-descriptions-item label="Avg Latency">{{ selectedHistory.stats.avg_latency }} ms</el-descriptions-item>
          <el-descriptions-item label="Error Rate">{{ selectedHistory.stats.total_requests > 0 ? (selectedHistory.stats.error_requests / selectedHistory.stats.total_requests * 100).toFixed(2) : 0 }}%</el-descriptions-item>
        </el-descriptions>
        <h4>RPS 趋势回放</h4>
        <v-chart :option="makeRpsOption(selectedHistory.history)" style="height: 250px" autoresize />
        <h4>延迟趋势回放</h4>
        <v-chart :option="makeLatencyOption(selectedHistory.history)" style="height: 250px" autoresize />
        <el-card shadow="never" style="margin-top: 16px">
          <template #header><span>详细配置</span></template>
          <pre style="max-height: 200px; overflow: auto; background: #f5f5f5; padding: 8px">{{ JSON.stringify(selectedHistory.config, null, 2) }}</pre>
        </el-card>
      </template>
    </el-drawer>
  </div>
</template>
