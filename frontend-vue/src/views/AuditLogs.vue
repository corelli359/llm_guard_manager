<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { auditLogsApi, getErrorMessage } from '../api'
import type { AuditLog } from '../types'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const logs = ref<AuditLog[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const detailDrawerOpen = ref(false)
const selectedLog = ref<AuditLog | null>(null)

// Filter form
const filterUsername = ref('')
const filterAction = ref('')
const filterResourceType = ref('')
const filterScenarioId = ref('')
const filterDateRange = ref<[Date, Date] | null>(null)

async function fetchLogs(filters: any = {}) {
  loading.value = true
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      ...filters,
    }
    const res = await auditLogsApi.queryLogs(params)
    logs.value = res.data.items || res.data
    total.value = res.data.total || res.data.length
  } catch (e: any) {
    ElMessage.error(getErrorMessage(e, '获取审计日志失败'))
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  const filters: any = {}
  if (filterUsername.value) filters.username = filterUsername.value
  if (filterAction.value) filters.action = filterAction.value
  if (filterResourceType.value) filters.resource_type = filterResourceType.value
  if (filterScenarioId.value) filters.scenario_id = filterScenarioId.value
  if (filterDateRange.value) {
    filters.start_date = dayjs(filterDateRange.value[0]).format('YYYY-MM-DD HH:mm:ss')
    filters.end_date = dayjs(filterDateRange.value[1]).format('YYYY-MM-DD HH:mm:ss')
  }
  currentPage.value = 1
  fetchLogs(filters)
}

function handleReset() {
  filterUsername.value = ''
  filterAction.value = ''
  filterResourceType.value = ''
  filterScenarioId.value = ''
  filterDateRange.value = null
  currentPage.value = 1
  fetchLogs()
}

function showDetail(log: AuditLog) {
  selectedLog.value = log
  detailDrawerOpen.value = true
}

function getActionType(action: string) {
  const map: Record<string, string> = { CREATE: 'success', UPDATE: '', DELETE: 'danger', VIEW: 'info', EXPORT: 'warning' }
  return map[action] || 'info'
}

function formatTime(t: string) { return dayjs(t).format('YYYY-MM-DD HH:mm:ss') }

function handlePageChange(page: number) { currentPage.value = page; fetchLogs() }
function handleSizeChange(size: number) { pageSize.value = size; currentPage.value = 1; fetchLogs() }

onMounted(() => fetchLogs())
</script>

<template>
  <div style="padding: 24px">
    <!-- Filter -->
    <el-card style="margin-bottom: 16px">
      <template #header><span>审计日志查询</span></template>
      <el-form :inline="true" @submit.prevent="handleSearch">
        <el-form-item label="用户名">
          <el-input v-model="filterUsername" placeholder="输入用户名" style="width: 150px" clearable />
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="filterAction" placeholder="选择操作" style="width: 150px" clearable>
            <el-option label="CREATE" value="CREATE" />
            <el-option label="UPDATE" value="UPDATE" />
            <el-option label="DELETE" value="DELETE" />
            <el-option label="VIEW" value="VIEW" />
            <el-option label="EXPORT" value="EXPORT" />
          </el-select>
        </el-form-item>
        <el-form-item label="资源类型">
          <el-select v-model="filterResourceType" placeholder="选择资源类型" style="width: 150px" clearable>
            <el-option label="USER" value="USER" />
            <el-option label="SCENARIO" value="SCENARIO" />
            <el-option label="KEYWORD" value="KEYWORD" />
            <el-option label="POLICY" value="POLICY" />
            <el-option label="META_TAG" value="META_TAG" />
          </el-select>
        </el-form-item>
        <el-form-item label="场景ID">
          <el-input v-model="filterScenarioId" placeholder="输入场景ID" style="width: 150px" clearable />
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker v-model="filterDateRange" type="datetimerange" range-separator="至" start-placeholder="开始" end-placeholder="结束" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch"><el-icon><Search /></el-icon>查询</el-button>
          <el-button @click="handleReset"><el-icon><Refresh /></el-icon>重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table -->
    <el-card>
      <template #header><span>审计日志列表 (共 {{ total }} 条)</span></template>
      <el-table :data="logs" v-loading="loading" row-key="id" style="width: 100%">
        <el-table-column prop="created_at" label="时间" width="180" :formatter="(_r: any, _c: any, v: string) => formatTime(v)" />
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="action" label="操作" width="100">
          <template #default="{ row }"><el-tag :type="getActionType(row.action)" size="small">{{ row.action }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="resource_type" label="资源类型" width="150" />
        <el-table-column prop="resource_id" label="资源ID" width="200" show-overflow-tooltip />
        <el-table-column prop="scenario_id" label="场景ID" width="150" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showDetail(row)">
              <el-icon><View /></el-icon>详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 16px; display: flex; justify-content: flex-end">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <!-- Detail Drawer -->
    <el-drawer v-model="detailDrawerOpen" title="审计日志详情" direction="rtl" size="600px">
      <template v-if="selectedLog">
        <div style="margin-bottom: 16px"><strong>日志ID:</strong> {{ selectedLog.id }}</div>
        <div style="margin-bottom: 16px"><strong>用户:</strong> {{ selectedLog.username }} (ID: {{ selectedLog.user_id }})</div>
        <div style="margin-bottom: 16px"><strong>操作:</strong> <el-tag :type="getActionType(selectedLog.action)" size="small">{{ selectedLog.action }}</el-tag></div>
        <div style="margin-bottom: 16px"><strong>资源类型:</strong> {{ selectedLog.resource_type }}</div>
        <div v-if="selectedLog.resource_id" style="margin-bottom: 16px"><strong>资源ID:</strong> {{ selectedLog.resource_id }}</div>
        <div v-if="selectedLog.scenario_id" style="margin-bottom: 16px"><strong>场景ID:</strong> {{ selectedLog.scenario_id }}</div>
        <div style="margin-bottom: 16px"><strong>IP地址:</strong> {{ selectedLog.ip_address || 'N/A' }}</div>
        <div style="margin-bottom: 16px">
          <strong>User Agent:</strong>
          <div style="word-break: break-all; font-size: 12px; color: #666">{{ selectedLog.user_agent || 'N/A' }}</div>
        </div>
        <div style="margin-bottom: 16px"><strong>时间:</strong> {{ formatTime(selectedLog.created_at) }}</div>
        <div v-if="selectedLog.details">
          <strong>详细信息:</strong>
          <pre style="background: #f5f5f5; padding: 12px; border-radius: 4px; margin-top: 8px; overflow: auto; max-height: 400px">{{ JSON.stringify(selectedLog.details, null, 2) }}</pre>
        </div>
      </template>
    </el-drawer>
  </div>
</template>
