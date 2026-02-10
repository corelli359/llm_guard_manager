<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { scenariosApi, playgroundApi, getErrorMessage } from '../api'
import type { ScenarioApp, PlaygroundResponse, PlaygroundHistory } from '../types'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const scenarios = ref<ScenarioApp[]>([])
const loading = ref(false)
const fetchingScenarios = ref(false)
const result = ref<PlaygroundResponse | null>(null)

// Form
const formData = ref({
  app_id: '', input_prompt: '',
  use_customize_white: false, use_customize_words: true, use_customize_rule: true,
  use_vip_black: false, use_vip_white: false,
})

// History
const historyVisible = ref(false)
const historyList = ref<PlaygroundHistory[]>([])
const historyLoading = ref(false)
const detailVisible = ref(false)
const selectedHistory = ref<PlaygroundHistory | null>(null)

async function fetchScenarios() {
  fetchingScenarios.value = true
  try { scenarios.value = (await scenariosApi.getAll()).data }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '获取场景列表失败')) }
  finally { fetchingScenarios.value = false }
}

async function fetchHistory() {
  historyLoading.value = true
  try { historyList.value = (await playgroundApi.getHistory({ playground_type: 'INPUT', size: 50 })).data }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '获取历史记录失败')) }
  finally { historyLoading.value = false }
}

function openHistory() { historyVisible.value = true; fetchHistory() }

async function handleRun() {
  if (!formData.value.app_id || !formData.value.input_prompt) {
    ElMessage.warning('请选择场景并输入测试文本'); return
  }
  loading.value = true; result.value = null
  try {
    const res = await playgroundApi.testInput(formData.value)
    result.value = res.data; ElMessage.success('检测完成')
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '检测请求失败')) }
  finally { loading.value = false }
}

function handleRestore(item: PlaygroundHistory) {
  const cfg = item.config_snapshot || {}
  formData.value = {
    app_id: item.app_id, input_prompt: item.input_data.input_prompt,
    use_customize_white: cfg.use_customize_white ?? false,
    use_customize_words: cfg.use_customize_words ?? false,
    use_customize_rule: cfg.use_customize_rule ?? false,
    use_vip_black: cfg.use_vip_black ?? false,
    use_vip_white: cfg.use_vip_white ?? false,
  }
  if (item.output_data) result.value = item.output_data
  ElMessage.success('已恢复历史配置'); historyVisible.value = false
}

// PLACEHOLDER_HELPERS
function handleViewDetails(item: PlaygroundHistory) { selectedHistory.value = item; detailVisible.value = true }

function getScoreLabel(score: number) {
  if (score === -1) return { text: 'Error', type: 'danger' as const, color: '#ff4d4f', bg: '#fff2f0', border: '#ff4d4f', desc: '请求执行失败，请检查输出详情。' }
  if (score === 0) return { text: 'Pass', type: 'success' as const, color: '#52c41a', bg: '#f6ffed', border: '#52c41a', desc: '内容安全，未命中有害规则。' }
  if (score === 50) return { text: 'Rewrite', type: 'warning' as const, color: '#faad14', bg: '#fffbe6', border: '#faad14', desc: '命中部分敏感词，建议脱敏或改写后发布。' }
  if (score === 100) return { text: 'Block', type: 'danger' as const, color: '#f5222d', bg: '#fff1f0', border: '#f5222d', desc: '命中高风险敏感词，内容已被拦截。' }
  if (score === 1000) return { text: 'Manual', type: 'warning' as const, color: '#722ed1', bg: '#f9f0ff', border: '#722ed1', desc: '内容复杂或存在潜在风险，需人工审核。' }
  return { text: String(score), type: 'info' as const, color: '#666', bg: '#fafafa', border: '#d9d9d9', desc: '未知决策' }
}

onMounted(fetchScenarios)
</script>

