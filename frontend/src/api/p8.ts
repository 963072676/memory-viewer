import { request } from './index'
import type {
  SemanticSearchResponse,
  SuggestTagsResponse,
  SummarizeResponse,
  BulkAutoTagResponse,
} from '@/types'

// F-33: Semantic search
export function semanticSearch(q: string, limit: number = 10, mode: 'semantic' | 'keyword' = 'semantic'): Promise<SemanticSearchResponse> {
  const params = new URLSearchParams()
  params.set('q', q)
  params.set('limit', String(limit))
  params.set('mode', mode)
  return request<SemanticSearchResponse>(`/search/semantic?${params}`)
}

// F-34: Suggest tags for a memory
export function suggestTags(memoryId: string): Promise<SuggestTagsResponse> {
  return request<SuggestTagsResponse>(`/memories/${memoryId}/suggest-tags`, {
    method: 'POST',
  })
}

// F-34: Summarize a memory
export function summarizeMemory(memoryId: string): Promise<SummarizeResponse> {
  return request<SummarizeResponse>(`/memories/${memoryId}/summarize`, {
    method: 'POST',
  })
}

// F-34: Bulk auto-tag
export function bulkAutoTag(ids?: string[], maxTags: number = 5): Promise<BulkAutoTagResponse> {
  return request<BulkAutoTagResponse>('/memories/bulk-auto-tag', {
    method: 'POST',
    body: JSON.stringify({ ids: ids || null, max_tags: maxTags }),
  })
}
