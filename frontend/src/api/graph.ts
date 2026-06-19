import { request } from '@/api/index'

export interface MemoryGraphNode {
  id: string
  label: string
  type: string
  strength: number
  size: number
  provider: string
  sessionId?: string | null
  tags: string[]
  contentSnippet: string
}

export interface MemoryGraphEdge {
  source: string
  target: string
  weight: number
  shared_concepts: string[]
  relation_type: string
}

export interface MemoryGraphResponse {
  nodes: MemoryGraphNode[]
  edges: MemoryGraphEdge[]
  meta: {
    node_count: number
    edge_count: number
    max_weight: number
    providers: string[]
  }
}

export function fetchMemoryGraph(params: {
  provider?: string
  sessionId?: string
  limit?: number
} = {}): Promise<MemoryGraphResponse> {
  const qs = new URLSearchParams()
  if (params.provider) qs.set('provider', params.provider)
  if (params.sessionId) qs.set('sessionId', params.sessionId)
  if (params.limit) qs.set('limit', String(params.limit))
  const query = qs.toString()
  return request<MemoryGraphResponse>(`/graph${query ? `?${query}` : ''}`)
}
