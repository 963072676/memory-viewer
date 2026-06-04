<template>
  <div class="digest-card">
    <div class="digest-meta">
      <span class="digest-type">{{ digest.type }}</span>
      <span class="digest-date">{{ formatDate(digest.generated_at) }}</span>
      <span class="digest-stats">{{ digest.stats?.total_memories || 0 }} memories</span>
    </div>

    <div class="digest-summary">{{ digest.summary }}</div>

    <!-- New Memories Section -->
    <div class="section" v-if="digest.sections?.new_memories?.length">
      <h4>🆕 New Memories</h4>
      <div class="memory-list">
        <div v-for="m in digest.sections.new_memories" :key="m.id" class="memory-item">
          <span class="memory-type">{{ m.type }}</span>
          <span class="memory-title">{{ m.title }}</span>
          <span v-for="tag in (m.tags || []).slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
        </div>
      </div>
    </div>

    <!-- Top Changes Section -->
    <div class="section" v-if="digest.sections?.top_changes?.length">
      <h4>🔄 Top Changes</h4>
      <div class="memory-list">
        <div v-for="m in digest.sections.top_changes" :key="m.id" class="memory-item">
          <span class="memory-type">{{ m.type }}</span>
          <span class="memory-title">{{ m.title }}</span>
        </div>
      </div>
    </div>

    <!-- Emerging Themes -->
    <div class="section" v-if="digest.sections?.emerging_themes?.length">
      <h4>🌟 Emerging Themes</h4>
      <div class="theme-cloud">
        <span v-for="t in digest.sections.emerging_themes" :key="t.theme" class="theme-tag" :style="{ fontSize: `${Math.min(1.2, 0.75 + t.count * 0.1)}rem` }">
          {{ t.theme }} ({{ t.count }})
        </span>
      </div>
    </div>

    <!-- Health Alerts -->
    <div class="section" v-if="digest.sections?.health_alerts?.length">
      <h4>⚠️ Health Alerts</h4>
      <div class="alert-list">
        <div v-for="a in digest.sections.health_alerts" :key="a.id" class="alert-item" :class="a.alert">
          <span class="alert-icon">{{ a.alert === 'critical' ? '🔴' : '🟡' }}</span>
          <span>{{ a.title }}</span>
          <span class="alert-score">{{ a.health_score }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ digest: any }>()

function formatDate(iso: string): string {
  if (!iso) return ''
  try { return new Date(iso).toLocaleString() } catch { return iso }
}
</script>

<style scoped>
.digest-card {
  background: var(--card, #fff); border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px; padding: 20px;
}
.digest-meta {
  display: flex; gap: 12px; align-items: center; margin-bottom: 16px;
  font-size: 0.8rem; color: var(--text-secondary, #86868b);
}
.digest-type {
  background: var(--accent, #007aff); color: var(--card); padding: 2px 8px;
  border-radius: 4px; font-weight: 600; text-transform: capitalize;
}
.digest-summary {
  font-size: 0.95rem; line-height: 1.6; color: var(--text, #1d1d1f);
  margin-bottom: 20px; padding: 12px; background: var(--tag-bg, #f5f5f7);
  border-radius: 8px;
}
.section { margin-bottom: 20px; }
.section h4 { margin: 0 0 8px; font-size: 0.95rem; font-weight: 600; color: var(--primary, #007aff); }
.memory-list { display: flex; flex-direction: column; gap: 6px; }
.memory-item {
  display: flex; align-items: center; gap: 8px; padding: 6px 10px;
  background: var(--tag-bg, #f5f5f7); border-radius: 6px; font-size: 0.85rem;
}
.memory-type {
  font-size: 0.7rem; background: var(--border, #e5e5ea); padding: 1px 6px;
  border-radius: 3px; font-weight: 500;
}
.memory-title { flex: 1; }
.tag {
  font-size: 0.7rem; background: rgba(0,113,227,0.1); color: var(--accent, #007aff);
  padding: 1px 6px; border-radius: 3px;
}
.theme-cloud { display: flex; flex-wrap: wrap; gap: 8px; }
.theme-tag {
  background: var(--tag-bg, #f5f5f7); padding: 4px 10px;
  border-radius: 12px; color: var(--primary, #007aff); font-weight: 500;
}
.alert-list { display: flex; flex-direction: column; gap: 6px; }
.alert-item {
  display: flex; align-items: center; gap: 8px; padding: 8px 10px;
  border-radius: 6px; font-size: 0.85rem;
}
.alert-item.critical { background: rgba(255,59,48,0.1); }
.alert-item.warning { background: rgba(255,149,0,0.1); }
.alert-score { margin-left: auto; font-weight: 600; }
</style>
