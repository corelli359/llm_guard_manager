<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { GlobalKeyword, MetaTag } from '../types'
import { globalKeywordsApi, metaTagsApi, getErrorMessage } from '../api'

const keywords = ref<GlobalKeyword[]>([])
const tags = ref<MetaTag[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const searchText = ref('')
const filterTag = ref('')
const form = ref<Partial<GlobalKeyword>>({ keyword: '', tag_code: '', risk_level: 'Medium', is_active: true })

onMounted(() => { fetchKeywords(); fetchTags() })

async function fetchTags() {
  try { tags.value = (await metaTagsApi.getAll()).data } catch {}
}

async function fetchKeywords() {
  loading.value = true
  try {
    const res = await globalKeywordsApi.getAll(0, 1000, searchText.value || undefined, filterTag.value || undefined)
    keywords.value = res.data
  } catch (e: any) {
    ElMessage.error(getErrorMessage(e, '获取关键词失败'))
  } finally { loading.value = false }
}

function handleAdd() {
  editingId.value = null
  form.value = { keyword: '', tag_code: '', risk_level: 'Medium', is_active: true }
  dialogVisible.value = true
}

function handleEdit(row: GlobalKeyword) {
  editingId.value = row.id
  form.value = { ...row }
  dialogVisible.value = true
}

async function handleDelete(row: GlobalKeyword) {
  try {
    await ElMessageBox.confirm('确定删除此关键词？', '确认', { type: 'warning' })
    await globalKeywordsApi.delete(row.id)
    ElMessage.success('已删除')
    fetchKeywords()
  } catch (e: any) { if (e !== 'cancel') ElMessage.error(getErrorMessage(e, '删除失败')) }
}

async function handleSubmit() {
  try {
    if (editingId.value) {
      await globalKeywordsApi.update(editingId.value, form.value)
      ElMessage.success('已更新')
    } else {
      await globalKeywordsApi.create(form.value as Omit<GlobalKeyword, 'id'>)
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    fetchKeywords()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '操作失败')) }
}

function getRiskColor(level: string) {
  if (level === 'High') return 'danger'
  if (level === 'Medium') return 'warning'
  return 'success'
}
</script>

<template>
  <div style="padding: 24px">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">全局敏感词库</h2>
      <div style="display: flex; gap: 8px">
        <el-input v-model="searchText" placeholder="搜索关键词" clearable style="width: 200px" @clear="fetchKeywords" @keyup.enter="fetchKeywords" />
        <el-select v-model="filterTag" placeholder="按标签筛选" clearable style="width: 180px" @change="fetchKeywords">
          <el-option v-for="t in tags" :key="t.tag_code" :label="t.tag_name" :value="t.tag_code" />
        </el-select>
        <el-button type="primary" @click="handleAdd">新增关键词</el-button>
      </div>
    </div>

    <el-table :data="keywords" v-loading="loading" border>
      <el-table-column prop="keyword" label="关键词" min-width="200" />
      <el-table-column prop="tag_code" label="标签" width="150" />
      <el-table-column prop="risk_level" label="风险等级" width="120">
        <template #default="{ row }">
          <el-tag :type="getRiskColor(row.risk_level)">{{ row.risk_level }}</el-tag>
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

    <el-dialog :title="editingId ? '编辑关键词' : '新增关键词'" v-model="dialogVisible" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="关键词" required>
          <el-input v-model="form.keyword" placeholder="输入敏感词" />
        </el-form-item>
        <el-form-item label="标签" required>
          <el-select v-model="form.tag_code" filterable placeholder="选择标签">
            <el-option v-for="t in tags" :key="t.tag_code" :label="`${t.tag_name} (${t.tag_code})`" :value="t.tag_code" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险等级" required>
          <el-select v-model="form.risk_level">
            <el-option label="High" value="High" /><el-option label="Medium" value="Medium" /><el-option label="Low" value="Low" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
