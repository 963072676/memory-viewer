<template>
  <div class="smart-collections">
    <div class="section-header">{{ $t('i18n.smart_collection') }}</div>
    <div
      v-for="col in store.collections"
      :key="col.id"
      class="collection-item"
      :class="{ active: activeCollection === col.id }"
      @click="selectCollection(col.id)"
    >
      <span class="collection-icon">{{ iconMap[col.icon] || col.icon }}</span>
      <span class="collection-name">{{ col.name }}</span>
      <span class="collection-count">{{ col.count }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAgentMemoryStore } from '@/stores/agentmemory'

// Icon name → emoji mapping (backend returns Lucide-style names)
const iconMap: Record<string, string> = {
  clock: '🕐',
  zap: '⚡',
  heart: '❤️',
  tag: '🏷️',
  refresh: '🔄',
  archive: '📦',
  star: '⭐',
  alert: '⚠️',
  folder: '📁',
  file: '📄',
  search: '🔍',
  bookmark: '🔖',
  brain: '🧠',
  lightbulb: '💡',
  bug: '🐛',
  code: '💻',
  globe: '🌐',
  lock: '🔒',
  user: '👤',
  layers: '📚',
}

const store = useAgentMemoryStore()
const route = useRoute()
const router = useRouter()

const activeCollection = computed(() => {
  const q = route.query.collection
  return typeof q === 'string' ? q : null
})

function selectCollection(id: string) {
  // Toggle off if already active
  if (activeCollection.value === id) {
    router.push({ query: { ...route.query, collection: undefined } })
  } else {
    router.push({ query: { ...route.query, collection: id } })
  }
}

// Fetch collections on first use
if (store.collections.length === 0) {
  store.loadCollections()
}
</script>

<style scoped>
.smart-collections {
  margin-top: 8px;
}

.section-header {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 8px 16px 4px;
}

.collection-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  border-radius: var(--radius);
  cursor: pointer;
  transition: background 0.2s;
  color: var(--primary);
  font-size: 0.85rem;
}

.collection-item:hover {
  background: var(--tag-bg);
}

.collection-item.active {
  background: var(--accent);
  /* P38 r19: 改 hardcoded white → var(--card), 与全站 token 对齐 */
  color: var(--card);
}

.collection-icon {
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}

.collection-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.collection-count {
  background: var(--accent);
  /* P38 r19: 改 hardcoded white → var(--card), 与全站 token 对齐 */
  color: var(--card);
  font-size: 0.65rem;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
  line-height: 1.2;
}

.collection-item.active .collection-count {
  background: rgba(255, 255, 255, 0.3);
  color: white;
}
</style>
