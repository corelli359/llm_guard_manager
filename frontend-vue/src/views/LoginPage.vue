<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'

const router = useRouter()
const loading = ref(false)
const loginType = ref('admin')
const form = ref({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const formRef = ref()

async function handleLogin() {
  try {
    await formRef.value?.validate()
  } catch { return }

  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('username', form.value.username)
    params.append('password', form.value.password)

    const response = await api.post('/login/access-token', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })

    const role = response.data.role
    localStorage.setItem('access_token', response.data.access_token)
    localStorage.setItem('user_role', role)

    if (loginType.value === 'admin' && role !== 'ADMIN') {
      ElMessage.warning('您不是管理员，已跳转至审核界面')
    } else if (loginType.value === 'auditor' && role === 'ADMIN') {
      ElMessage.info('检测到管理员账号登录')
    }

    ElMessage.success('登录成功！')
    router.push('/')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '登录失败，请检查用户名和密码。')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 style="text-align: center; margin-bottom: 24px">LLM Guard 管理平台</h2>
      <el-tabs v-model="loginType" stretch>
        <el-tab-pane label="管理员登录" name="admin" />
        <el-tab-pane label="审核员登录" name="auditor" />
      </el-tabs>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="0" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" size="large" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" size="large" style="width: 100%" @click="handleLogin">
            立即登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
}
.login-card {
  width: 400px;
}
</style>
