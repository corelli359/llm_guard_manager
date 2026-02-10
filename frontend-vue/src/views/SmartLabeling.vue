<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { stagingApi, metaTagsApi, getErrorMessage } from '../api'
import type { MetaTag } from '../types'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const activeTab = ref('keywords')
const data = ref<any[]>([])
const rulesData = ref<any[]>([])
const loading = ref(false)
const statusFilter = ref('CLAIMED')
const selectedRows = ref<any[]>([])
const syncing = ref(false)
const metaTags = ref<MetaTag[]>([])
const myTasksStats = ref<any>(null)
const taskOverview = ref<any>(null)
const countdown = ref('')
const claiming = ref(false)
const showMyTasks = ref(true)
const userEdits = ref<Record<string, any>>({})

const riskOptions = ['High', 'Medium', 'Low']
const strategyOptions = ['BLOCK', 'PASS', 'REWRITE']
const userRole = localStorage.getItem('user_role')
const isAdmin = userRole === 'ADMIN'

let countdownTimer: ReturnType<typeof setInterval> | null = null

const selectedIds = computed(() => selectedRows.value.map((r: any) => r.id))

async function fetchMetaTags() {
  try { metaTags.value = (await metaTagsApi.getAll()).data.filter((t: MetaTag) => t.is_active) }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '获取标签列表失败')) }
}

async function fetchData() {
  loading.value = true
  try {
    if (activeTab.value === 'keywords') {
      data.value = (await stagingApi.listKeywords(statusFilter.value, showMyTasks.value && statusFilter.value === 'CLAIMED')).data
    } else {
      rulesData.value = (await stagingApi.listRules(statusFilter.value, showMyTasks.value && statusFilter.value === 'CLAIMED')).data
    }
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '获取数据失败')) }
  finally { loading.value = false }
}

async function fetchMyTasksStats() {
  try { myTasksStats.value = (await stagingApi.getMyTasksStats(activeTab.value)).data } catch { /* ignore */ }
}

async function fetchTaskOverview() {
  try { taskOverview.value = (await stagingApi.getTaskOverview(activeTab.value)).data } catch { /* ignore */ }
}

function startCountdown() {
  if (countdownTimer) clearInterval(countdownTimer)
  countdownTimer = setInterval(() => {
    if (!myTasksStats.value?.expires_at) { countdown.value = ''; return }
    const dist = new Date(myTasksStats.value.expires_at).getTime() - Date.now()
    if (dist < 0) { countdown.value = '已超时'; if (countdownTimer) clearInterval(countdownTimer) }
    else {
      const m = Math.floor((dist % 3600000) / 60000)
      const s = Math.floor((dist % 60000) / 1000)
      countdown.value = `${m}:${s.toString().padStart(2, '0')}`
    }
  }, 1000)
}

async function handleClaimBatch() {
  claiming.value = true
  try {
    const res = await stagingApi.claimBatch(50, activeTab.value)
    ElMessage.success(`成功领取 ${res.data.claimed_count} 条任务`)
    statusFilter.value = 'CLAIMED'; showMyTasks.value = true
    fetchData(); fetchMyTasksStats(); fetchTaskOverview()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '领取任务失败')) }
  finally { claiming.value = false }
}

// PLACEHOLDER_REVIEW
async function handleReviewKeyword(record: any, newStatus: string) {
  try {
    const edits = userEdits.value[record.id] || {}
    await stagingApi.reviewKeyword(record.id, {
      final_tag: edits.final_tag || record.final_tag || record.predicted_tag,
      final_risk: edits.final_risk || record.final_risk || record.predicted_risk,
      status: newStatus,
    })
    ElMessage.success('操作成功')
    delete userEdits.value[record.id]
    fetchData(); fetchMyTasksStats(); fetchTaskOverview()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '操作失败')) }
}

