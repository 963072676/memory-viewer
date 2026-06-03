<template>
  <div class="related-memories" v-if="loaded">
    <div class="related-header">
      <span class="related-title">🔗 相关记忆</span>
      <span class="related-count" v-if="recommendations.length">{{ recommendations.length }} 条</span>
    </div>
    <div v-if="recommendations.length === 0" class="related-empty">
      暂无相关记忆
    </div>
    <div v-else class="related-list">
      <div
        v-for="rec in recommendations"
        :key="rec.memory.id"
        class="related-item"
      >
        <div class="related-item-title">{{ rec.memory.title }}</div>
        <div class="related-item-meta">
          <span class="score-pill" :style="{ opacity: 0.4 + rec.score * 0.6 }">
            {{ (rec.score * 100).toFixed(0) }}%
          </span>
          <div class="shared-tags" v-if="rec.shared_concepts.length">
            <span class="shared-tag" v-for="c in rec.shared_concepts" :key="c">{{ c }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getRecommendations } from '@/api/agentmemory'
import type { RecommendationItem } from '@/types'

const props = defineProps<{
  memoryId: string
}>()

const loaded = ref(false)
const recommendations = ref<RecommendationItem[]>([])

onMounted(async () => {
  try {
    const data = await getRecommendations(props.memoryId, 5)
    recommendations.value = data.recommendations
  } catch (e) {
    console.error('Failed to load recommendations:', e)
  } finally {
    loaded.value = true
  }
})
</script>

<style scoped>
.related-memories {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.related-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.related-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary);
}

.related-count {
  font-size: 0.65rem;
  color: var(--text-secondary);
}

.related-empty {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-align: center;
  padding: 8px 0;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.related-item {
  padding: 6px 8px;
  background: var(--tag-bg);
  border-radius: 6px;
  cursor: default;
}

.related-item-title {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--primary);
  margin-bottom: 4px;
}

.related-item-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.score-pill {
  font-size: 0.6rem;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 8px;
  background: var(--accent);
  /* P38 r17: 改 hardcoded white → var(--card), 与 QuickAccessBar 同源 */
  color: var(--card);
}

.shared-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.shared-tag {
  font-size: 0.6rem;
  padding: 1px 5px;
  border-radius: 8px;
  background: var(--card);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}
</style>
