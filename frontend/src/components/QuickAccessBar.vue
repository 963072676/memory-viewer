<template>
  <div class="quick-access-bar">
    <div class="quick-buttons">
      <button
        v-for="btn in buttons"
        :key="btn.id"
        class="quick-btn"
        :class="{ active: activeButton === btn.id }"
        :aria-pressed="activeButton === btn.id"
        @click="selectButton(btn)"
      >
        <span class="quick-btn__icon">{{ btn.icon }}</span>
        <span class="quick-btn__label">{{ $t(btn.labelKey) }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const STORAGE_KEY = 'quick-access-active'

interface QuickButton {
  id: string
  labelKey: string
  icon: string
  route?: string
  query?: Record<string, string>
}

const router = useRouter()
const route = useRoute()
const activeButton = ref('all')

const buttons: QuickButton[] = [
  { id: 'all', labelKey: 'i18n.quick_all_memories', icon: '📋', route: '/' },
  { id: 'favorites', labelKey: 'i18n.quick_favorites', icon: '⭐', route: '/', query: { filter: 'favorite' } },
  { id: 'recent7', labelKey: 'i18n.quick_recent_7_days', icon: '📅', route: '/', query: { filter: 'recent7' } },
  { id: 'graph', labelKey: 'i18n.quick_graph', icon: '📊', route: '/graph' },
]

function selectButton(btn: QuickButton) {
  activeButton.value = btn.id
  localStorage.setItem(STORAGE_KEY, btn.id)

  if (!btn.route) return
  if (btn.query) {
    router.push({ path: btn.route, query: btn.query })
  } else {
    router.push(btn.route)
  }
}

function syncActiveFromRoute() {
  const path = route.path
  const filter = route.query.filter as string

  if (path === '/graph') {
    activeButton.value = 'graph'
  } else if (path === '/' && filter === 'favorite') {
    activeButton.value = 'favorites'
  } else if (path === '/' && filter === 'recent7') {
    activeButton.value = 'recent7'
  } else if (path === '/') {
    activeButton.value = 'all'
  }
}

watch(() => route.fullPath, syncActiveFromRoute)

onMounted(() => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved && buttons.some(b => b.id === saved)) {
    const btn = buttons.find(b => b.id === saved)!
    activeButton.value = saved
    if (btn.route) {
      if (btn.query) {
        router.replace({ path: btn.route, query: btn.query })
      } else {
        router.replace(btn.route)
      }
    }
  }
  syncActiveFromRoute()
})
</script>

<style scoped>
.quick-access-bar {
  margin-bottom: 16px;
}

.quick-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-family: var(--font);
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-btn:hover {
  background: var(--tag-bg);
  color: var(--primary);
  border-color: var(--accent);
}

.quick-btn.active {
  background: var(--accent);
  /* P38 r17: 改 hardcoded #fff → var(--card) (与全站 token 契约一致, light=白, dark=深底).
     此前 dark 模式 active 按钮文字是 #fff (固定白), 在 dark 背景上对比度过高且刺眼。
     用 --card 后 active 按钮的 fg 跟随主题底色翻转, 维持 "accent 背景 + 主题反色文字" 的对比. */
  color: var(--card);
  border-color: var(--accent);
  font-weight: 500;
}

.quick-btn__icon {
  font-size: 0.9rem;
}

.quick-btn__label {
  white-space: nowrap;
}
</style>
