import { ref, computed } from 'vue'
import { fetchChangelog, type ChangelogEntry } from '@/api/changelog'

const STORAGE_KEY = 'memory-viewer-last-read-version'
const changelog = ref<ChangelogEntry[]>([])
const loaded = ref(false)
const showModal = ref(false)

export function useChangelog() {
  async function loadChangelog() {
    if (loaded.value) return
    try {
      const data = await fetchChangelog()
      changelog.value = data.changelog
      loaded.value = true
      checkAutoShow()
    } catch (e) {
      console.error('Failed to load changelog:', e)
    }
  }

  function checkAutoShow() {
    if (changelog.value.length === 0) return
    const latestVersion = changelog.value[0].version
    const lastRead = localStorage.getItem(STORAGE_KEY)
    if (!lastRead || lastRead !== latestVersion) {
      showModal.value = true
    }
  }

  function markAsRead() {
    if (changelog.value.length > 0) {
      localStorage.setItem(STORAGE_KEY, changelog.value[0].version)
    }
    showModal.value = false
  }

  function openModal() {
    showModal.value = true
  }

  function closeModal() {
    showModal.value = false
  }

  const currentVersion = computed(() =>
    changelog.value.length > 0 ? changelog.value[0].version : ''
  )

  const hasUpdate = computed(() => {
    const lastRead = localStorage.getItem(STORAGE_KEY)
    return !lastRead || lastRead !== currentVersion.value
  })

  return {
    changelog,
    loaded,
    showModal,
    currentVersion,
    hasUpdate,
    loadChangelog,
    checkAutoShow,
    markAsRead,
    openModal,
    closeModal,
  }
}
