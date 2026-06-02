import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchHermesMemory, type HermesMemoryResponse, type HermesProfileData } from '@/api/hermes-memory'

export const useHermesMemoryStore = defineStore('hermes-memory', () => {
  const globalData = ref<HermesProfileData>({ memory: [], user: [] })
  const profiles = ref<Record<string, HermesProfileData>>({})
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastFetch = ref<Date | null>(null)

  const profileNames = computed(() => Object.keys(profiles.value))

  const totalEntries = computed(() => {
    let count = globalData.value.memory.length + globalData.value.user.length
    for (const p of Object.values(profiles.value)) {
      count += p.memory.length + p.user.length
    }
    return count
  })

  async function fetchMemory() {
    loading.value = true
    error.value = null
    try {
      const data = await fetchHermesMemory()
      globalData.value = data.global
      profiles.value = data.profiles
      lastFetch.value = new Date()
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch hermes memory'
    } finally {
      loading.value = false
    }
  }

  async function refresh() {
    await fetchMemory()
  }

  return {
    globalData,
    profiles,
    loading,
    error,
    lastFetch,
    profileNames,
    totalEntries,
    fetchMemory,
    refresh,
  }
})
