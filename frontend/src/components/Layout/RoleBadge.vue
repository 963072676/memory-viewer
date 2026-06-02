<template>
  <span class="role-badge" :class="role">
    {{ icon }} {{ label || role }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ role: string; label?: string }>()

const icon = computed(() => {
  switch (props.role) {
    case 'admin': return '👑'
    case 'editor': return '✏️'
    case 'viewer': return '👁️'
    default: return '👤'
  }
})
</script>

<style scoped>
.role-badge {
  display: inline-flex; align-items: center; gap: 3px;
  font-size: 0.7rem; font-weight: 600; padding: 2px 8px;
  border-radius: 4px; text-transform: capitalize;
}
.role-badge.admin { background: rgba(255,149,0,0.15); color: #ff9500; }
.role-badge.editor { background: rgba(0,113,227,0.1); color: #007aff; }
.role-badge.viewer { background: rgba(134,134,139,0.1); color: #86868b; }
</style>
