<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { stagingApi, getErrorMessage } from '../api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const taskType = ref('keywords')
const stats = ref<any[]>([])

const totalReviewed = computed(() => stats.value.reduce((s, i) => s + i.reviewed_count, 0))
const totalIgnored = computed(() => stats.value.reduce((s, i) => s + i.ignored_count, 0))
const totalAll = computed(() => stats.value.reduce((s, i) => s + i.total_count, 0))

async function fetchStats() {
  loading.value = true
  try {
    const res = await stagingApi.getAnnotatorStats(taskType.value)
    stats.value = res.data
  } catch (e: any) {
    ElMessage.error(getErrorMessage(e, '获取统计数据失败'))
  } finally {
    loading.value = false
  }
}

function completionRate(row: any) {
  return row.total_count > 0
    ? (((row.reviewed_count + row.ignored_count) / row.total_count) * 100).toFixed(1) + '%'
    : '0.0%'
}

onMounted(fetchStats)
watch(taskType, fetchStats)
</script>

<template>
  <div style="padding: 24px">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">标注员统计 (Annotator Statistics)</h2>
      <el-select v-model="taskType" style="width: 200px">
        <el-option label="敏感词审核" value="keywords" />
        <el-option label="规则审核" value="rules" />
      </el-select>
    </div>

    <el-row :gutter="16" style="margin-bottom: 24px">
      <el-col :span="6">
        <el-card shadow="never">
          <el-statistic title="总标注员数" :value="stats.length">
            <template #prefix><el-icon><User /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <el-statistic title="总已审核" :value="totalReviewed" :value-style="{ color: '#3f8600' }">
            <template #prefix><el-icon><CircleCheck /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <el-statistic title="总已忽略" :value="totalIgnored" :value-style="{ color: '#999' }">
            <template #prefix><el-icon><CircleClose /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="never">
          <el-statistic title="总标注数" :value="totalAll">
            <template #prefix><el-icon><Document /></el-icon></template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <el-table :data="stats" v-loading="loading" row-key="annotator" style="width: 100%">
        <el-table-column prop="annotator" label="标注员">
          <template #default="{ row }">
            <el-icon style="margin-right: 4px"><User /></el-icon>{{ row.annotator }}
          </template>
        </el-table-column>
        <el-table-column prop="reviewed_count" label="已审核" sortable>
          <template #default="{ row }">
            <span style="color: #52c41a; font-weight: bold">{{ row.reviewed_count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="ignored_count" label="已忽略" sortable>
          <template #default="{ row }">
            <span style="color: #999">{{ row.ignored_count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_count" label="总计" sortable>
          <template #default="{ row }">
            <span style="font-weight: bold">{{ row.total_count }}</span>
          </template>
        </el-table-column>
        <el-table-column label="完成率" sortable :sort-method="(a: any, b: any) => (a.total_count > 0 ? (a.reviewed_count + a.ignored_count) / a.total_count : 0) - (b.total_count > 0 ? (b.reviewed_count + b.ignored_count) / b.total_count : 0)">
          <template #default="{ row }">{{ completionRate(row) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>
