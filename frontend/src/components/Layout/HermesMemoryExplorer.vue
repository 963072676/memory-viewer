<template>
  <div class="hermes-explorer">
    <div class="section-header">
      <h2 class="section-title">{{ $t('en_hermes_memory') }}</h2>
      <span v-if="visibleEntryCount > 0" class="entry-count">
        {{ $t('i18n.hermes_entry_count', { count: visibleEntryCount }) }}
      </span>
    </div>

    <div v-if="loading && memories.length === 0" class="card-grid" aria-live="polite">
      <div v-for="i in 4" :key="i" class="skeleton-card"></div>
    </div>

    <div v-else-if="error && memories.length === 0" class="error-state" role="alert">
      <div class="error-copy">
        <strong>{{ $t('i18n.load_failed') }}</strong>
        <span>{{ $t('i18n.hermes_load_failed') }}</span>
      </div>
      <button type="button" class="action-btn" @click="loadMemories">
        {{ $t('i18n.retry') }}
      </button>
    </div>

    <template v-else>
      <div v-if="error" class="error-state error-state--inline" role="alert">
        <div class="error-copy">
          <strong>{{ $t('i18n.load_failed') }}</strong>
          <span>{{ $t('i18n.hermes_load_failed') }}</span>
        </div>
        <button type="button" class="action-btn" @click="loadMemories">
          {{ $t('i18n.retry') }}
        </button>
      </div>

      <div v-if="visibleEntryCount === 0" class="empty-state-wrap">
        <EmptyState
          icon="🧠"
          :title="$t('i18n.hermes_empty_title')"
          :message="$t('i18n.hermes_empty_message')"
          :action-text="$t('i18n.source_management')"
          @action="router.push('/sources')"
        />
      </div>

      <div
        v-else
        class="explorer-shell"
        :class="{ 'explorer-shell--with-preview': selectedMemory }"
      >
        <div class="explorer-main">
          <section v-for="group in visibleGroups" :key="group.id" class="profile-section">
            <h3 class="profile-heading">{{ group.label }}</h3>
            <div class="card-grid">
              <button
                v-for="entry in group.entries"
                :key="entry.memory.id"
                type="button"
                class="hermes-card"
                :class="{ 'hermes-card--selected': selectedId === entry.memory.id }"
                :aria-pressed="selectedId === entry.memory.id"
                @click="selectedId = entry.memory.id"
              >
                <span class="hermes-label">
                  <span class="hermes-label__dot" aria-hidden="true"></span>
                  {{ entry.file }}
                  <span class="hermes-index">#{{ entry.index + 1 }}</span>
                </span>
                <p>{{ entry.memory.content }}</p>
              </button>
            </div>
          </section>
        </div>

        <MemoryPreviewPanel
          v-if="selectedMemory"
          :unified-memory="selectedMemory"
          @close="selectedId = ''"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { fetchUnifiedMemories, type UnifiedMemory } from '@/api/sources'
import EmptyState from '@/components/Layout/EmptyState.vue'
import MemoryPreviewPanel from '@/components/Layout/MemoryPreviewPanel.vue'

const props = withDefaults(defineProps<{
  profile?: string
}>(), {
  profile: '',
})

interface HermesEntry {
  file: string
  index: number
  memory: UnifiedMemory
}

interface HermesGroup {
  id: string
  label: string
  entries: HermesEntry[]
}

const router = useRouter()
const { t } = useI18n()
const selectedId = ref('')
const memories = ref<UnifiedMemory[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
let requestId = 0

function metadataString(memory: UnifiedMemory, key: string, fallback: string) {
  const value = memory.metadata?.[key]
  return typeof value === 'string' && value ? value : fallback
}

function metadataIndex(memory: UnifiedMemory, fallback: number) {
  const value = Number(memory.metadata?.index)
  return Number.isFinite(value) ? value : fallback
}

const groups = computed<HermesGroup[]>(() => {
  const byProfile = new Map<string, HermesEntry[]>()
  for (const memory of memories.value) {
    const profile = metadataString(memory, 'profile', 'global')
    const entries = byProfile.get(profile) || []
    entries.push({
      file: metadataString(memory, 'file', 'MEMORY.md'),
      index: metadataIndex(memory, entries.length),
      memory,
    })
    byProfile.set(profile, entries)
  }

  return Array.from(byProfile, ([id, entries]) => ({
    id,
    label: id === 'global' ? t('en_global_with_icon') : `👤 ${id}`,
    entries,
  }))
})

const visibleGroups = computed(() => {
  const profile = props.profile.trim()
  return profile ? groups.value.filter(group => group.id === profile) : groups.value
})

const visibleEntries = computed(() => visibleGroups.value.flatMap(group => group.entries))
const visibleEntryCount = computed(() => visibleEntries.value.length)
const selectedMemory = computed(() => (
  visibleEntries.value.find(entry => entry.memory.id === selectedId.value)?.memory || null
))

watch(visibleEntries, entries => {
  if (!entries.some(entry => entry.memory.id === selectedId.value)) selectedId.value = ''
})

async function loadMemories() {
  const currentRequest = ++requestId
  loading.value = true
  error.value = null
  try {
    const response = await fetchUnifiedMemories({ source: 'hermes', limit: 500 })
    if (currentRequest === requestId) memories.value = response.memories
  } catch (cause: any) {
    if (currentRequest === requestId) {
      error.value = cause?.message || 'Failed to load Hermes memories'
    }
  } finally {
    if (currentRequest === requestId) loading.value = false
  }
}

function handleRefresh() {
  loadMemories()
}

onMounted(() => {
  window.addEventListener('app-refresh', handleRefresh)
  loadMemories()
})

onUnmounted(() => {
  requestId++
  window.removeEventListener('app-refresh', handleRefresh)
})
</script>

<style scoped>
.hermes-explorer,
.explorer-main {
  min-width: 0;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-header-gap);
}

