import { ref, computed } from 'vue'
import { semanticSearch } from '@/api/p8'
import type { SemanticSearchResult } from '@/types'

export function useSemanticSearch() {
  const results = ref<SemanticSearchResult[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const searchMode = ref<'semantic' | 'keyword'>('semantic')
  const lastQuery = ref('')

  async function search(query: string, limit: number = 20) {
    if (!query.trim()) {
      results.value = []
      return
    }

    loading.value = true
    error.value = null
    lastQuery.value = query

    try {
      const resp = await semanticSearch(query, limit, searchMode.value)
      results.value = resp.results
    } catch (e: any) {
      error.value = e.message || 'Search failed'
      results.value = []
    } finally {
      loading.value = false
    }
  }

  function toggleMode() {
    searchMode.value = searchMode.value === 'semantic' ? 'keyword' : 'semantic'
  }

  function clear() {
    results.value = []
    lastQuery.value = ''
    error.value = null
  }

  return {
    results,
    loading,
    error,
    searchMode,
    lastQuery,
    search,
    toggleMode,
    clear,
  }
}
