import { request } from '@/api/index'

export interface MemoryMetadata {
  source: string
  timestamp: number
  agentId?: string
  sessionId?: string
  tags?: string[]
  raw?: unknown
}

export interface MemoryItem {
  id: string
  content: string
  metadata: MemoryMetadata
  embedding?: number[]
}

export interface MemoryCreateInput {
  content: string
  metadata?: Record<string, unknown>
  embedding?: number[]
  provider?: string
  title?: string
  type?: string
  concepts?: string[]
  strength?: number
  tags?: string[]
  agentId?: string
  sessionId?: string
}

export interface MemoryUpdateInput {
  content?: string
  metadata?: Record<string, unknown>
  provider?: string
  title?: string
  type?: string
  concepts?: string[]
  strength?: number
  tags?: string[]
  agentId?: string
  sessionId?: string
}

export interface MemoryListResponse {
  items: MemoryItem[]
  total: number
  limit: number
  offset: number
  provider: string
}

export function fetchMemories(params: {
  limit?: number
  offset?: number
  provider?: string
  includeRaw?: boolean
} = {}): Promise<MemoryListResponse> {
  const qs = new URLSearchParams()
  if (params.limit) qs.set('limit', String(params.limit))
  if (params.offset) qs.set('offset', String(params.offset))
  if (params.provider) qs.set('provider', params.provider)
  if (params.includeRaw !== undefined) qs.set('include_raw', String(params.includeRaw))
  const query = qs.toString()
  return request<MemoryListResponse>(`/memories${query ? '?' + query : ''}`)
}

export function createMemory(input: MemoryCreateInput): Promise<{ memory: MemoryItem }> {
  return request<{ memory: MemoryItem }>('/memories', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function fetchMemory(id: string, provider?: string): Promise<{ memory: MemoryItem }> {
  const qs = new URLSearchParams()
  if (provider) qs.set('provider', provider)
  const query = qs.toString()
  return request<{ memory: MemoryItem }>(`/memories/${encodeURIComponent(id)}${query ? '?' + query : ''}`)
}

export function updateMemory(id: string, input: MemoryUpdateInput): Promise<{ success: boolean; memory: MemoryItem }> {
  return request<{ success: boolean; memory: MemoryItem }>(`/memories/${encodeURIComponent(id)}`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}

export function deleteMemory(id: string, provider?: string): Promise<{ success: boolean; deleted_id: string }> {
  const qs = new URLSearchParams()
  if (provider) qs.set('provider', provider)
  const query = qs.toString()
  return request<{ success: boolean; deleted_id: string }>(
    `/memories/${encodeURIComponent(id)}${query ? '?' + query : ''}`,
    { method: 'DELETE' },
  )
}