async function handleReviewRule(record: any, newStatus: string) {
  try {
    const edits = userEdits.value[record.id] || {}
    await stagingApi.reviewRule(record.id, {
      final_strategy: edits.final_strategy || record.final_strategy || record.predicted_strategy,
      status: newStatus,
    })
    ElMessage.success('操作成功')
    delete userEdits.value[record.id]
    fetchData(); fetchMyTasksStats(); fetchTaskOverview()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '操作失败')) }
}

async function handleDeleteItem(id: string) {
  try {
    if (activeTab.value === 'keywords') await stagingApi.deleteKeyword(id)
    else await stagingApi.deleteRule(id)
    ElMessage.success('已删除'); fetchData()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '删除失败')) }
}

async function handleSync() {
  if (selectedIds.value.length === 0) return
  syncing.value = true
  try {
    const res = activeTab.value === 'keywords'
      ? await stagingApi.syncKeywords(selectedIds.value)
      : await stagingApi.syncRules(selectedIds.value)
    ElMessage.success(`成功同步 ${res.data.synced_count} 条数据入库`)
    selectedRows.value = []; fetchData(); fetchTaskOverview()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '同步失败')) }
  finally { syncing.value = false }
}

async function handleSyncAll() {
  syncing.value = true
  try {
    const allIds = (activeTab.value === 'keywords' ? data.value : rulesData.value).map((i: any) => i.id)
    if (allIds.length === 0) { ElMessage.warning('没有可入库的数据'); return }
    const res = activeTab.value === 'keywords'
      ? await stagingApi.syncKeywords(allIds)
      : await stagingApi.syncRules(allIds)
    ElMessage.success(`成功同步 ${res.data.synced_count} 条数据入库`)
    selectedRows.value = []; fetchData(); fetchTaskOverview()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '同步失败')) }
  finally { syncing.value = false }
}

async function handleBatchReview(newStatus: string) {
  if (selectedIds.value.length === 0) return
  syncing.value = true
  try {
    const items = selectedRows.value.map((record: any) => {
      const edits = userEdits.value[record.id] || {}
      if (activeTab.value === 'keywords') {
        return { id: record.id, final_tag: edits.final_tag || record.final_tag || record.predicted_tag, final_risk: edits.final_risk || record.final_risk || record.predicted_risk, status: newStatus }
      } else {
        return { id: record.id, final_strategy: edits.final_strategy || record.final_strategy || record.predicted_strategy, status: newStatus }
      }
    })
    const res = activeTab.value === 'keywords'
      ? await stagingApi.batchReviewKeywords(items)
      : await stagingApi.batchReviewRules(items)
    ElMessage.success(`成功${newStatus === 'REVIEWED' ? '确认' : '忽略'} ${res.data.success_count} 条任务`)
    selectedIds.value.forEach(id => delete userEdits.value[id])
    selectedRows.value = []; fetchData(); fetchMyTasksStats(); fetchTaskOverview()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '批量操作失败')) }
  finally { syncing.value = false }
}

async function handleReleaseExpired() {
  try {
    const res = await stagingApi.releaseExpired()
    ElMessage.success(`已释放 ${res.data.released_keywords + res.data.released_rules} 条超时任务`)
    fetchData(); fetchMyTasksStats(); fetchTaskOverview()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '释放失败')) }
}

function handleSelectionChange(rows: any[]) { selectedRows.value = rows }
function isRowSelectable(row: any) {
  return (statusFilter.value === 'REVIEWED' && isAdmin) || (statusFilter.value === 'CLAIMED' && row.status === 'CLAIMED')
}
function getStatusType(s: string) {
  const m: Record<string, string> = { PENDING: '', CLAIMED: 'warning', REVIEWED: 'success', SYNCED: 'primary', IGNORED: 'info' }
  return m[s] || 'info'
}
function setEdit(id: string, field: string, val: string) {
  userEdits.value = { ...userEdits.value, [id]: { ...userEdits.value[id], [field]: val } }
}

const taskProgress = computed(() => {
  if (!myTasksStats.value || myTasksStats.value.claimed_count === 0) return null
  const total = myTasksStats.value.claimed_count + myTasksStats.value.reviewed_count + myTasksStats.value.ignored_count
  const done = myTasksStats.value.reviewed_count + myTasksStats.value.ignored_count
  return { total, done, pct: total > 0 ? Math.round((done / total) * 100) : 0 }
})

