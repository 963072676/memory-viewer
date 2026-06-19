import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { fetchSessions, type MemorySession } from '@/api/sessions'
import type { AgentMemory } from '@/types'

const STORAGE_KEY = 'memory-viewer-active-session'

export const useSessionStore = defineStore('sessions', () => {
  const sessions = ref<MemorySession[]>([])
  const activeSessionId = ref(localStorage.getItem(STORAGE_KEY) || '')
  const activeProvider = ref('')
  const providers = ref<string[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const loaded = ref(false)

  const activeSession = computed(() => (
    sessions.value.find(session => session.id === activeSessionId.value) || null
  ))

  const sessionOptions = computed(() => {
    const seen = new Set<string>()
    return sessions.value.filter(session => {
      const key = `${session.provider}:${session.id}`
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
  })

  function setActiveSession(id: string) {
    activeSessionId.value = id
    if (id) {
      localStorage.setItem(STORAGE_KEY, id)
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  }

  function syncActiveSession() {
    if (!activeSessionId.value) return
    if (!sessionOptions.value.some(session => session.id === activeSessionId.value)) {
      setActiveSession('')
    }
  }

  function mergeDerivedSessions(memories: AgentMemory[]) {
    if (sessions.value.length > 0) return
    const derived: MemorySession[] = []
    const seen = new Set<string>()
    for (const memory of memories) {
      for (const sessionId of memory.sessionIds || []) {
        if (!sessionId || seen.has(sessionId)) continue
        seen.add(sessionId)
        derived.push({
          id: sessionId,
          provider: 'agentmemory',
          metadata: { source: 'agentmemory', derived: true },
        })
      }
    }
    sessions.value = derived
    providers.value = derived.length ? ['agentmemory'] : []
    syncActiveSession()
  }

  async function load(provider?: string) {
    loading.value = true
    error.value = null
    try {
      const response = await fetchSessions(provider)
      sessions.value = response.sessions
      providers.value = response.providers
      activeProvider.value = response.activeProvider
      loaded.value = true
      syncActiveSession()
    } catch (e: any) {
      error.value = e?.message || 'Failed to load sessions'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    sessions,
    activeSessionId,
    activeSession,
    activeProvider,
    providers,
    loading,
    error,
    loaded,
    sessionOptions,
    setActiveSession,
    mergeDerivedSessions,
    load,
  }
})
