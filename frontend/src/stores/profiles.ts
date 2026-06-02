import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useProfilesStore = defineStore('profiles', () => {
  const profiles = ref<string[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchProfiles() {
    loading.value = true
    error.value = null
    try {
      const { fetchProfiles: fetch } = await import('@/api/profiles')
      profiles.value = await fetch()
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch profiles'
    } finally {
      loading.value = false
    }
  }

  return { profiles, loading, error, fetchProfiles }
})
