<template>
  <div class="session-switcher">
    <div class="session-control">
      <label for="active-session">Session</label>
      <select
        id="active-session"
        :value="sessionStore.activeSessionId"
        class="session-select"
        :disabled="sessionStore.loading"
        @change="onSessionChange"
      >
        <option value="">All sessions</option>
        <option
          v-for="session in sessionStore.sessionOptions"
          :key="`${session.provider}-${session.id}`"
          :value="session.id"
        >
          {{ session.id }}{{ session.provider ? ` / ${session.provider}` : '' }}
        </option>
      </select>
    </div>

    <div class="session-meta">
      <span>{{ sessionStore.sessionOptions.length }} sessions</span>
      <span>{{ activeLabel }}</span>
    </div>

    <button
      class="action-btn action-btn--sm"
      type="button"
      :disabled="sessionStore.loading"
      aria-label="Refresh sessions"
      title="Refresh sessions"
      @click="refreshSessions"
    >
      Refresh
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useSessionStore } from '@/stores/sessions'
import { useAgentMemoryStore } from '@/stores/agentmemory'

const sessionStore = useSessionStore()
const agentMemoryStore = useAgentMemoryStore()

const activeLabel = computed(() => (
  sessionStore.activeSessionId ? `Active ${sessionStore.activeSessionId}` : 'All memory'
))

function onSessionChange(event: Event) {
  const target = event.target as HTMLSelectElement
  sessionStore.setActiveSession(target.value)
}

async function refreshSessions() {
  try {
    await sessionStore.load()
  } catch {
    sessionStore.mergeDerivedSessions(agentMemoryStore.memories)
  }
}

watch(
  () => agentMemoryStore.memories,
  memories => {
    sessionStore.mergeDerivedSessions(memories)
  },
  { deep: true },
)

onMounted(refreshSessions)
</script>

<style scoped>
.session-switcher {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
  margin: 0 0 var(--space-4);
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--card);
}

.session-control {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: min(100%, 360px);
}

.session-control label {
  color: var(--text-secondary);
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
}

.session-select {
  min-width: 220px;
  min-height: 34px;
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--bg);
  color: var(--primary);
  font-family: var(--font);
  font-size: 0.85rem;
}

.session-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex: 1;
  color: var(--text-secondary);
  font-size: 0.78rem;
}

.session-meta span {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--tag-bg);
}

@media (max-width: 640px) {
  .session-control,
  .session-select,
  .session-switcher .action-btn {
    width: 100%;
  }

  .session-control {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
