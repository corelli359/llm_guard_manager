<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usersApi, userRolesApi, rolesApi, scenariosApi, getErrorMessage } from '../api'
import type { User, Role, ScenarioApp, UserRoleAssignment } from '../types'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const users = ref<User[]>([])
const roles = ref<Role[]>([])
const scenarios = ref<ScenarioApp[]>([])
const loading = ref(false)
const assignModalOpen = ref(false)
const rolesDrawerOpen = ref(false)
const selectedUser = ref<User | null>(null)
const userRoleAssignments = ref<UserRoleAssignment[]>([])
const selectedRoleType = ref('')

const assignForm = ref({ role_id: '', scenario_id: '' })

async function fetchUsers() {
  loading.value = true
  try { users.value = (await usersApi.list()).data }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '获取用户列表失败')) }
  finally { loading.value = false }
}
async function fetchRoles() {
  try { roles.value = (await rolesApi.list()).data } catch { /* ignore */ }
}
async function fetchScenarios() {
  try { scenarios.value = (await scenariosApi.getAll()).data } catch { /* ignore */ }
}

async function handleStatusChange(row: User, val: boolean) {
  try { await usersApi.updateStatus(row.id, val); ElMessage.success('状态已更新'); fetchUsers() }
  catch (e: any) { ElMessage.error(getErrorMessage(e, '更新失败')) }
}

async function handleDelete(row: User) {
  try {
    await ElMessageBox.confirm('确定删除用户吗?', '确认')
    await usersApi.delete(row.id); ElMessage.success('用户已删除'); fetchUsers()
  } catch (e: any) { if (e !== 'cancel') ElMessage.error(getErrorMessage(e, '删除失败')) }
}

function openAssignModal(user: User) {
  selectedUser.value = user
  selectedRoleType.value = ''
  assignForm.value = { role_id: '', scenario_id: '' }
  assignModalOpen.value = true
}

function handleRoleSelectChange(roleId: string) {
  const role = roles.value.find(r => r.id === roleId)
  selectedRoleType.value = role?.role_type || ''
  if (role?.role_type === 'GLOBAL') assignForm.value.scenario_id = ''
}

async function handleAssignRole() {
  if (!selectedUser.value || !assignForm.value.role_id) return
  try {
    const data: any = { role_id: assignForm.value.role_id }
    if (assignForm.value.scenario_id) data.scenario_id = assignForm.value.scenario_id
    await userRolesApi.assignRole(selectedUser.value.id, data)
    ElMessage.success('角色分配成功'); assignModalOpen.value = false; fetchUsers()
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '分配失败')) }
}

async function openRolesDrawer(user: User) {
  selectedUser.value = user
  try {
    userRoleAssignments.value = (await userRolesApi.getUserRoles(user.id)).data
    rolesDrawerOpen.value = true
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '获取用户角色失败')) }
}

async function handleRemoveRole(assignmentId: string) {
  if (!selectedUser.value) return
  try {
    await userRolesApi.removeRole(selectedUser.value.id, assignmentId)
    ElMessage.success('角色已移除')
    userRoleAssignments.value = (await userRolesApi.getUserRoles(selectedUser.value.id)).data
  } catch (e: any) { ElMessage.error(getErrorMessage(e, '移除失败')) }
}

// PLACEHOLDER_MORE
const isSelf = (row: User) => row.user_id === localStorage.getItem('user_id')
const roleColorMap: Record<string, string> = { SYSTEM_ADMIN: 'danger', SCENARIO_ADMIN: '', ANNOTATOR: 'success', AUDITOR: 'warning' }
const roleLabelMap: Record<string, string> = { SYSTEM_ADMIN: '系统管理员', SCENARIO_ADMIN: '场景管理员', ANNOTATOR: '标注员', AUDITOR: '审计员' }
function formatTime(t: string) { return dayjs(t).format('YYYY-MM-DD HH:mm') }

onMounted(() => { fetchUsers(); fetchRoles(); fetchScenarios() })
</script>

