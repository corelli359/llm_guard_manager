<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { ScenarioKeyword, MetaTag } from '../types'
import { scenarioKeywordsApi, metaTagsApi, getErrorMessage } from '../api'

const props = defineProps<{ scenarioId: string; mode: 'custom' | 'super' }>()
const ruleMode = computed(() => props.mode === 'custom' ? 1 : 0)

const keywords = ref<ScenarioKeyword[]>([])
const filteredKeywords = ref<ScenarioKeyword[]>([])
const tags = ref<MetaTag[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const categoryFilter = ref<'all' | 0 | 1>('all')
const searchText = ref('')
const hasAccess = ref(true)
const form = ref<Partial<ScenarioKeyword>>({})

watch([() => props.scenarioId, () => props.mode], () => { fetchKeywords(); fetchTags() }, { immediate: true })
watch([keywords, categoryFilter, searchText], applyFilters)

async function fetchKeywords() {
  if (!props.scenarioId) return
  loading.value = true
  try { keywords.value = (await scenarioKeywordsApi.getByScenario(props.scenarioId, ruleMode.value)).data; hasAccess.value = true }
  catch (e: any) { if (e.response?.status === 403) hasAccess.value = false; ElMessage.error(getErrorMessage(e, '获取场景敏感词失败')) }
  finally { loading.value = false }
}

async function fetchTags() {
  try { tags.value = (await metaTagsApi.getAll()).data } catch {}
}

function applyFilters() {
  let filtered = [...keywords.value]
  if (categoryFilter.value !== 'all') filtered = filtered.filter(k => k.category === categoryFilter.value)
  if (searchText.value.trim()) { const s = searchText.value.toLowerCase(); filtered = filtered.filter(k => k.keyword.toLowerCase().includes(s)) }
  filteredKeywords.value = filtered
}

function handleAdd() {
  editingId.value = null
  form.value = { scenario_id: props.scenarioId, is_active: true, category: 1, rule_mode: ruleMode.value, risk_level: 'High', keyword: '', tag_code: '' }
  dialogVisible.value = true
}
function handleEdit(row: ScenarioKeyword) { editingId.value = row.id; form.value = { ...row }; dialogVisible.value = true }
async function handleDelete(row: ScenarioKeyword) {
  try { await scenarioKeywordsApi.delete(row.id); ElMessage.success('已删除'); fetchKeywords() }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '删除失败')) }
}
async function handleSubmit() {
  try {
    if (editingId.value) { await scenarioKeywordsApi.update(editingId.value, form.value); ElMessage.success('已更新') }
    else { await scenarioKeywordsApi.create(form.value as Omit<ScenarioKeyword, 'id'>); ElMessage.success('已添加') }
    dialogVisible.value = false; fetchKeywords()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '操作失败')) }
}

function getRiskColor(level: string) { return level === 'High' ? 'danger' : level === 'Medium' ? 'warning' : 'success' }
</script>

<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <div style="display:flex;gap:8px;align-items:center">
        <span>过滤:</span>
        <el-radio-group v-model="categoryFilter" size="small">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button :label="1">仅黑名单</el-radio-button>
          <el-radio-button :label="0">仅白名单</el-radio-button>
        </el-radio-group>
      </div>
      <div style="display:flex;gap:8px">
        <el-input v-model="searchText" placeholder="搜索敏感词" clearable style="width:200px" />
        <el-button v-if="hasAccess" type="primary" @click="handleAdd">添加敏感词</el-button>
      </div>
    </div>
    <el-table :data="filteredKeywords" v-loading="loading" border>
      <el-table-column prop="keyword" label="敏感词内容" min-width="200" />
      <el-table-column prop="category" label="名单类型" width="120">
        <template #default="{ row }">
          <el-tag :type="row.category === 0 ? 'success' : 'danger'">{{ row.category === 0 ? '白名单' : '黑名单' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="tag_code" label="关联标签" width="150">
        <template #default="{ row }"><el-tag v-if="row.tag_code">{{ row.tag_code }}</el-tag><span v-else>-</span></template>
      </el-table-column>
      <el-table-column prop="risk_level" label="风险等级" width="120">
        <template #default="{ row }">
          <el-tag v-if="row.risk_level" :type="getRiskColor(row.risk_level)">{{ row.risk_level }}</el-tag><span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }"><el-switch :model-value="row.is_active" disabled size="small" /></template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <template v-if="hasAccess">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
          <el-tag v-else type="info">无权限</el-tag>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="editingId ? '编辑敏感词' : '添加敏感词'" v-model="dialogVisible" width="550px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="场景 ID"><el-input :model-value="form.scenario_id" disabled /></el-form-item>
        <el-form-item label="敏感词" required><el-input v-model="form.keyword" placeholder="输入敏感词" /></el-form-item>
        <el-form-item label="名单类型" required>
          <el-select v-model="form.category"><el-option :value="1" label="黑名单 (Block)" /><el-option :value="0" label="白名单 (Allow)" /></el-select>
        </el-form-item>
        <el-form-item label="关联标签" required>
          <el-select v-model="form.tag_code" filterable placeholder="选择标签">
            <el-option v-for="t in tags" :key="t.tag_code" :label="`${t.tag_name} (${t.tag_code})`" :value="t.tag_code" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险等级">
          <el-select v-model="form.risk_level"><el-option value="High" label="高 (High)" /><el-option value="Medium" label="中 (Medium)" /><el-option value="Low" label="低 (Low)" /></el-select>
        </el-form-item>
        <el-form-item label="是否启用"><el-switch v-model="form.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
