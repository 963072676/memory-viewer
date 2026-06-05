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
/* P47 r1: RoleBadge 3 角色硬编码 Apple hex → 全站 token (与 P45 r1 HealthBadge 决策树同源).
   之前 admin/editor/viewer 各自硬编码 #ff9500 / #007aff / #86868b, 在 dark 模式看到的依然是
   "light mode 字面 hex" — 与 P38 r19 theme-contract sweep 漏掉的最后一组 on-accent 类色对.
   替换策略:
   - admin (运营者/橙色) → --warning-bg / --warning (与全站"提醒/待办"语义统一, dark 模式自动 #3e2a0a / #ffb84d)
   - editor (编辑者/蓝色) → --accent-subtle / --accent (与全站"主品牌"语义统一, dark 模式自动调整)
   - viewer (观察者/灰色) → --tag-bg / --text-secondary (与全站"中性/默认"语义统一)
   触达: MemoryDetailView 顶部 role 标识 (高频), SettingsView 团队成员列表, 任何展示 role 的角落. */
.role-badge.admin { background: var(--warning-bg); color: var(--warning); }
.role-badge.editor { background: var(--accent-subtle); color: var(--accent); }
.role-badge.viewer { background: var(--tag-bg); color: var(--text-secondary); }
</style>
