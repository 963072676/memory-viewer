import { request } from './index'
import type { QuickSearchResponse } from '@/types'

export interface SearchResult {
  source: string
  id: string
  type?: string
  title?: string
  content: string
  concepts?: string[]
  strength?: number
  updatedAt?: string
  profile?: string
  file?: string
  index?: number
  matchField: string
  matchSnippet: string
}

export interface SearchResponse {
  query: string
  mode: 'keyword' | 'semantic' | 'hybrid'
  total: number
  limit: number
  offset: number
  results: SearchResult[]
}

export function searchMemories(params: {
  q: string
  mode?: 'keyword' | 'semantic' | 'hybrid'
  source?: string
  type?: string
  profile?: string
  strengthMin?: number
  strengthMax?: number
  dateFrom?: string
  dateTo?: string
  limit?: number
  offset?: number
  tag?: string
}): Promise<SearchResponse> {
  const searchParams = new URLSearchParams()
  searchParams.set('q', params.q)
  if (params.mode) searchParams.set('mode', params.mode)
  if (params.source) searchParams.set('source', params.source)
  if (params.type) searchParams.set('type', params.type)
  if (params.profile) searchParams.set('profile', params.profile)
  if (params.strengthMin !== undefined) searchParams.set('strength_min', String(params.strengthMin))
  if (params.strengthMax !== undefined) searchParams.set('strength_max', String(params.strengthMax))
  if (params.dateFrom) searchParams.set('date_from', params.dateFrom)
  if (params.dateTo) searchParams.set('date_to', params.dateTo)
  if (params.limit) searchParams.set('limit', String(params.limit))
  if (params.offset) searchParams.set('offset', String(params.offset))
  if (params.tag) searchParams.set('tag', params.tag)
  return request<SearchResponse>(`/search?${searchParams}`)
}

// F47: Quick search for command palette
export function quickSearch(q: string, limit: number = 10): Promise<QuickSearchResponse> {
  const searchParams = new URLSearchParams()
  searchParams.set('q', q)
  searchParams.set('limit', String(limit))
  return request<QuickSearchResponse>(`/search/quick?${searchParams}`)
}
