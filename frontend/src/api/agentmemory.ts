import { request } from './index'
import {
  createMemory,
  deleteMemory,
  fetchMemories as fetchUnifiedMemories,
  fetchMemory,
  updateMemory,
  type MemoryItem,
} from './memories'
import type {
  AgentMemory,
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

const AGENTMEMORY_PROVIDER = 'agentmemory'
const DEFAULT_MEMORY_TYPE: AgentMemory['type'] = 'fact'

function memoryType(value: unknown): AgentMemory['type'] {
  const allowed: AgentMemory['type'][] = ['pattern', 'fact', 'preference', 'bug', 'workflow', 'architecture']
  return allowed.includes(value as AgentMemory['type']) ? value as AgentMemory['type'] : DEFAULT_MEMORY_TYPE
}

function healthColor(value: unknown): AgentMemory['health_color'] {
  return value === 'green' || value === 'yellow' || value === 'red' ? value : undefined
}

function rawMemory(item: MemoryItem): Record<string, any> {
  return (item.metadata.raw && typeof item.metadata.raw === 'object')
    ? item.metadata.raw as Record<string, any>
    : {}
}

function toAgentMemory(item: MemoryItem): AgentMemory {
  const raw = rawMemory(item)
  const metadata = item.metadata || {}
  return {
    id: item.id,
    type: memoryType(raw.type),
    title: raw.title || item.content.slice(0, 80) || item.id,
    content: item.content,
    concepts: Array.isArray(raw.concepts) ? raw.concepts : [],
    files: Array.isArray(raw.files) ? raw.files : [],
    createdAt: raw.createdAt || raw.created_at || new Date(metadata.timestamp || Date.now()).toISOString(),
    updatedAt: raw.updatedAt || raw.updated_at || new Date(metadata.timestamp || Date.now()).toISOString(),
    strength: Number(raw.strength ?? 5),
    version: Number(raw.version ?? 1),
    isLatest: raw.isLatest ?? true,
    sessionIds: Array.isArray(raw.sessionIds)
      ? raw.sessionIds
      : (metadata.sessionId ? [metadata.sessionId] : []),
    archived: Boolean(raw.archived ?? false),
    health_score: raw.health_score,
    health_color: healthColor(raw.health_color),
    tags: Array.isArray(metadata.tags)
      ? metadata.tags
      : (Array.isArray(raw.tags) ? raw.tags : []),
  }
}

function toAgentMemoryResponse(item: MemoryItem): AgentMemoryResponse {
  return { memories: [toAgentMemory(item)] }
}

export function fetchAgentMemory(includeArchived?: boolean): Promise<AgentMemoryResponse> {
  if (includeArchived) {
    return request<AgentMemoryResponse>('/agentmemory/paginated?limit=500&include_archived=true')
  }
  return fetchUnifiedMemories({
    provider: AGENTMEMORY_PROVIDER,
    limit: 500,
    includeRaw: true,
  }).then(response => ({ memories: response.items.map(toAgentMemory) }))
}

export function fetchAgentMemoryPaginated(params: {
  limit?: number
  offset?: number
  sort?: string
  order?: string
  type?: string
  tag?: string
}): Promise<AgentMemoryPaginatedResponse> {
  return fetchUnifiedMemories({
    provider: AGENTMEMORY_PROVIDER,
    limit: 500,
    includeRaw: true,
  }).then(response => {
    let memories = response.items.map(toAgentMemory)
    if (params.type) {
      memories = memories.filter(memory => memory.type === params.type)
    }
    if (params.tag) {
      const tag = params.tag.toLowerCase()
      memories = memories.filter(memory => (memory.tags || []).some(t => t.toLowerCase() === tag))
    }

    const sort = params.sort || 'updatedAt'
    const order = params.order === 'asc' ? 1 : -1
    memories.sort((a, b) => {
      if (sort === 'strength') return (a.strength - b.strength) * order
      if (sort === 'type') return a.type.localeCompare(b.type) * order
      return (new Date(a[sort as 'updatedAt' | 'createdAt']).getTime() - new Date(b[sort as 'updatedAt' | 'createdAt']).getTime()) * order
    })

    const offset = params.offset || 0
    const limit = params.limit || 50
    return {
      total: memories.length,
      limit,
      offset,
      memories: memories.slice(offset, offset + limit),
    }
  })
}

export function createAgentMemory(data: {
  title: string
  content: string
  type?: string
  concepts?: string[]
  strength?: number
  tags?: string[]
}): Promise<any> {
  return createMemory({
    provider: AGENTMEMORY_PROVIDER,
    content: data.content,
    title: data.title,
    type: data.type,
    concepts: data.concepts,
    strength: data.strength,
    tags: data.tags,
  }).then(response => ({ success: true, memory: toAgentMemory(response.memory) }))
}

// F-08: Update memory
export function updateAgentMemory(id: string, data: {
  content?: string
  concepts?: string[]
  strength?: number
}): Promise<any> {
  return updateMemory(id, {
    provider: AGENTMEMORY_PROVIDER,
    content: data.content,
    concepts: data.concepts,
    strength: data.strength,
  }).then(response => ({ success: response.success, memory: toAgentMemory(response.memory) }))
}

// F-09: Delete single memory
export function deleteAgentMemory(id: string): Promise<any> {
  return deleteMemory(id, AGENTMEMORY_PROVIDER)
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
  return request<GraphResponse>('/graph')
}

// F46: Set memory tags
export function setMemoryTags(id: string, tags: string[]): Promise<any> {
  return updateMemory(id, {
    provider: AGENTMEMORY_PROVIDER,
    tags,
  }).then(response => ({ success: response.success, memory: toAgentMemory(response.memory) }))
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
  return fetchMemory(id, AGENTMEMORY_PROVIDER).then(response => toAgentMemoryResponse(response.memory))
}
