import { request } from '@/api/index'

export interface SourceInfo {
  name: string
  type: string
  enabled: boolean
  healthy: boolean
  count: number
}

export interface SourcesResponse {
  sources: SourceInfo[]
}

export interface UnifiedMemory {
  id: string
  title: string
  content: string
  type: string
  concepts: string[]
  strength: number
  createdAt: string
  updatedAt: string
  source: string
  metadata: Record<string, unknown>
}

export interface UnifiedMemoriesResponse {
  memories: UnifiedMemory[]
  total: number
  offset: number
  limit: number
}

export async function fetchSources(): Promise<SourcesResponse> {
  return request<SourcesResponse>('/sources')
}

export async function fetchUnifiedMemories(params: {
  limit?: number
  offset?: number
  source?: string
} = {}): Promise<UnifiedMemoriesResponse> {
  const qs = new URLSearchParams()
  if (params.limit) qs.set('limit', String(params.limit))
  if (params.offset) qs.set('offset', String(params.offset))
  if (params.source) qs.set('source', params.source)
  const query = qs.toString()
  return request<UnifiedMemoriesResponse>(`/memories/unified${query ? '?' + query : ''}`)
}