<template>
  <div style="padding: 24px">
    <div style="margin-bottom: 16px">
      <h2 style="margin: 0">用户管理</h2>
      <p style="color: #666; margin: 4px 0 0">SSO 用户首次登录后自动创建，在此管理角色和权限。</p>
    </div>

    <el-table :data="users" v-loading="loading" row-key="id" style="width: 100%">
      <el-table-column prop="user_id" label="用户ID" width="150">
        <template #default="{ row }">{{ row.user_id || '-' }}</template>
      </el-table-column>
      <el-table-column prop="username" label="用户名" width="120">
        <template #default="{ row }">{{ row.username || '-' }}</template>
      </el-table-column>
      <el-table-column prop="display_name" label="姓名" width="120">
        <template #default="{ row }">{{ row.display_name || '-' }}</template>
      </el-table-column>
      <el-table-column prop="role" label="角色" width="130">
        <template #default="{ row }">
          <el-tag :type="roleColorMap[row.role] || 'info'" size="small">{{ roleLabelMap[row.role] || row.role }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="100">
        <template #default="{ row }">
          <el-switch v-model="row.is_active" :disabled="isSelf(row)" active-text="启用" inactive-text="禁用" @change="(v: boolean) => handleStatusChange(row, v)" />
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160" :formatter="(_r: any, _c: any, v: string) => formatTime(v)" />
      <el-table-column label="操作" min-width="260" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openAssignModal(row)"><el-icon><UserFilled /></el-icon>分配角色</el-button>
          <el-button size="small" @click="openRolesDrawer(row)"><el-icon><View /></el-icon>查看角色</el-button>
          <el-button size="small" type="danger" :disabled="isSelf(row)" @click="handleDelete(row)"><el-icon><Delete /></el-icon></el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Assign Role Modal -->
    <el-dialog v-model="assignModalOpen" :title="`为用户 ${selectedUser?.user_id} 分配角色`" width="500px">
      <el-form label-position="top">
        <el-form-item label="选择角色" required>
          <el-select v-model="assignForm.role_id" placeholder="请选择角色" style="width: 100%" @change="handleRoleSelectChange">
            <el-option v-for="r in roles" :key="r.id" :value="r.id" :label="`${r.role_name} (${r.role_code})`">
              <span>{{ r.role_name }} ({{ r.role_code }})</span>
              <el-tag :type="r.role_type === 'GLOBAL' ? '' : 'success'" size="small" style="margin-left: 8px">{{ r.role_type === 'GLOBAL' ? '全局' : '场景' }}</el-tag>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item v-if="selectedRoleType === 'SCENARIO'" label="选择场景" required>
          <el-select v-model="assignForm.scenario_id" placeholder="请选择场景" style="width: 100%">
            <el-option v-for="s in scenarios" :key="s.app_id" :value="s.app_id" :label="`${s.app_name} (${s.app_id})`" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignModalOpen = false">取消</el-button>
        <el-button type="primary" @click="handleAssignRole">分配</el-button>
      </template>
    </el-dialog>

    <!-- Roles Drawer -->
    <el-drawer v-model="rolesDrawerOpen" :title="`用户角色列表 - ${selectedUser?.user_id}`" direction="rtl" size="600px">
      <p v-if="userRoleAssignments.length === 0">该用户还没有分配任何角色</p>
      <div v-else style="display: flex; flex-direction: column; gap: 12px">
        <el-card v-for="a in userRoleAssignments" :key="a.id" shadow="never">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>
                <el-icon><UserFilled /></el-icon> {{ a.role_name }}
                <el-tag :type="a.role_type === 'GLOBAL' ? '' : 'success'" size="small" style="margin-left: 8px">{{ a.role_type === 'GLOBAL' ? '全局' : '场景' }}</el-tag>
              </span>
              <el-popconfirm title="确定移除该角色吗?" @confirm="handleRemoveRole(a.id)">
                <template #reference><el-button size="small" type="danger">移除</el-button></template>
              </el-popconfirm>
            </div>
          </template>
          <p><strong>角色编码:</strong> {{ a.role_code }}</p>
          <p v-if="a.scenario_id"><strong>场景ID:</strong> {{ a.scenario_id }}</p>
          <p><strong>分配时间:</strong> {{ formatTime(a.created_at) }}</p>
        </el-card>
      </div>
    </el-drawer>
  </div>
</template>
