<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { ScenarioApp } from '../types'
import { scenariosApi, getErrorMessage } from '../api'

const router = useRouter()
const apps = ref<ScenarioApp[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<string | null>(null)
const form = ref<Partial<ScenarioApp>>({
  app_id: '', app_name: '', description: '', is_active: true,
  enable_whitelist: true, enable_blacklist: true, enable_custom_policy: true,
})

onMounted(() => fetchApps())

async function fetchApps() {
  loading.value = true
  try { apps.value = (await scenariosApi.getAll()).data }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '获取应用列表失败')) }
  finally { loading.value = false }
}

function handleAdd() {
  editingId.value = null
  form.value = { app_id: '', app_name: '', description: '', is_active: true, enable_whitelist: true, enable_blacklist: true, enable_custom_policy: true }
  dialogVisible.value = true
}

function handleEdit(row: ScenarioApp) {
  editingId.value = row.id; form.value = { ...row }; dialogVisible.value = true
}

async function handleDelete(row: ScenarioApp) {
  try {
    await ElMessageBox.confirm('确定注销该应用吗？', '确认', { type: 'warning' })
    await scenariosApi.delete(row.id); ElMessage.success('应用已注销'); fetchApps()
  } catch (e: any) { if (e !== 'cancel') ElMessage.error(getErrorMessage(e, '删除失败')) }
}

async function handleSubmit() {
  try {
    if (editingId.value) { await scenariosApi.update(editingId.value, form.value); ElMessage.success('应用信息已更新') }
    else { await scenariosApi.create(form.value as Omit<ScenarioApp, 'id'>); ElMessage.success('应用已成功注册') }
    dialogVisible.value = false; fetchApps()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '操作失败')) }
}
</script>

<template>
  <div style="padding: 24px">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px">
      <h2 style="margin: 0">应用管理 (App Management)</h2>
      <el-button type="primary" @click="handleAdd">注册新应用</el-button>
    </div>

    <el-table :data="apps" v-loading="loading" border row-key="id">
      <el-table-column prop="app_id" label="应用 ID (App ID)" width="200">
        <template #default="{ row }"><b>{{ row.app_id }}</b></template>
      </el-table-column>
      <el-table-column prop="app_name" label="应用名称" width="200" />
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <el-switch :model-value="row.is_active" disabled size="small" />
        </template>
      </el-table-column>
      <el-table-column label="功能模块" min-width="250">
        <template #default="{ row }">
          <el-tag v-if="row.enable_blacklist" type="danger" size="small" style="margin-right:4px">黑名单</el-tag>
          <el-tag v-if="row.enable_whitelist" type="success" size="small" style="margin-right:4px">白名单</el-tag>
          <el-tag v-if="row.enable_custom_policy" size="small">自定义策略</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="router.push(`/apps/${row.app_id}`)">进入管理</el-button>
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">注销</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="editingId ? '编辑应用' : '注册新应用'" v-model="dialogVisible" width="550px">
      <el-form :model="form" label-width="140px">
        <el-form-item label="应用唯一标识 (App ID)" required>
          <el-input v-model="form.app_id" :disabled="!!editingId" placeholder="例如：chat_bot_01" />
        </el-form-item>
        <el-form-item label="应用名称" required>
          <el-input v-model="form.app_name" placeholder="例如：智能客服助手" />
        </el-form-item>
        <el-form-item label="应用描述">
          <el-input v-model="form.description" type="textarea" placeholder="可选：简要描述应用用途" />
        </el-form-item>
        <el-card shadow="never" style="margin-top: 8px">
          <template #header><span>功能开关</span></template>
          <el-form-item label="激活应用"><el-switch v-model="form.is_active" /></el-form-item>
          <el-form-item label="启用敏感词黑名单"><el-switch v-model="form.enable_blacklist" /></el-form-item>
          <el-form-item label="启用白名单"><el-switch v-model="form.enable_whitelist" /></el-form-item>
          <el-form-item label="启用自定义处置策略"><el-switch v-model="form.enable_custom_policy" /></el-form-item>
        </el-card>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
