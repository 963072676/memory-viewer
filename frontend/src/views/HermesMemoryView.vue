<template>
  <div class="hermes-view">
    <h2 class="section-title">{{ $t('en_hermes_memory') }}</h2>
    <div v-if="store.loading" class="card-grid">
      <div v-for="i in 4" :key="i" class="skeleton-card"></div>
    </div>
    <div v-else-if="store.totalEntries === 0">
      <!-- P38 r30: EmptyState message prop 改 v-bind (i18n 触发) -->
      <EmptyState icon="🧠" :message="`${$t('i18n.no')} Hermes Memory ${$t('i18n.data')}`" />
    </div>
    <template v-else>
      <!-- Global -->
      <div class="profile-section">
        <h3 class="profile-heading">{{ $t('en_global_with_icon') }}</h3>
        <div class="card-grid">
          <div v-for="(entry, i) in store.globalData.memory" :key="'gm-' + i" class="hermes-card">
            <div class="hermes-label"><span class="hermes-label__dot" />MEMORY.md</div>
            <p>{{ entry }}</p>
          </div>
          <div v-for="(entry, i) in store.globalData.user" :key="'gu-' + i" class="hermes-card">
            <div class="hermes-label"><span class="hermes-label__dot" />USER.md</div>
            <p>{{ entry }}</p>
          </div>
        </div>
      </div>
      <!-- Profiles -->
      <div v-for="(data, name) in store.profiles" :key="name" class="profile-section">
        <h3 class="profile-heading">👤 {{ name }}</h3>
        <div class="card-grid">
          <div v-for="(entry, i) in data.memory" :key="'pm-' + i" class="hermes-card">
            <div class="hermes-label"><span class="hermes-label__dot" />MEMORY.md</div>
            <p>{{ entry }}</p>
          </div>
          <div v-for="(entry, i) in data.user" :key="'pu-' + i" class="hermes-card">
            <div class="hermes-label"><span class="hermes-label__dot" />USER.md</div>
            <p>{{ entry }}</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useHermesMemoryStore } from '@/stores/hermes-memory'
import EmptyState from '@/components/Layout/EmptyState.vue'
const store = useHermesMemoryStore()
</script>

<style scoped>
.hermes-view {
  padding-bottom: 40px;
}

h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 24px;
  letter-spacing: -0.02em;
}

/* P38 r20: section-title 左侧 3px accent bar — 与 HomeView / AppSidebar 同源 (r15 模式).
   让 Hermes view 的页面标题与 AgentMemory / Dashboard 等其他 view 的 section title
   共享同一视觉语言。3px 圆角条 + 12px padding-left + 60% 高度居中。 */
.section-title {
  position: relative;
  padding-left: 12px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--accent);
  border-radius: 0 2px 2px 0;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.profile-section {
  margin-bottom: 32px;
}

.profile-heading {
  position: relative;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--primary);
  /* P38 r28: h3 视觉锚点 — 2px accent bar 左侧 rail.
     与 r27 section-title 3px bar 同源但 h3 视觉重量更轻 → 用 2px 而非 3px.
     之前 h3 是无视觉锚点的纯文字, 在 in-page 多 section 排版时无分组感.
     2px bar + 10px padding-left 让 h3 与下方 hermes-card 视觉断点更清晰. */
  padding-left: 10px;
}

.profile-heading::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 2px;
  height: 70%;
  background: var(--accent);
  border-radius: 0 2px 2px 0;
}

/* P38 r20: .hermes-card 视觉升级 — 与 MemoryCard 视觉语言同源 (hover + shadow + translateY).
   之前 .hermes-card 是纯静态 card (无 hover, 无 shadow, 无 transition), 扫视时与上下
   MemoryCard 形成"粗糙/精细"对比。统一 hover 语言后用户跨 view 切换无视觉跳变。 */
.hermes-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}

.hermes-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-3px);
}

/* P38 r20: .hermes-label 加 5px accent dot prefix + 1px border + inline-flex —
   复用 r15 MemoryDetailView type-chip 的"dot + uppercase + 1px 边框"视觉语言。
   让 MEMORY.md / USER.md 标签从"无锚点的小灰字"升级为"视觉锚点小色块",
   与 list 卡片里的 type chip 形成统一 badge 节奏。 */
.hermes-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.7rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
  padding: 2px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--tag-bg);
}

.hermes-label__dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
  flex-shrink: 0;
  opacity: 0.85;
}

.hermes-card p {
  font-size: 0.875rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.skeleton-card {
  height: 80px;
  background: linear-gradient(90deg, var(--tag-bg) 25%, var(--border) 50%, var(--tag-bg) 75%);
  background-size: 200% 100%;
  border-radius: var(--radius);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Responsive */
@media (max-width: 767px) {
  h2 {
    font-size: 1.2rem;
  }

  .card-grid {
    grid-template-columns: 1fr;
  }

  .hermes-card p {
    font-size: 0.825rem;
  }

  .skeleton-card {
    height: 60px;
  }
}
</style>
