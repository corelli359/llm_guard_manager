<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { RuleScenarioPolicy, MetaTag } from '../types'
import { rulePoliciesApi, metaTagsApi, getErrorMessage } from '../api'

const props = defineProps<{ scenarioId: string; ruleMode: number; modeName: string }>()

const policies = ref<RuleScenarioPolicy[]>([])
const filteredPolicies = ref<RuleScenarioPolicy[]>([])
const tags = ref<MetaTag[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const matchType = ref<'KEYWORD' | 'TAG'>('KEYWORD')
const searchText = ref('')
const hasAccess = ref(true)
const form = ref<Partial<RuleScenarioPolicy>>({})

watch([() => props.scenarioId, () => props.ruleMode], () => { fetchPolicies(); fetchTags() }, { immediate: true })
watch([policies, searchText], applyFilters)

async function fetchPolicies() {
  if (!props.scenarioId) return
  loading.value = true
  try {
    const res = await rulePoliciesApi.getByScenario(props.scenarioId)
    policies.value = res.data.filter((p: RuleScenarioPolicy) => p.rule_mode === props.ruleMode)
    hasAccess.value = true
  } catch (e: any) {
    if (e.response?.status === 403) hasAccess.value = false
    ElMessage.error(getErrorMessage(e, '获取策略列表失败'))
  } finally { loading.value = false }
}

async function fetchTags() { try { tags.value = (await metaTagsApi.getAll()).data } catch {} }

function applyFilters() {
  let filtered = [...policies.value]
  if (searchText.value.trim()) {
    const s = searchText.value.toLowerCase()
    filtered = filtered.filter(p => p.match_value.toLowerCase().includes(s) || p.strategy.toLowerCase().includes(s))
  }
  filteredPolicies.value = filtered
}

function handleAdd() {
  editingId.value = null; matchType.value = 'KEYWORD'
  form.value = { scenario_id: props.scenarioId, is_active: true, rule_mode: props.ruleMode, match_type: 'KEYWORD', strategy: 'BLOCK', match_value: '', extra_condition: '' }
  dialogVisible.value = true
}
function handleEdit(row: RuleScenarioPolicy) {
  editingId.value = row.id; matchType.value = row.match_type; form.value = { ...row }; dialogVisible.value = true
}
async function handleDelete(row: RuleScenarioPolicy) {
  try { await rulePoliciesApi.delete(row.id); ElMessage.success('已删除'); fetchPolicies() }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '删除失败')) }
}
async function handleSubmit() {
  try {
    if (editingId.value) { await rulePoliciesApi.update(editingId.value, form.value); ElMessage.success('已更新') }
    else { await rulePoliciesApi.create(form.value as Omit<RuleScenarioPolicy, 'id'>); ElMessage.success('已创建') }
    dialogVisible.value = false; fetchPolicies()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '操作失败')) }
}

function onMatchTypeChange(val: 'KEYWORD' | 'TAG') { matchType.value = val; form.value.match_value = ''; form.value.extra_condition = '' }
function getStrategyType(s: string) { return s === 'BLOCK' ? 'danger' : s === 'PASS' ? 'success' : 'warning' }
function getStrategyLabel(s: string) { return s === 'BLOCK' ? '拦截' : s === 'PASS' ? '放行' : '重写' }
</script>

<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <span style="color:#666">当前模式: <el-tag size="small">{{ modeName }}</el-tag></span>
      <div style="display:flex;gap:8px">
        <el-input v-model="searchText" placeholder="搜索匹配值或策略" clearable style="width:220px" />
        <el-button v-if="hasAccess" type="primary" @click="handleAdd">新增规则</el-button>
      </div>
    </div>
    <el-table :data="filteredPolicies" v-loading="loading" border>
      <el-table-column prop="match_type" label="匹配类型" width="120">
        <template #default="{ row }"><el-tag :type="row.match_type === 'KEYWORD' ? '' : 'warning'">{{ row.match_type === 'KEYWORD' ? '敏感词' : '标签' }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="match_value" label="匹配内容" width="200" />
      <el-table-column prop="extra_condition" label="额外条件" width="150">
        <template #default="{ row }">{{ row.extra_condition || '-' }}</template>
      </el-table-column>
      <el-table-column prop="strategy" label="处置策略" width="120">
        <template #default="{ row }"><el-tag :type="getStrategyType(row.strategy)">{{ getStrategyLabel(row.strategy) }}</el-tag></template>
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

    <el-dialog :title="editingId ? '编辑规则' : '新增规则'" v-model="dialogVisible" width="600px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="场景 ID"><el-input :model-value="form.scenario_id" disabled /></el-form-item>
        <el-form-item label="规则模式"><el-select :model-value="form.rule_mode" disabled><el-option :value="0" label="超级模式" /><el-option :value="1" label="自定义模式" /></el-select></el-form-item>
        <el-form-item label="匹配类型" required>
          <el-radio-group v-model="form.match_type" @change="onMatchTypeChange">
            <el-radio-button value="KEYWORD">敏感词 (KEYWORD)</el-radio-button>
            <el-radio-button value="TAG">标签 (TAG)</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <template v-if="form.match_type === 'KEYWORD'">
          <el-form-item label="敏感词内容" required><el-input v-model="form.match_value" placeholder="输入要匹配的敏感词" /></el-form-item>
          <el-form-item label="关联标签">
            <el-select v-model="form.extra_condition" clearable filterable placeholder="可选">
              <el-option v-for="t in tags" :key="t.tag_code" :label="`${t.tag_name} (${t.tag_code})`" :value="t.tag_code" />
            </el-select>
          </el-form-item>
        </template>
        <template v-else>
          <el-form-item label="标签编码" required>
            <el-select v-model="form.match_value" filterable placeholder="选择标签">
              <el-option v-for="t in tags" :key="t.tag_code" :label="`${t.tag_name} (${t.tag_code})`" :value="t.tag_code" />
            </el-select>
          </el-form-item>
          <el-form-item label="模型判定结果">
            <el-select v-model="form.extra_condition" clearable placeholder="可选">
              <el-option label="safe (安全)" value="safe" /><el-option label="unsafe (不安全)" value="unsafe" /><el-option label="controversial (有争议)" value="controversial" />
            </el-select>
          </el-form-item>
        </template>
        <el-form-item label="处置策略" required>
          <el-select v-model="form.strategy"><el-option label="拦截 (BLOCK)" value="BLOCK" /><el-option label="放行 (PASS)" value="PASS" /><el-option label="重写 (REWRITE)" value="REWRITE" /></el-select>
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
