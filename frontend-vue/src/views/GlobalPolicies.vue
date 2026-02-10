<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { RuleGlobalDefault, MetaTag } from '../types'
import { globalPoliciesApi, metaTagsApi, getErrorMessage } from '../api'

const policies = ref<RuleGlobalDefault[]>([])
const tags = ref<MetaTag[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const form = ref<Partial<RuleGlobalDefault>>({ tag_code: '', strategy: 'BLOCK', extra_condition: '', is_active: true })

onMounted(() => { fetchPolicies(); fetchTags() })

async function fetchTags() {
  try { tags.value = (await metaTagsApi.getAll()).data } catch {}
}

async function fetchPolicies() {
  loading.value = true
  try { policies.value = (await globalPoliciesApi.getAll()).data }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '获取策略失败')) }
  finally { loading.value = false }
}

function handleAdd() {
  editingId.value = null
  form.value = { tag_code: '', strategy: 'BLOCK', extra_condition: '', is_active: true }
  dialogVisible.value = true
}
function handleEdit(row: RuleGlobalDefault) {
  editingId.value = row.id; form.value = { ...row }; dialogVisible.value = true
}
async function handleDelete(row: RuleGlobalDefault) {
  try {
    await ElMessageBox.confirm('确定删除此策略？', '确认', { type: 'warning' })
    await globalPoliciesApi.delete(row.id); ElMessage.success('已删除'); fetchPolicies()
  } catch (e: any) { if (e !== 'cancel') ElMessage.error(getErrorMessage(e, '删除失败')) }
}
async function handleSubmit() {
  try {
    if (editingId.value) { await globalPoliciesApi.update(editingId.value, form.value); ElMessage.success('已更新') }
    else { await globalPoliciesApi.create(form.value as Omit<RuleGlobalDefault, 'id'>); ElMessage.success('已创建') }
    dialogVisible.value = false; fetchPolicies()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '操作失败')) }
}

function getStrategyType(s: string) {
  if (s === 'BLOCK') return 'danger'
  if (s === 'PASS') return 'success'
  return 'warning'
}
function getStrategyLabel(s: string) {
  if (s === 'BLOCK') return '拦截'
  if (s === 'PASS') return '放行'
  return '重写'
}
</script>

<template>
  <div style="padding: 24px">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <div><h2 style="margin: 0">全局默认策略</h2><p style="color: #666; margin: 4px 0 0">当场景策略未匹配时的兜底规则</p></div>
      <el-button type="primary" @click="handleAdd">新增策略</el-button>
    </div>

    <el-table :data="policies" v-loading="loading" border>
      <el-table-column prop="tag_code" label="标签编码" width="200" />
      <el-table-column prop="extra_condition" label="额外条件" width="200">
        <template #default="{ row }">{{ row.extra_condition || '-' }}</template>
      </el-table-column>
      <el-table-column prop="strategy" label="处置策略" width="120">
        <template #default="{ row }">
          <el-tag :type="getStrategyType(row.strategy)">{{ getStrategyLabel(row.strategy) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="editingId ? '编辑策略' : '新增策略'" v-model="dialogVisible" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="标签编码" required>
          <el-select v-model="form.tag_code" filterable placeholder="选择标签">
            <el-option v-for="t in tags" :key="t.tag_code" :label="`${t.tag_name} (${t.tag_code})`" :value="t.tag_code" />
          </el-select>
        </el-form-item>
        <el-form-item label="额外条件">
          <el-select v-model="form.extra_condition" clearable placeholder="可选">
            <el-option label="safe (安全)" value="safe" />
            <el-option label="unsafe (不安全)" value="unsafe" />
            <el-option label="controversial (有争议)" value="controversial" />
          </el-select>
        </el-form-item>
        <el-form-item label="处置策略" required>
          <el-select v-model="form.strategy">
            <el-option label="拦截 (BLOCK)" value="BLOCK" />
            <el-option label="放行 (PASS)" value="PASS" />
            <el-option label="重写 (REWRITE)" value="REWRITE" />
          </el-select>
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
