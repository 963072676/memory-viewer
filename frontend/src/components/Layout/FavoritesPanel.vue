<template>
  <div class="favorites-panel">
    <div class="section-header" @click="expanded = !expanded">
      <span class="header-icon">⭐</span>
      <span class="header-label">{{ $t('en_favorites') }}</span>
      <span class="header-count" v-if="favorites.length">{{ favorites.length }}</span>
      <span class="expand-arrow">{{ expanded ? '▲' : '▼' }}</span>
    </div>
    <transition name="slide">
      <div v-if="expanded" class="favorites-list">
        <div v-if="loading" class="fav-loading">{{ $t('en_loading_dots') }}</div>
        <div v-else-if="favorites.length === 0" class="fav-empty">{{ $t('en_no_favorites') }}</div>
        <div
          v-for="fav in favorites"
          :key="fav.memory_id"
          class="fav-item"
          @click="navigateToMemory(fav.memory_id)"
        >
          <span class="fav-icon">{{ typeIcon(fav.type) }}</span>
          <span class="fav-title">{{ fav.title }}</span>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getFavorites, type FavoriteItem } from '@/api/favorites'

const router = useRouter()
const expanded = ref(true)
const loading = ref(false)
const favorites = ref<FavoriteItem[]>([])

function typeIcon(type: string): string {
  const icons: Record<string, string> = {
    pattern: '🟢',
    fact: '🔵',
    preference: '🔴',
    bug: '🟠',
    workflow: '🟣',
    architecture: '🩵',
  }
  return icons[type] || '📄'
}

function navigateToMemory(id: string) {
  router.push({ path: '/', query: { highlight: id } })
}

async function loadFavorites() {
  loading.value = true
  try {
    const res = await getFavorites()
    favorites.value = res.favorites
  } catch {
    favorites.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadFavorites)

defineExpose({ refresh: loadFavorites })
</script>

<style scoped>
.favorites-panel {
  margin-top: 8px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: background 0.2s;
}

.section-header:hover {
  background: var(--tag-bg);
  border-radius: var(--radius);
}

.header-icon {
  font-size: 0.9rem;
}

.header-label {
  flex: 1;
}

.header-count {
  background: var(--accent);
  /* P38 r19: 改 hardcoded white → var(--card), 与全站 token 对齐 */
  color: var(--card);
  font-size: 0.6rem;
  padding: 1px 6px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
}

.expand-arrow {
  font-size: 0.6rem;
}

.favorites-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 4px 0;
}

.fav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px 6px 24px;
  cursor: pointer;
  border-radius: var(--radius);
  transition: background 0.2s;
  font-size: 0.8rem;
  color: var(--primary);
}

.fav-item:hover {
  background: var(--tag-bg);
}

.fav-icon {
  font-size: 0.75rem;
  flex-shrink: 0;
}

.fav-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.fav-loading,
.fav-empty {
  padding: 8px 24px;
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-style: italic;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
}

.slide-enter-to,
.slide-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>
