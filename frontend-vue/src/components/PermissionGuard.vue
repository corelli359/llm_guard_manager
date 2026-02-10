<script setup lang="ts">
import { computed } from 'vue'
import { usePermissionStore } from '../stores/permission'

const props = defineProps<{
  roles?: string[]
  scenarioId?: string
  permission?: string
}>()

const permStore = usePermissionStore()

const allowed = computed(() => {
  if (props.roles) return permStore.hasRole(props.roles)
  if (props.scenarioId && props.permission) return permStore.hasScenarioPermission(props.scenarioId, props.permission)
  if (props.permission) return permStore.hasPermission(props.permission)
  return true
})
</script>

<template>
  <slot v-if="allowed" />
  <slot v-else name="fallback" />
</template>
