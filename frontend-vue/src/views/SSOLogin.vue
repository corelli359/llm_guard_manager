<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ssoApi } from '../api'
import { usePermissionStore } from '../stores/permission'

const router = useRouter()
const route = useRoute()
const permStore = usePermissionStore()
const status = ref<'loading' | 'success' | 'error'>('loading')
const errorMessage = ref('')

onMounted(async () => {
  const ticket = route.query.ticket as string
  const returnUrl = (route.query.return_url as string) || '/'

  if (!ticket) {
    status.value = 'error'
    errorMessage.value = '缺少Ticket参数，请从门户系统登录'
    return
  }

  try {
    const response = await ssoApi.login(ticket)
    const { access_token, role, user_id } = response.data

    localStorage.setItem('access_token', access_token)
    localStorage.setItem('user_role', role)
    localStorage.setItem('user_id', user_id)

    await permStore.fetchPermissions()
    status.value = 'success'

    setTimeout(() => {
      router.replace(returnUrl)
    }, 500)
  } catch (error: any) {
    status.value = 'error'
    errorMessage.value = error.response?.data?.detail || '登录失败，请重试'
  }
})

function handleBackToPortal() {
  const portalUrl = import.meta.env.VITE_PORTAL_URL || '/login'
  window.location.href = portalUrl
}
</script>

<template>
  <div class="sso-container">
    <div v-if="status === 'loading'" class="sso-center">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p style="color: #666; margin-top: 16px">正在登录，请稍候...</p>
    </div>

    <el-result v-else-if="status === 'error'" icon="error" title="登录失败" :sub-title="errorMessage">
      <template #extra>
        <el-button type="primary" @click="handleBackToPortal">返回门户系统</el-button>
        <el-button @click="() => location.reload()">重试</el-button>
      </template>
    </el-result>

    <el-result v-else icon="success" title="登录成功" sub-title="正在跳转..." />
  </div>
</template>

<style scoped>
.sso-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.sso-center {
  text-align: center;
}
</style>
