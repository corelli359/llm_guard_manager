<template>
  <el-card>
    <h2>欢迎回来, {{ userId }}</h2>
    <p>您的角色是: {{ role }}</p>
    <el-divider />
    <el-alert title="系统正常运行中" type="success" show-icon :closable="false" />
  </el-card>
</template>

<script setup lang="ts">
const userId = localStorage.getItem('user_id')
const role = localStorage.getItem('user_role')
</script>
