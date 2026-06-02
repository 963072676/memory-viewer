import { defineStore } from 'pinia'
import { ref } from 'vue'
import { searchMemories, type SearchResponse } from '@/api/search'
import { semanticSearch } from '@/api/p8'
import type { SemanticSearchResponse } from '@/types'

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
  const semanticResults = ref<SemanticSearchResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const filters = ref<SearchFilters>({})
  const searchMode = ref<SearchMode>('keyword')

  function setSearchMode(mode: SearchMode) {
    searchMode.value = mode
    // Clear results when switching modes
    results.value = null
    semanticResults.value = null
  }

  async function search(q: string, extraFilters?: SearchFilters) {
    const activeFilters = extraFilters || filters.value
    const hasQuery = q.trim().length > 0
    const hasFilters = Object.values(activeFilters).some(v => v !== undefined && v !== '')

    if (!hasQuery && !hasFilters) {
      results.value = null
      return
    }

    query.value = q
    loading.value = true
    error.value = null
    try {
      results.value = await searchMemories({
        q: q || '*',
        source: activeFilters.source,
        type: activeFilters.types,
        strengthMin: activeFilters.strengthMin,
        strengthMax: activeFilters.strengthMax,
        dateFrom: activeFilters.dateFrom,
        dateTo: activeFilters.dateTo,
        tag: activeFilters.tags,
      })
    } catch (e: any) {
      error.value = e.message || 'Search failed'
    } finally {
      loading.value = false
    }
  }

  function setFilters(f: SearchFilters) {
    filters.value = f
  }

  function clearFilters() {
    filters.value = {}
  }

  function clear() {
    query.value = ''
    results.value = null
    semanticResults.value = null
    filters.value = {}
  }

  async function doSemanticSearch(q: string) {
    if (!q.trim()) {
      semanticResults.value = null
      return
    }
    query.value = q
    loading.value = true
    error.value = null
    try {
      semanticResults.value = await semanticSearch(q, 20, 'semantic')
    } catch (e: any) {
      error.value = e.message || 'Semantic search failed'
    } finally {
      loading.value = false
    }
  }

  return {
    query, results, semanticResults, loading, error, filters, searchMode,
    search, doSemanticSearch, setSearchMode, setFilters, clearFilters, clear,
  }
})