.section-title {
  position: relative;
  margin: 0;
  padding-left: 12px;
  color: var(--primary);
  font-size: 1.5rem;
  font-weight: 600;
}

.section-title::before,
.profile-heading::before {
  position: absolute;
  left: 0;
  top: 50%;
  border-radius: 0 2px 2px 0;
  background: var(--accent);
  content: '';
  transform: translateY(-50%);
}

.section-title::before {
  width: 3px;
  height: 60%;
}

.entry-count {
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.explorer-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--space-5);
  align-items: start;
}

.explorer-shell--with-preview {
  grid-template-columns: minmax(0, 1fr) minmax(300px, 360px);
}

.profile-section {
  margin-bottom: 32px;
}

.profile-heading {
  position: relative;
  margin: 0 0 16px;
  padding-left: 10px;
  color: var(--primary);
  font-size: 1.05rem;
  font-weight: 600;
}

.profile-heading::before {
  width: 2px;
  height: 70%;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-card-gap);
}

.hermes-card {
  width: 100%;
  min-width: 0;
  padding: 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card);
  color: var(--primary);
  box-shadow: var(--shadow);
  cursor: pointer;
  font: inherit;
  text-align: left;
  transition: box-shadow 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              transform 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              border-color 0.2s ease;
}

.hermes-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
}

.hermes-card--selected,
.hermes-card:focus-visible {
  border-color: var(--accent);
  outline: 2px solid var(--accent);
  outline-offset: 3px;
}

.hermes-label {
  display: flex;
  align-items: center;
  width: fit-content;
  gap: 6px;
  margin-bottom: 10px;
  padding: 2px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--tag-bg);
  color: var(--text-secondary);
  font-size: 0.68rem;
  font-weight: 600;
}

.hermes-label__dot {
  width: 5px;
  height: 5px;
  flex: 0 0 5px;
  border-radius: 50%;
  background: var(--accent);
}

.hermes-index {
  color: var(--text-tertiary);
  font-family: var(--font-mono);
}

.hermes-card p {
  display: -webkit-box;
  margin: 0;
  overflow: hidden;
  color: var(--primary);
  font-size: 0.875rem;
  line-height: 1.6;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 5;
}

.error-state {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px;
  border: 1px solid var(--error-border);
  border-radius: var(--radius);
  background: var(--error-bg);
}

.error-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 4px;
  color: var(--error);
}

.error-copy span {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.error-state--inline {
  flex-wrap: wrap;
  margin-bottom: var(--space-4);
}

.error-state--inline .error-copy {
  flex: 1 1 18rem;
}

.action-btn {
  flex: 0 0 auto;
  padding: 7px 14px;
  border: 1px solid var(--border);
  border-radius: 7px;
  background: var(--card);
  color: var(--primary);
  cursor: pointer;
  font: inherit;
  font-size: 0.8rem;
}

.action-btn:hover,
.action-btn:focus-visible {
  border-color: var(--accent);
  outline: none;
}

.empty-state-wrap {
  display: flex;
  justify-content: center;
}

.skeleton-card {
  height: 120px;
  border-radius: var(--radius);
  background: linear-gradient(90deg, var(--tag-bg) 25%, var(--border) 50%, var(--tag-bg) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (max-width: 1024px) {
  .explorer-shell--with-preview {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 767px) {
  .section-header,
  .error-state {
    align-items: stretch;
    flex-direction: column;
  }

  .section-title {
    font-size: 1.2rem;
  }

  .card-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