watch([activeTab, statusFilter, showMyTasks], () => { selectedRows.value = []; fetchData(); fetchMyTasksStats(); fetchTaskOverview() })
watch(() => myTasksStats.value?.expires_at, startCountdown)

onMounted(() => { fetchMetaTags(); fetchData(); fetchMyTasksStats(); fetchTaskOverview() })
onUnmounted(() => { if (countdownTimer) clearInterval(countdownTimer) })
</script>

<template>
  <div style="padding: 24px">
    <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
      <h2 style="margin: 0">智能标注与审核 (Smart Labeling)</h2>
      <el-button v-if="isAdmin" @click="handleReleaseExpired">释放超时任务</el-button>
    </div>

    <!-- Task Overview -->
    <el-card v-if="taskOverview" shadow="never" style="margin-bottom: 16px">
      <el-row :gutter="16">
        <el-col :span="4"><el-statistic title="总任务数" :value="taskOverview.total_count" /></el-col>
        <el-col :span="4"><el-statistic title="待认领" :value="taskOverview.pending_count" :value-style="{ color: '#1890ff' }" /></el-col>
        <el-col :span="4"><el-statistic title="已认领" :value="taskOverview.claimed_count" :value-style="{ color: '#fa8c16' }" /></el-col>
        <el-col :span="4"><el-statistic title="已审核" :value="taskOverview.reviewed_count" :value-style="{ color: '#52c41a' }" /></el-col>
        <el-col :span="4"><el-statistic title="已入库" :value="taskOverview.synced_count" :value-style="{ color: '#722ed1' }" /></el-col>
        <el-col :span="4"><el-statistic title="已忽略" :value="taskOverview.ignored_count" :value-style="{ color: '#999' }" /></el-col>
      </el-row>
    </el-card>

    <!-- Task Progress -->
    <el-card shadow="never" style="margin-bottom: 16px">
      <template v-if="!taskProgress">
        <div style="display: flex; align-items: center; gap: 12px">
          <el-icon :size="20"><Document /></el-icon>
          <span>当前没有认领的任务</span>
          <el-button type="primary" :loading="claiming" @click="handleClaimBatch">领取新任务 (50条)</el-button>
        </div>
      </template>
      <template v-else>
        <el-row :gutter="24" style="margin-bottom: 12px">
          <el-col :span="4"><el-statistic title="当前批次进度" :value="taskProgress.done" :suffix="`/ ${taskProgress.total}`" /></el-col>
          <el-col :span="4"><el-statistic title="剩余时间" :value="countdown" :value-style="{ color: countdown === '已超时' ? '#cf1322' : '#3f8600' }" /></el-col>
          <el-col :span="4"><el-statistic title="待标注" :value="myTasksStats?.claimed_count" /></el-col>
          <el-col :span="4"><el-statistic title="已完成" :value="myTasksStats?.reviewed_count" :value-style="{ color: '#3f8600' }" /></el-col>
          <el-col :span="4"><el-statistic title="已忽略" :value="myTasksStats?.ignored_count" :value-style="{ color: '#999' }" /></el-col>
        </el-row>
        <el-progress :percentage="taskProgress.pct" :status="taskProgress.pct === 100 ? 'success' : undefined" />
        <el-alert v-if="countdown === '已超时'" title="任务已超时，未完成的任务将被释放" type="warning" show-icon closable style="margin-top: 8px" />
      </template>
    </el-card>

    <!-- Help -->
    <el-alert title="操作指引" type="info" show-icon :closable="false" style="margin-bottom: 16px">
      <template #default>
        <ul style="padding-left: 20px; margin: 0">
          <li><strong>领取任务</strong>: 点击"领取新任务"按钮，一次领取50条待标注数据，30分钟内完成</li>
          <li><strong>确认</strong>: 认可模型结果或已修正数据，标记为"已审核"</li>
          <li><strong>忽略</strong>: 认为数据无效，标记为"已忽略"</li>
          <li><strong>入库</strong>: (仅管理员) 批量将"已审核"的数据写入正式环境</li>
        </ul>
      </template>
    </el-alert>

    <!-- Status Filter -->
    <el-radio-group v-model="statusFilter" style="margin-bottom: 16px">
      <el-radio-button value="CLAIMED">我的任务</el-radio-button>
      <el-radio-button value="PENDING">待认领</el-radio-button>
      <el-radio-button value="REVIEWED">已审核</el-radio-button>
      <el-radio-button v-if="isAdmin" value="SYNCED">已入库</el-radio-button>
      <el-radio-button value="IGNORED">已忽略</el-radio-button>
    </el-radio-group>

    <!-- Batch Actions -->
    <div v-if="(statusFilter === 'CLAIMED' && selectedIds.length > 0) || (isAdmin && statusFilter === 'REVIEWED')" style="margin-bottom: 16px; padding: 12px 16px; background: #f0f2f5; border-radius: 4px; display: flex; gap: 8px">
      <template v-if="statusFilter === 'CLAIMED' && selectedIds.length > 0">
        <el-button type="primary" :loading="syncing" @click="handleBatchReview('REVIEWED')"><el-icon><Check /></el-icon>批量确认 ({{ selectedIds.length }})</el-button>
        <el-button type="danger" :loading="syncing" @click="handleBatchReview('IGNORED')"><el-icon><Close /></el-icon>批量忽略 ({{ selectedIds.length }})</el-button>
      </template>
      <template v-if="isAdmin && statusFilter === 'REVIEWED'">
        <el-button v-if="selectedIds.length > 0" type="primary" :loading="syncing" @click="handleSync"><el-icon><Upload /></el-icon>批量入库 ({{ selectedIds.length }})</el-button>
        <el-popconfirm :title="`确定要将当前所有已审核数据入库吗？共 ${activeTab === 'keywords' ? data.length : rulesData.length} 条`" @confirm="handleSyncAll">
          <template #reference><el-button :loading="syncing"><el-icon><Upload /></el-icon>全量入库 ({{ activeTab === 'keywords' ? data.length : rulesData.length }})</el-button></template>
        </el-popconfirm>
      </template>
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" type="card">
      <el-tab-pane label="敏感词审核" name="keywords">
        <el-table :data="data" v-loading="loading" row-key="id" @selection-change="handleSelectionChange">
          <el-table-column v-if="(statusFilter === 'REVIEWED' && isAdmin) || statusFilter === 'CLAIMED'" type="selection" :selectable="isRowSelectable" width="50" />
          <el-table-column prop="keyword" label="敏感词" />
          <el-table-column label="模型预测">
            <template #default="{ row }">
              <el-tag size="small">{{ row.predicted_tag }}</el-tag>
              <el-tag type="warning" size="small" style="margin-left: 4px">{{ row.predicted_risk }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="人工修正 (Final)" min-width="200">
            <template #default="{ row }">
              <div style="display: flex; flex-direction: column; gap: 4px">
                <el-select :model-value="userEdits[row.id]?.final_tag || row.final_tag || row.predicted_tag" size="small" :disabled="row.status !== 'CLAIMED'" filterable style="width: 180px" @change="(v: string) => setEdit(row.id, 'final_tag', v)">
                  <el-option v-for="t in metaTags" :key="t.tag_code" :value="t.tag_code" :label="`${t.tag_code} - ${t.tag_name}`" />
                </el-select>
                <el-select :model-value="userEdits[row.id]?.final_risk || row.final_risk || row.predicted_risk" size="small" :disabled="row.status !== 'CLAIMED'" style="width: 180px" @change="(v: string) => setEdit(row.id, 'final_risk', v)">
                  <el-option v-for="r in riskOptions" :key="r" :value="r" :label="r" />
                </el-select>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
              <el-tag v-if="row.is_modified" type="warning" size="small" style="margin-left: 4px">Modified</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="审计信息" width="140">
            <template #default="{ row }">
              <el-tooltip v-if="row.annotator" :content="dayjs(row.annotated_at).format('YYYY-MM-DD HH:mm')"><el-tag size="small"><el-icon><User /></el-icon>{{ row.annotator }}</el-tag></el-tooltip>
              <el-tooltip v-else-if="row.claimed_by" :content="`认领于 ${dayjs(row.claimed_at).format('YYYY-MM-DD HH:mm')}`"><el-tag type="warning" size="small"><el-icon><User /></el-icon>{{ row.claimed_by }}</el-tag></el-tooltip>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140">
            <template #default="{ row }">
              <template v-if="row.status === 'CLAIMED'">
                <el-tooltip content="确认通过"><el-button type="primary" size="small" @click="handleReviewKeyword(row, 'REVIEWED')"><el-icon><Check /></el-icon></el-button></el-tooltip>
                <el-tooltip content="忽略"><el-button type="danger" size="small" @click="handleReviewKeyword(row, 'IGNORED')"><el-icon><Close /></el-icon></el-button></el-tooltip>
              </template>
              <el-popconfirm v-if="row.status === 'IGNORED'" title="确定彻底删除?" @confirm="handleDeleteItem(row.id)">
                <template #reference><el-button type="danger" size="small"><el-icon><Delete /></el-icon>删除</el-button></template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="规则审核" name="rules">
        <el-table :data="rulesData" v-loading="loading" row-key="id" @selection-change="handleSelectionChange">
          <el-table-column v-if="(statusFilter === 'REVIEWED' && isAdmin) || statusFilter === 'CLAIMED'" type="selection" :selectable="isRowSelectable" width="50" />
          <el-table-column label="标签" prop="tag_code">
            <template #default="{ row }"><el-tag type="primary" size="small">{{ row.tag_code }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="extra_condition" label="额外条件">
            <template #default="{ row }">{{ row.extra_condition || '-' }}</template>
          </el-table-column>
          <el-table-column label="模型预测">
            <template #default="{ row }"><el-tag size="small">{{ row.predicted_strategy }}</el-tag></template>
          </el-table-column>
          <el-table-column label="人工修正 (Final)" width="150">
            <template #default="{ row }">
              <el-select :model-value="userEdits[row.id]?.final_strategy || row.final_strategy || row.predicted_strategy" size="small" :disabled="row.status !== 'CLAIMED'" style="width: 120px" @change="(v: string) => setEdit(row.id, 'final_strategy', v)">
                <el-option v-for="s in strategyOptions" :key="s" :value="s" :label="s" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
              <el-tag v-if="row.is_modified" type="warning" size="small" style="margin-left: 4px">Modified</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="审计信息" width="140">
            <template #default="{ row }">
              <el-tooltip v-if="row.annotator" :content="dayjs(row.annotated_at).format('YYYY-MM-DD HH:mm')"><el-tag size="small"><el-icon><User /></el-icon>{{ row.annotator }}</el-tag></el-tooltip>
              <el-tooltip v-else-if="row.claimed_by" :content="`认领于 ${dayjs(row.claimed_at).format('YYYY-MM-DD HH:mm')}`"><el-tag type="warning" size="small"><el-icon><User /></el-icon>{{ row.claimed_by }}</el-tag></el-tooltip>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140">
            <template #default="{ row }">
              <template v-if="row.status === 'CLAIMED'">
                <el-tooltip content="确认通过"><el-button type="primary" size="small" @click="handleReviewRule(row, 'REVIEWED')"><el-icon><Check /></el-icon></el-button></el-tooltip>
                <el-tooltip content="忽略"><el-button type="danger" size="small" @click="handleReviewRule(row, 'IGNORED')"><el-icon><Close /></el-icon></el-button></el-tooltip>
              </template>
              <el-popconfirm v-if="row.status === 'IGNORED'" title="确定彻底删除?" @confirm="handleDeleteItem(row.id)">
                <template #reference><el-button type="danger" size="small"><el-icon><Delete /></el-icon>删除</el-button></template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
