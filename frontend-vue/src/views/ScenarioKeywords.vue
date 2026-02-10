<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { scenarioKeywordsApi, metaTagsApi, getErrorMessage } from '../api'
import type { ScenarioKeyword, MetaTag } from '../types'

const route = useRoute()
const router = useRouter()
const appId = computed(() => route.params.appId as string)
const keywords = ref<ScenarioKeyword[]>([])
const tags = ref<MetaTag[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const currentScenarioId = ref('')
const searchScenarioId = ref('')
const form = ref<Partial<ScenarioKeyword>>({})

onMounted(() => {
  if (appId.value) { currentScenarioId.value = appId.value; searchScenarioId.value = appId.value; fetchKeywords(appId.value) }
  fetchTags()
})

async function fetchKeywords(scenarioId: string) {
  if (!scenarioId) return
  loading.value = true
  try { keywords.value = (await scenarioKeywordsApi.getByScenario(scenarioId)).data; currentScenarioId.value = scenarioId }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '获取场景敏感词失败')) }
  finally { loading.value = false }
}

async function fetchTags() { try { tags.value = (await metaTagsApi.getAll()).data } catch {} }

function handleSearch() {
  if (searchScenarioId.value.trim()) fetchKeywords(searchScenarioId.value.trim())
  else ElMessage.warning('请输入场景 ID')
}

function handleAdd() {
  if (!currentScenarioId.value) { ElMessage.warning('请先选择一个场景'); return }
  editingId.value = null
  form.value = { scenario_id: currentScenarioId.value, is_active: true, category: 1, risk_level: 'High', keyword: '', tag_code: '' }
  dialogVisible.value = true
}
function handleEdit(row: ScenarioKeyword) { editingId.value = row.id; form.value = { ...row }; dialogVisible.value = true }
async function handleDelete(row: ScenarioKeyword) {
  try { await scenarioKeywordsApi.delete(row.id); ElMessage.success('已删除'); fetchKeywords(currentScenarioId.value) }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '删除失败')) }
}
async function handleSubmit() {
  try {
    if (editingId.value) { await scenarioKeywordsApi.update(editingId.value, form.value); ElMessage.success('已更新') }
    else { await scenarioKeywordsApi.create(form.value as Omit<ScenarioKeyword, 'id'>); ElMessage.success('已添加') }
    dialogVisible.value = false; fetchKeywords(currentScenarioId.value)
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '操作失败')) }
}

function getRiskColor(l: string) { return l === 'High' ? 'danger' : l === 'Medium' ? 'warning' : 'success' }
</script>

<template>
  <div style="padding: 24px">
    <el-button v-if="appId" @click="router.push(`/apps/${appId}`)" style="margin-bottom:16px">返回应用概览</el-button>
    <h2>场景敏感词库 {{ appId ? `- ${appId}` : '' }}</h2>

    <el-card v-if="!appId" style="margin-bottom:16px">
      <template #header>选择场景</template>
      <div style="display:flex;gap:8px;align-items:center">
        <span>场景 ID:</span>
        <el-input v-model="searchScenarioId" placeholder="请输入场景 ID" style="flex:1" @keyup.enter="handleSearch" />
        <el-button type="primary" @click="handleSearch">加载配置</el-button>
      </div>
    </el-card>

    <template v-if="currentScenarioId">
      <div style="display:flex;justify-content:flex-end;margin-bottom:16px">
        <el-button type="primary" @click="handleAdd">添加敏感词 ({{ currentScenarioId }})</el-button>
      </div>
      <el-table :data="keywords" v-loading="loading" border>
        <el-table-column prop="scenario_id" label="场景 ID" width="150" />
        <el-table-column prop="keyword" label="敏感词内容" min-width="200" />
        <el-table-column prop="category" label="名单类型" width="120">
          <template #default="{ row }"><el-tag :type="row.category === 0 ? 'success' : 'danger'">{{ row.category === 0 ? '白名单' : '黑名单' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="tag_code" label="关联标签" width="150">
          <template #default="{ row }"><el-tag v-if="row.tag_code">{{ row.tag_code }}</el-tag><span v-else>-</span></template>
        </el-table-column>
        <el-table-column prop="risk_level" label="风险等级" width="100">
          <template #default="{ row }"><el-tag v-if="row.risk_level" :type="getRiskColor(row.risk_level)">{{ row.risk_level }}</el-tag><span v-else>-</span></template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }"><el-switch :model-value="row.is_active" disabled size="small" /></template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </template>

    <el-dialog :title="editingId ? '编辑敏感词' : '添加敏感词'" v-model="dialogVisible" width="500px">
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
          <el-select v-model="form.risk_level"><el-option value="High" /><el-option value="Medium" /><el-option value="Low" /></el-select>
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