<template>
  <div style="padding: 24px">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <div>
        <h2 style="margin: 0">输入试验场 (Input Playground)</h2>
        <p style="margin: 0; color: #666">在这里您可以模拟用户输入，测试不同场景下的安全围栏检测效果。</p>
      </div>
      <el-button @click="openHistory"><el-icon><Clock /></el-icon>历史记录</el-button>
    </div>

    <el-row :gutter="24">
      <!-- Left: Config -->
      <el-col :span="10">
        <el-card>
          <template #header><span>配置测试参数</span></template>
          <el-form label-position="top">
            <el-form-item label="选择场景 (app_id)" required>
              <el-select v-model="formData.app_id" placeholder="搜索场景..." filterable :loading="fetchingScenarios" style="width: 100%">
                <el-option v-for="s in scenarios" :key="s.app_id" :value="s.app_id" :label="`${s.app_name} (${s.app_id})`" />
              </el-select>
            </el-form-item>
            <el-form-item label="测试文本 (Input Prompt)" required>
              <el-input v-model="formData.input_prompt" type="textarea" :rows="6" placeholder="输入需要检测的内容..." />
            </el-form-item>
            <el-divider content-position="left">高级检测开关</el-divider>
            <el-row :gutter="16">
              <el-col :span="12"><el-form-item label="自定义白名单"><el-switch v-model="formData.use_customize_white" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="自定义敏感词"><el-switch v-model="formData.use_customize_words" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="自定义规则"><el-switch v-model="formData.use_customize_rule" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="VIP 黑名单"><el-switch v-model="formData.use_vip_black" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="VIP 白名单"><el-switch v-model="formData.use_vip_white" /></el-form-item></el-col>
            </el-row>
            <el-button type="primary" :loading="loading" style="width: 100%; margin-top: 16px" size="large" @click="handleRun">
              <el-icon><VideoPlay /></el-icon>开始检测
            </el-button>
          </el-form>
        </el-card>
      </el-col>

      <!-- Right: Result -->
      <el-col :span="14">
        <el-card style="min-height: 600px">
          <template #header><span>检测结果</span></template>
          <div v-if="!result && !loading" style="text-align: center; padding: 100px 0; color: #999">
            <el-icon :size="48"><VideoPlay /></el-icon>
            <p>配置参数并点击"开始检测"查看结果</p>
          </div>
          <div v-if="loading" style="text-align: center; padding: 100px 0" v-loading="true" element-loading-text="正在请求围栏服务..." />
          <template v-if="result && !loading">
            <div v-if="result.final_decision" :style="{ borderLeft: `8px solid ${getScoreLabel(result.final_decision.score).border}`, backgroundColor: getScoreLabel(result.final_decision.score).bg, padding: '16px', borderRadius: '4px', marginBottom: '16px' }">
              <h3 :style="{ color: getScoreLabel(result.final_decision.score).color, margin: '0 0 8px' }">
                {{ getScoreLabel(result.final_decision.score).text }}
              </h3>
              <p style="margin: 0 0 8px">{{ getScoreLabel(result.final_decision.score).desc }}</p>
              <el-tag :type="getScoreLabel(result.final_decision.score).type" size="small">Score: {{ result.final_decision.score }}</el-tag>
            </div>
            <el-divider content-position="left">决策详情 (all_decision_dict)</el-divider>
            <pre style="background: #f5f5f5; padding: 16px; border-radius: 4px; max-height: 300px; overflow: auto">{{ JSON.stringify(result.all_decision_dict, null, 2) }}</pre>
            <el-divider content-position="left">原始响应 (Raw Response)</el-divider>
            <pre style="background: #f5f5f5; padding: 16px; border-radius: 4px; max-height: 300px; overflow: auto">{{ JSON.stringify(result, null, 2) }}</pre>
          </template>
        </el-card>
      </el-col>
    </el-row>

    <!-- History Drawer -->
    <el-drawer v-model="historyVisible" title="历史记录 (History)" direction="rtl" size="420px">
      <div v-loading="historyLoading">
        <div v-for="item in historyList" :key="item.id" style="border-bottom: 1px solid #eee; padding: 12px 0">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px">
            <span>
              <el-tag :type="getScoreLabel(item.score).type" size="small">{{ getScoreLabel(item.score).text }}</el-tag>
              <span style="font-size: 12px; color: #999; margin-left: 8px">{{ dayjs(item.created_at).format('MM-DD HH:mm:ss') }}</span>
            </span>
            <span>
              <el-tooltip content="查看详情"><el-button link @click="handleViewDetails(item)"><el-icon><View /></el-icon></el-button></el-tooltip>
              <el-tooltip content="回填配置"><el-button link @click="handleRestore(item)"><el-icon><RefreshRight /></el-icon></el-button></el-tooltip>
            </span>
          </div>
          <div style="display: flex; justify-content: space-between">
            <el-tag size="small">{{ item.app_id }}</el-tag>
            <el-tag v-if="item.latency !== undefined" type="primary" size="small">{{ item.latency }}ms</el-tag>
          </div>
          <div style="margin-top: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 350px; color: #666; font-size: 12px">
            {{ item.input_data.input_prompt }}
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailVisible" title="历史详情 (History Details)" width="800px">
      <template v-if="selectedHistory">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="Request ID">{{ selectedHistory.request_id }}</el-descriptions-item>
          <el-descriptions-item label="App ID">{{ selectedHistory.app_id }}</el-descriptions-item>
          <el-descriptions-item label="Time">{{ dayjs(selectedHistory.created_at).format('YYYY-MM-DD HH:mm:ss') }}</el-descriptions-item>
          <el-descriptions-item label="Score"><el-tag :type="getScoreLabel(selectedHistory.score).type" size="small">{{ getScoreLabel(selectedHistory.score).text }} ({{ selectedHistory.score }})</el-tag></el-descriptions-item>
          <el-descriptions-item label="Latency (Total)">{{ selectedHistory.latency ? `${selectedHistory.latency} ms` : '-' }}</el-descriptions-item>
          <el-descriptions-item label="Latency (Upstream)">{{ selectedHistory.upstream_latency ? `${selectedHistory.upstream_latency} ms` : '-' }}</el-descriptions-item>
        </el-descriptions>
        <h4 style="margin-top: 16px">Input Prompt</h4>
        <div style="background: #f5f5f5; padding: 12px; border-radius: 4px; white-space: pre-wrap">{{ selectedHistory.input_data.input_prompt }}</div>
        <h4>Config Snapshot</h4>
        <pre style="background: #f5f5f5; padding: 12px; border-radius: 4px; max-height: 200px; overflow: auto">{{ JSON.stringify(selectedHistory.config_snapshot, null, 2) }}</pre>
        <h4>Output Response</h4>
        <pre style="background: #f5f5f5; padding: 12px; border-radius: 4px; max-height: 400px; overflow: auto">{{ JSON.stringify(selectedHistory.output_data, null, 2) }}</pre>
      </template>
    </el-dialog>
  </div>
</template>
