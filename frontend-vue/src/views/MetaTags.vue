<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { MetaTag } from '../types'
import { metaTagsApi, getErrorMessage } from '../api'

const tags = ref<MetaTag[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const form = ref<Partial<MetaTag>>({ tag_code: '', tag_name: '', parent_code: '', level: 1, is_active: true })

onMounted(() => fetchTags())

async function fetchTags() {
  loading.value = true
  try {
    const res = await metaTagsApi.getAll()
    tags.value = res.data
  } catch (e: any) {
    ElMessage.error(getErrorMessage(e, '获取标签列表失败'))
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  editingId.value = null
  form.value = { tag_code: '', tag_name: '', parent_code: '', level: 1, is_active: true }
  dialogVisible.value = true
}

function handleEdit(row: MetaTag) {
  editingId.value = row.id
  form.value = { ...row }
  dialogVisible.value = true
}

async function handleDelete(row: MetaTag) {
  try {
    await ElMessageBox.confirm('确定要删除此标签吗？', '确认删除', { type: 'warning' })
    await metaTagsApi.delete(row.id)
    ElMessage.success('标签已删除')
    fetchTags()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(getErrorMessage(e, '删除失败'))
  }
}

async function handleSubmit() {
  try {
    if (editingId.value) {
      await metaTagsApi.update(editingId.value, form.value)
      ElMessage.success('标签已更新')
    } else {
      await metaTagsApi.create(form.value as Omit<MetaTag, 'id'>)
      ElMessage.success('标签已创建')
    }
    dialogVisible.value = false
    fetchTags()
  } catch (e: any) {
    ElMessage.error(getErrorMessage(e, '操作失败'))
  }
}
</script>

<template>
  <div style="padding: 24px">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <div>
        <h2 style="margin: 0">标签管理</h2>
        <p style="color: #666; margin: 4px 0 0">管理内容分类标签体系</p>
      </div>
      <el-button type="primary" @click="handleAdd">新增标签</el-button>
    </div>

    <el-table :data="tags" v-loading="loading" row-key="id" border>
      <el-table-column prop="tag_code" label="标签编码" width="200" />
      <el-table-column prop="tag_name" label="标签名称" width="200" />
      <el-table-column prop="parent_code" label="父级编码" width="200">
        <template #default="{ row }">{{ row.parent_code || '-' }}</template>
      </el-table-column>
      <el-table-column prop="level" label="层级" width="80" />
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="editingId ? '编辑标签' : '新增标签'" v-model="dialogVisible" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="标签编码" required>
          <el-input v-model="form.tag_code" :disabled="!!editingId" placeholder="如: POLITICS" />
        </el-form-item>
        <el-form-item label="标签名称" required>
          <el-input v-model="form.tag_name" placeholder="如: 政治敏感" />
        </el-form-item>
        <el-form-item label="父级编码">
          <el-select v-model="form.parent_code" clearable filterable placeholder="选择父级标签">
            <el-option v-for="t in tags" :key="t.tag_code" :label="`${t.tag_name} (${t.tag_code})`" :value="t.tag_code" />
          </el-select>
        </el-form-item>
        <el-form-item label="层级">
          <el-input-number v-model="form.level" :min="1" :max="5" />
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
