<template>
  <div class="conflict-card" :class="'severity-' + conflict.severity">
    <div class="conflict-header">
      <div class="severity-badge" :class="'severity-' + conflict.severity">
        {{ severityIcons[conflict.severity] || '⚠️' }}
        {{ conflict.severity }}
      </div>
      <div class="conflict-type">{{ conflictLabels[conflict.conflict_type] || conflict.conflict_type }}</div>
      <div class="similarity">相似度: {{ (conflict.similarity * 100).toFixed(0) }}%</div>
    </div>

    <div class="conflict-body">
      <div class="memory-side">
        <div class="side-label">记忆 A</div>
        <div class="memory-title">{{ conflict.memory_a.title }}</div>
        <div class="memory-content">{{ conflict.memory_a.content }}</div>
        <div class="memory-meta">
          <span class="memory-type">{{ conflict.memory_a.type }}</span>
          <span class="memory-strength">💪 {{ (conflict.memory_a.strength * 10).toFixed(0) }}%</span>
        </div>
      </div>
      <div class="vs-divider">⚡ VS</div>
      <div class="memory-side">
        <div class="side-label">记忆 B</div>
        <div class="memory-title">{{ conflict.memory_b.title }}</div>
        <div class="memory-content">{{ conflict.memory_b.content }}</div>
        <div class="memory-meta">
          <span class="memory-type">{{ conflict.memory_b.type }}</span>
          <span class="memory-strength">💪 {{ (conflict.memory_b.strength * 10).toFixed(0) }}%</span>
        </div>
      </div>
    </div>

    <div v-if="conflict.resolved" class="conflict-resolved">
      ✅ 已解决: {{ conflict.resolution?.action }} ({{ conflict.resolution?.resolved_by }})
    </div>
    <div v-else class="conflict-actions">
      <button class="btn-resolve keep-a" @click="$emit('resolve', conflict.id, 'keep_a')">保留 A</button>
      <button class="btn-resolve keep-b" @click="$emit('resolve', conflict.id, 'keep_b')">保留 B</button>
      <button class="btn-resolve merge" @click="$emit('resolve', conflict.id, 'merge')">合并</button>
      <button class="btn-resolve dismiss" @click="$emit('resolve', conflict.id, 'dismiss')">忽略</button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  conflict: any
}>()

defineEmits<{
  resolve: [id: string, action: string]
}>()

const severityIcons: Record<string, string> = {
  high: '🔴',
  medium: '🟠',
  low: '🟡',
}

const conflictLabels: Record<string, string> = {
  direct_contradiction: '直接矛盾',
  outdated_info: '信息过时',
  partial_overlap: '部分重叠',
}
</script>

<style scoped>
.conflict-card {
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px;
  padding: 16px;
  background: var(--card, #fff);
  margin-bottom: 12px;
  transition: border-color 0.2s;
}

.conflict-card.severity-high {
  border-left: 4px solid #ff3b30;
}

.conflict-card.severity-medium {
  border-left: 4px solid #ff9500;
}

.conflict-card.severity-low {
  border-left: 4px solid #ffcc00;
}

.conflict-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.severity-badge {
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.severity-badge.severity-high { background: #ffe5e5; color: #ff3b30; }
.severity-badge.severity-medium { background: #fff3e0; color: #ff9500; }
.severity-badge.severity-low { background: #fffde5; color: #b38b00; }

.conflict-type {
  font-size: 0.8rem;
  color: var(--text-secondary, #86868b);
  font-weight: 500;
}

.similarity {
  font-size: 0.75rem;
  color: var(--text-secondary, #86868b);
  margin-left: auto;
}

.conflict-body {
  display: flex;
  gap: 12px;
  align-items: stretch;
}

.memory-side {
  flex: 1;
  padding: 12px;
  background: var(--bg, #f2f2f7);
  border-radius: 8px;
}

.side-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-secondary, #86868b);
  text-transform: uppercase;
  margin-bottom: 4px;
}

.memory-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text, #1d1d1f);
  margin-bottom: 4px;
}

.memory-content {
  font-size: 0.8rem;
  color: var(--text-secondary, #86868b);
  margin-bottom: 8px;
  line-height: 1.4;
}

.memory-meta {
  display: flex;
  gap: 8px;
  font-size: 0.7rem;
}

.memory-type {
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--tag-bg, #f2f2f7);
  color: var(--text-secondary, #86868b);
}

.vs-divider {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-secondary, #86868b);
}

.conflict-resolved {
  margin-top: 12px;
  padding: 8px;
  background: #e8f5e9;
  border-radius: 6px;
  font-size: 0.8rem;
  color: #2e7d32;
}

.conflict-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.btn-resolve {
  padding: 6px 14px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 6px;
  background: var(--card, #fff);
  font-size: 0.8rem;
  cursor: pointer;
  font-family: var(--font);
  font-weight: 500;
  transition: background 0.2s;
}

.btn-resolve:hover {
  background: var(--tag-bg, #f2f2f7);
}

.btn-resolve.keep-a { color: #007aff; border-color: #007aff; }
.btn-resolve.keep-b { color: #34c759; border-color: #34c759; }
.btn-resolve.merge { color: #ff9500; border-color: #ff9500; }
.btn-resolve.dismiss { color: var(--text-secondary, #86868b); }

@media (max-width: 640px) {
  .conflict-body { flex-direction: column; }
  .vs-divider { justify-content: center; }
}
</style>
