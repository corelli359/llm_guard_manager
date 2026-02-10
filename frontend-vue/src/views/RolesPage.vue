<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { rolesApi, getErrorMessage } from '../api'
import type { Role, PermissionItem } from '../types'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const roles = ref<Role[]>([])
const allPermissions = ref<PermissionItem[]>([])
const loading = ref(false)
const createModalOpen = ref(false)
const editModalOpen = ref(false)
const permModalOpen = ref(false)
const selectedRole = ref<Role | null>(null)
const selectedPermIds = ref<string[]>([])

const createForm = ref({ role_code: '', role_name: '', role_type: '', description: '' })
const editForm = ref({ role_name: '', role_type: '', description: '' })

const globalPerms = computed(() => allPermissions.value.filter(p => p.scope === 'GLOBAL'))
const scenarioPerms = computed(() => allPermissions.value.filter(p => p.scope === 'SCENARIO'))

async function fetchRoles() {
  loading.value = true
  try { roles.value = (await rolesApi.list()).data }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '获取角色列表失败')) }
  finally { loading.value = false }
}

async function fetchAllPermissions() {
  try { allPermissions.value = (await rolesApi.listAllPermissions()).data } catch { /* ignore */ }
}

async function handleCreate() {
  try {
    await rolesApi.create(createForm.value)
    ElMessage.success('角色创建成功'); createModalOpen.value = false
    createForm.value = { role_code: '', role_name: '', role_type: '', description: '' }
    fetchRoles()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '创建失败')) }
}

async function handleEdit() {
  if (!selectedRole.value) return
  try {
    await rolesApi.update(selectedRole.value.id, editForm.value)
    ElMessage.success('角色更新成功'); editModalOpen.value = false; fetchRoles()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '更新失败')) }
}

async function handleDelete(row: Role) {
  try {
    await ElMessageBox.confirm('确定删除该角色吗?', '确认')
    await rolesApi.delete(row.id); ElMessage.success('角色已删除'); fetchRoles()
  } catch (e: any) { if (e !== 'cancel') ElMessage.error(getErrorMessage(e, '删除失败')) }
}

function openEditModal(role: Role) {
  selectedRole.value = role
  editForm.value = { role_name: role.role_name, role_type: role.role_type, description: role.description || '' }
  editModalOpen.value = true
}

async function openPermModal(role: Role) {
  selectedRole.value = role
  try {
    const res = await rolesApi.getPermissions(role.id)
    selectedPermIds.value = res.data.map((p: PermissionItem) => p.id)
    permModalOpen.value = true
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '获取角色权限失败')) }
}

// PLACEHOLDER_SAVE
async function handleSavePermissions() {
  if (!selectedRole.value) return
  try {
    await rolesApi.updatePermissions(selectedRole.value.id, selectedPermIds.value)
    ElMessage.success('权限配置成功'); permModalOpen.value = false; fetchRoles()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '配置失败')) }
}

function formatTime(t: string) { return dayjs(t).format('YYYY-MM-DD HH:mm') }

onMounted(() => { fetchRoles(); fetchAllPermissions() })
</script>

<template>
  <div style="padding: 24px">
    <div style="margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center">
      <div>
        <h2 style="margin: 0">角色管理</h2>
        <p style="color: #666; margin: 4px 0 0">管理系统角色和权限配置。</p>
      </div>
      <el-button type="primary" @click="createForm = { role_code: '', role_name: '', role_type: '', description: '' }; createModalOpen = true">
        <el-icon><Plus /></el-icon>创建角色
      </el-button>
    </div>

    <el-table :data="roles" v-loading="loading" row-key="id" style="width: 100%">
      <el-table-column prop="role_name" label="角色名称" />
      <el-table-column prop="role_code" label="角色编码" />
      <el-table-column prop="role_type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="row.role_type === 'GLOBAL' ? '' : 'success'" size="small">{{ row.role_type === 'GLOBAL' ? '全局' : '场景' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="permission_count" label="权限数量" width="100" />
      <el-table-column prop="is_system" label="系统角色" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_system ? 'danger' : 'info'" size="small">{{ row.is_system ? '系统' : '自定义' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160" :formatter="(_r: any, _c: any, v: string) => formatTime(v)" />
      <el-table-column label="操作" min-width="260">
        <template #default="{ row }">
          <el-button size="small" @click="openEditModal(row)">编辑</el-button>
          <el-button size="small" @click="openPermModal(row)"><el-icon><Setting /></el-icon>配置权限</el-button>
          <el-button v-if="!row.is_system" size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create Modal -->
    <el-dialog v-model="createModalOpen" title="创建角色" width="500px">
      <el-form label-position="top">
        <el-form-item label="角色编码" required>
          <el-input v-model="createForm.role_code" placeholder="如: CONTENT_REVIEWER" />
        </el-form-item>
        <el-form-item label="角色名称" required>
          <el-input v-model="createForm.role_name" placeholder="如: 内容审核员" />
        </el-form-item>
        <el-form-item label="角色类型" required>
          <el-select v-model="createForm.role_type" placeholder="请选择" style="width: 100%">
            <el-option label="全局角色" value="GLOBAL" />
            <el-option label="场景角色" value="SCENARIO" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" :rows="3" placeholder="角色描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createModalOpen = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>

    <!-- Edit Modal -->
    <el-dialog v-model="editModalOpen" title="编辑角色" width="500px">
      <el-form label-position="top">
        <el-form-item label="角色名称" required>
          <el-input v-model="editForm.role_name" />
        </el-form-item>
        <el-form-item label="角色类型" required>
          <el-select v-model="editForm.role_type" style="width: 100%">
            <el-option label="全局角色" value="GLOBAL" />
            <el-option label="场景角色" value="SCENARIO" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editModalOpen = false">取消</el-button>
        <el-button type="primary" @click="handleEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- Permission Modal -->
    <el-dialog v-model="permModalOpen" :title="`配置权限 - ${selectedRole?.role_name}`" width="600px">
      <el-card shadow="never" style="margin-bottom: 16px">
        <template #header><span>全局权限</span></template>
        <el-checkbox-group v-model="selectedPermIds">
          <div v-for="p in globalPerms" :key="p.id" style="margin-bottom: 4px">
            <el-checkbox :value="p.id">{{ p.permission_name }} ({{ p.permission_code }})</el-checkbox>
          </div>
        </el-checkbox-group>
      </el-card>
      <el-card shadow="never">
        <template #header><span>场景权限</span></template>
        <el-checkbox-group v-model="selectedPermIds">
          <div v-for="p in scenarioPerms" :key="p.id" style="margin-bottom: 4px">
            <el-checkbox :value="p.id">{{ p.permission_name }} ({{ p.permission_code }})</el-checkbox>
          </div>
        </el-checkbox-group>
      </el-card>
      <template #footer>
        <el-button @click="permModalOpen = false">取消</el-button>
        <el-button type="primary" @click="handleSavePermissions">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
