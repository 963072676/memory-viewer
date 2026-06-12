<template>
  <div class="stats-bar">
    <div class="stats">
      <div class="stat-item">
        <!-- P38 r10: count-up 动画 — 首屏载入有"数字滚动"感（沿用 r9 useCountUp） -->
        <strong>{{ isLoaded ? agentMemoriesDisplay : '—' }}</strong>
        <span>AgentMemory {{ $t('i18n.items') }}</span>
      </div>
      <div class="stat-item">
        <strong>{{ isLoaded ? hermesTotalDisplay : '—' }}</strong>
        <span>Hermes Memory {{ $t('i18n.items') }}</span>
      </div>
      <div class="stat-item">
        <strong>{{ isLoaded ? profilesCountDisplay : '—' }}</strong>
        <span>{{ $t('en_profiles') }}</span>
      </div>
    </div>
    <SortDropdown />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useAgentMemoryStore } from '@/stores/agentmemory'
import { useHermesMemoryStore } from '@/stores/hermes-memory'
import { useCountUp } from '@/composables/useCountUp'
import SortDropdown from './SortDropdown.vue'

const agentMemoryStore = useAgentMemoryStore()
const hermesMemoryStore = useHermesMemoryStore()

// P38 r10: 3 个 stat 数字 count-up — 沿用 r9 的 useCountUp composable
// duration 600ms 比 Dashboard 的 800ms 短一点（首页 3 个数字同步滚，更轻快）
// storeToRefs 保持响应式（pinia store 直接解构会丢失响应性 + 类型推到 number[]）
// BUG: useCountUp 接受函数 source 时不自动 watch（见 useCountUp.ts line 110-121），
// 所以这里必须传 Ref/computed 而不是函数，否则 value 永远是初始 0。

// P39 r1: 在 store 还没 fetch 完时显示 "—" 而不是 0（避免视觉"不一致"）。
// 两个 store (`agentmemory` + `hermes-memory`) 都 fetch 完才显示数字,
// 避免 count-up 动画中段被截图 / 用户看到中间值。
const { memories, lastFetch: agentLastFetch } = storeToRefs(agentMemoryStore)
const { totalEntries, profileNames, lastFetch: hermesLastFetch } = storeToRefs(hermesMemoryStore)
const isLoaded = computed(() => agentLastFetch.value !== null && hermesLastFetch.value !== null)

const { value: agentMemoriesDisplay } = useCountUp(computed(() => memories.value.length), { duration: 600 })
const { value: hermesTotalDisplay } = useCountUp(computed(() => totalEntries.value), { duration: 600 })
const { value: profilesCountDisplay } = useCountUp(computed(() => profileNames.value.length), { duration: 600 })
</script>

<style scoped>
/* P44: StatsBar 与 TabBar 形成"信息层 → 导航层"节奏。
   - margin-bottom 从 20 → --space-3 (12px)，让位给 TabBar 的 --space-5 margin-top，
     形成更清晰的 12 + 20 节奏（与 P40 spacing scale 一致）
   - 其它样式（border-bottom 1px solid var(--border)）保留 — StatsBar 仍是"信息行" */
.stats-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
  flex-wrap: wrap;
  gap: var(--space-4);
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--border);
}

.stats {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.stat-item {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-align: center;
}

.stat-item strong {
  display: block;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--primary);
  /* P38 r10: tabular-nums 让 count-up 动画数字宽度稳定（不抖） */
  font-variant-numeric: tabular-nums;
  font-feature-settings: 'tnum';
}

.stat-item span {
  display: block;
  margin-top: 2px;
}

/* Responsive */
@media (max-width: 767px) {
  .stats-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-3);
    margin-bottom: var(--space-2);
  }

  .stats {
    gap: var(--space-4);
    width: 100%;
    justify-content: space-between;
  }

  .stat-item {
    font-size: 0.75rem;
    flex: 1;
    min-width: 80px;
  }

  .stat-item strong {
    font-size: 1.1rem;
  }
}
</style>
