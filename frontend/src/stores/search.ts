import { defineStore } from 'pinia'
import { ref } from 'vue'
import { searchMemories, type SearchResponse } from '@/api/search'

export type SearchMode = 'keyword' | 'semantic'

export interface SearchFilters {
  types?: string
  strengthMin?: number
  strengthMax?: number
  dateFrom?: string
  dateTo?: string
  source?: string
  tags?: string
}

export const useSearchStore = defineStore('search', () => {
  const query = ref('')
  const results = ref<SearchResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const filters = ref<SearchFilters>({})
  const searchMode = ref<SearchMode>('keyword')
  let searchRequestId = 0

  function setSearchMode(mode: SearchMode) {
    searchRequestId++
    searchMode.value = mode
    results.value = null
    error.value = null
    loading.value = false
  }

  async function runSearch(q: string, mode: SearchMode, extraFilters?: SearchFilters) {
    const activeFilters = extraFilters || filters.value
    const hasQuery = q.trim().length > 0
    const hasFilters = Object.values(activeFilters).some(v => v !== undefined && v !== '')

    if (!hasQuery && !hasFilters) {
      searchRequestId++
      results.value = null
      error.value = null
      loading.value = false
      return
    }

    const requestId = ++searchRequestId
    query.value = q
    loading.value = true
    error.value = null
    try {
      const response = await searchMemories({
        q: q || '*',
        mode,
        source: activeFilters.source,
        type: activeFilters.types,
        strengthMin: activeFilters.strengthMin,
        strengthMax: activeFilters.strengthMax,
        dateFrom: activeFilters.dateFrom,
        dateTo: activeFilters.dateTo,
        tag: activeFilters.tags,
      })
      if (requestId === searchRequestId) results.value = response
    } catch (e: any) {
      if (requestId === searchRequestId) {
        results.value = null
        error.value = e.message || 'Search failed'
      }
    } finally {
      if (requestId === searchRequestId) loading.value = false
    }
  }

  function search(q: string, extraFilters?: SearchFilters) {
    return runSearch(q, 'keyword', extraFilters)
  }

  function setFilters(f: SearchFilters) {
    filters.value = f
  }

  function clearFilters() {
    filters.value = {}
  }

  function clear() {
    searchRequestId++
    query.value = ''
    results.value = null
    filters.value = {}
    error.value = null
    loading.value = false
  }

  function doSemanticSearch(q: string) {
    return runSearch(q, 'semantic')
  }

  return {
    query, results, loading, error, filters, searchMode,
    search, doSemanticSearch, setSearchMode, setFilters, clearFilters, clear,
  }
})
