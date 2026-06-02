<template>
  <div class="issue-card" :class="issue.severity">
    <div class="issue-header">
      <span class="severity-badge">{{ issue.severity }}</span>
      <span class="issue-category">{{ issue.category }}</span>
    </div>
    <h4 class="issue-title">{{ issue.title }}</h4>
    <p class="issue-desc">{{ issue.description }}</p>
    <div class="issue-footer">
      <span class="affected-count" v-if="issue.affected_count">
        {{ issue.affected_count }} {{ issue.affected_count === 1 ? 'memory' : 'memories' }} affected
      </span>
      <span class="issue-suggestion" v-if="issue.suggestion">
        💡 {{ issue.suggestion }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  issue: {
    id: string
    severity: 'critical' | 'warning' | 'info'
    category: string
    title: string
    description: string
    affected_count: number
    suggestion?: string
  }
}>()
</script>

<style scoped>
.issue-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  transition: box-shadow 0.2s;
}

.issue-card:hover {
  box-shadow: var(--shadow);
}

.issue-card.critical {
  border-left: 4px solid #ef4444;
}

.issue-card.warning {
  border-left: 4px solid #eab308;
}

.issue-card.info {
  border-left: 4px solid #3b82f6;
}

.issue-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.severity-badge {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 4px;
}

.critical .severity-badge {
  background: #fef2f2;
  color: #dc2626;
}

.warning .severity-badge {
  background: #fefce8;
  color: #ca8a04;
}

.info .severity-badge {
  background: #eff6ff;
  color: #2563eb;
}

.issue-category {
  font-size: 0.7rem;
  color: var(--text-secondary);
  text-transform: capitalize;
}

.issue-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--primary);
  margin: 0 0 6px;
}

.issue-desc {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 10px;
}

.issue-footer {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.affected-count {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary);
  background: var(--tag-bg);
  padding: 2px 8px;
  border-radius: 4px;
}

.issue-suggestion {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-style: italic;
}
</style>
