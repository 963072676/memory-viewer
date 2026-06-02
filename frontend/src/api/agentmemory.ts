import { request } from './index'
import type {
  AgentMemoryResponse,
  AgentMemoryPaginatedResponse,
  DecayResponse,
  HealthResponse,
  RecommendationsResponse,
  DuplicatesResponse,
  MergeResponse,
  GraphResponse,
  TagsResponse,
  CollectionsResponse,
  TemplatesResponse,
} from '@/types'

export function fetchAgentMemory(includeArchived?: boolean): Promise<AgentMemoryResponse> {
  if (includeArchived) {
    return request<AgentMemoryResponse>('/agentmemory/paginated?limit=500&include_archived=true')
  }
  return request<AgentMemoryResponse>('/agentmemory')
}

export function fetchAgentMemoryPaginated(params: {
  limit?: number
  offset?: number
  sort?: string
  order?: string
  type?: string
  tag?: string
}): Promise<AgentMemoryPaginatedResponse> {
  const searchParams = new URLSearchParams()
  if (params.limit) searchParams.set('limit', String(params.limit))
  if (params.offset) searchParams.set('offset', String(params.offset))
  if (params.sort) searchParams.set('sort', params.sort)
  if (params.order) searchParams.set('order', params.order)
  if (params.type) searchParams.set('type', params.type)
  if (params.tag) searchParams.set('tag', params.tag)
  return request<AgentMemoryPaginatedResponse>(`/agentmemory/paginated?${searchParams}`)
}

export function createAgentMemory(data: {
  title: string
  content: string
  type?: string
  concepts?: string[]
  strength?: number
  tags?: string[]
}): Promise<any> {
  return request('/agentmemory', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

// F-08: Update memory
export function updateAgentMemory(id: string, data: {
  content?: string
  concepts?: string[]
  strength?: number
}): Promise<any> {
  return request(`/agentmemory/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

// F-09: Delete single memory
export function deleteAgentMemory(id: string): Promise<any> {
  return request(`/agentmemory/${id}`, {
    method: 'DELETE',
  })
}

// F-09: Batch delete memories
export function batchDeleteAgentMemory(ids: string[]): Promise<any> {
  return request('/agentmemory/batch/delete', {
    method: 'POST',
    body: JSON.stringify({ ids }),
  })
}

// F45: Unified batch action
export function batchAction(action: string, ids: string[], params?: Record<string, any>): Promise<any> {
  return request('/agentmemory/batch', {
    method: 'POST',
    body: JSON.stringify({ action, ids, params }),
  })
}

export async function importAgentMemory(file: File): Promise<any> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${import.meta.env.VITE_API_BASE || '/api'}/agentmemory/import`, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) {
    throw new Error(`Import failed: ${response.status}`)
  }
  return response.json()
}

export function exportAgentMemory(format: string = 'json', ids?: string): string {
  const params = new URLSearchParams()
  params.set('format', format)
  if (ids) params.set('ids', ids)
  return `${import.meta.env.VITE_API_BASE || '/api'}/agentmemory/export?${params}`
}

// F-15: Archive / Unarchive memory
export function archiveMemory(id: string): Promise<any> {
  return request(`/agentmemory/${id}/archive`, { method: 'PATCH' })
}

export function unarchiveMemory(id: string): Promise<any> {
  return request(`/agentmemory/${id}/unarchive`, { method: 'PATCH' })
}

// F-22: Decay
export function getDecay(id: string): Promise<DecayResponse> {
  return request<DecayResponse>(`/agentmemory/${id}/decay`)
}

// F-20: Health
export function getHealth(id: string): Promise<HealthResponse> {
  return request<HealthResponse>(`/agentmemory/${id}/health`)
}

// F-19: Recommendations
export function getRecommendations(id: string, limit: number = 5): Promise<RecommendationsResponse> {
  return request<RecommendationsResponse>(`/agentmemory/${id}/recommendations?limit=${limit}`)
}

// F-21: Duplicates
export function getDuplicates(threshold: number = 0.7): Promise<DuplicatesResponse> {
  return request<DuplicatesResponse>(`/agentmemory/duplicates?threshold=${threshold}`)
}

// F-21: Merge
export function mergeMemories(keepId: string, mergeId: string): Promise<MergeResponse> {
  return request<MergeResponse>('/agentmemory/merge', {
    method: 'POST',
    body: JSON.stringify({ keep_id: keepId, merge_id: mergeId }),
  })
}

// F-18: Graph
export function getGraph(): Promise<GraphResponse> {
  return request<GraphResponse>('/agentmemory/graph')
}

// F46: Set memory tags
export function setMemoryTags(id: string, tags: string[]): Promise<any> {
  return request(`/agentmemory/${id}/tags`, {
    method: 'PUT',
    body: JSON.stringify({ tags }),
  })
}

// F46: Fetch all tags
export function fetchAllTags(): Promise<TagsResponse> {
  return request<TagsResponse>('/tags')
}

// F48: Fetch smart collections
export function fetchCollections(): Promise<CollectionsResponse> {
  return request<CollectionsResponse>('/agentmemory/collections')
}

// F49: Fetch memory templates
export function fetchTemplates(): Promise<TemplatesResponse> {
  return request<TemplatesResponse>('/agentmemory/templates')
}

// P21-T2: Fetch single memory by ID
export function fetchAgentMemoryById(id: string): Promise<AgentMemoryResponse> {
  return request<AgentMemoryResponse>(`/agentmemory/${id}`)
}
