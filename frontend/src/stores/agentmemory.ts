import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AgentMemory, TagInfo, SmartCollection } from '@/types'
import {
  fetchAgentMemory,
  fetchAgentMemoryPaginated,
  fetchAllTags,
  fetchCollections,
  batchDeleteAgentMemory,
} from '@/api/agentmemory'

export const useAgentMemoryStore = defineStore('agentmemory', () => {
  const memories = ref<AgentMemory[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastFetch = ref<Date | null>(null)

  // F46: Tags state
  const allTags = ref<TagInfo[]>([])

  // F48: Smart Collections state
  const collections = ref<SmartCollection[]>([])

  // F45: Selection state for batch operations
  const selectedIds = ref<Set<string>>(new Set())
  const selectionCount = computed(() => selectedIds.value.size)
  const hasSelection = computed(() => selectedIds.value.size > 0)

  function toggleSelect(id: string) {
    if (selectedIds.value.has(id)) {
      selectedIds.value.delete(id)
    } else {
      selectedIds.value.add(id)
    }
    // Trigger reactivity for Set mutations
    selectedIds.value = new Set(selectedIds.value)
  }

  function clearSelection() {
    selectedIds.value = new Set()
  }

  function selectAll() {
    selectedIds.value = new Set(memories.value.map(m => m.id))
  }

  async function refresh(includeArchived = false) {
    loading.value = true
    error.value = null
    try {
      const response = await fetchAgentMemory(includeArchived)
      memories.value = response.memories || []
      lastFetch.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Failed to fetch memories'
      console.error('agentmemory.refresh error:', e)
    } finally {
      loading.value = false
    }
  }

  async function loadAllTags() {
    try {
      const response = await fetchAllTags()
      allTags.value = response.tags || []
    } catch (e: any) {
      console.error('agentmemory.loadAllTags error:', e)
    }
  }

  async function loadCollections() {
    try {
      const response = await fetchCollections()
      collections.value = response.collections || []
    } catch (e: any) {
      console.error('agentmemory.loadCollections error:', e)
    }
  }

  async function batchDelete(ids: string[]) {
    if (ids.length === 0) return
    try {
      await batchDeleteAgentMemory(ids)
      // Remove from local state
      memories.value = memories.value.filter(m => !ids.includes(m.id))
      clearSelection()
    } catch (e: any) {
      error.value = e?.message || 'Failed to delete memories'
      throw e
    }
  }

  // Alias used by some views (App.vue, TimelineView.vue) — equivalent to refresh().
  const fetchMemories = refresh

  return {
    memories,
    loading,
    error,
    lastFetch,
    allTags,
    collections,
    selectedIds,
    selectionCount,
    hasSelection,
    toggleSelect,
    clearSelection,
    selectAll,
    refresh,
    loadAllTags,
    loadCollections,
    batchDelete,
    fetchMemories,
  }
})
