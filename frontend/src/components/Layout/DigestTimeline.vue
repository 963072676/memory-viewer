<template>
  <div class="digest-timeline">
    <div
      v-for="item in items"
      :key="item.id"
      class="timeline-item"
      @click="$emit('select', item.id)"
    >
      <div class="timeline-dot"></div>
      <div class="timeline-content">
        <div class="timeline-type">{{ item.type }}</div>
        <div class="timeline-date">{{ formatDate(item.generated_at) }}</div>
        <div class="timeline-count">{{ item.total_memories }} memories</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ items: any[] }>()
defineEmits<{ select: [id: string] }>()

function formatDate(iso: string): string {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch { return iso }
}
</script>

<style scoped>
.digest-timeline { display: flex; flex-direction: column; gap: 0; }
.timeline-item {
  display: flex; align-items: flex-start; gap: 12px; padding: 10px 0;
  cursor: pointer; border-left: 2px solid var(--border, #e5e5ea);
  padding-left: 16px; position: relative;
}
.timeline-item:hover { background: var(--tag-bg, #f5f5f7); border-radius: 0 8px 8px 0; }
.timeline-dot {
  width: 10px; height: 10px; background: var(--accent, #007aff);
  border-radius: 50%; position: absolute; left: -6px; top: 14px;
}
.timeline-content { flex: 1; }
.timeline-type {
  font-size: 0.75rem; font-weight: 600; text-transform: capitalize;
  color: var(--primary, #007aff);
}
.timeline-date { font-size: 0.75rem; color: var(--text-secondary, #86868b); }
.timeline-count { font-size: 0.7rem; color: var(--text-secondary, #86868b); }
</style>
