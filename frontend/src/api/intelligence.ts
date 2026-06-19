import { request } from '@/api/index'

export interface IntelligenceSummary {
  summary: string
  memoryCount: number
  providers: string[]
  sessionIds: string[]
  topTags: string[]
  keywords: string[]
}

export interface IntelligenceCompression {
  compressed: string
  originalCount: number
  compressedCount: number
  maxChars: number
  keywords: string[]
}

export interface IntelligenceCluster {
  id: string
  name: string
  count: number
  memoryIds: string[]
  providers: string[]
  keywords: string[]
}

export interface IntelligenceClusters {
  clusters: IntelligenceCluster[]
  total: number
  memoryCount: number
}

export interface IntelligenceContradiction {
  id: string
  memoryA: { id: string; content: string; provider: string }
  memoryB: { id: string; content: string; provider: string }
  sharedTerms: string[]
  severity: 'low' | 'medium' | 'high' | string
}

export interface IntelligenceContradictions {
  contradictions: IntelligenceContradiction[]
  total: number
}

function intelligenceParams(params: { provider?: string; sessionId?: string; limit?: number }) {
  const searchParams = new URLSearchParams()
  if (params.provider) searchParams.set('provider', params.provider)
  if (params.sessionId) searchParams.set('sessionId', params.sessionId)
  if (params.limit) searchParams.set('limit', String(params.limit))
  return searchParams.toString()
}

export function fetchIntelligenceSummary(params: {
  provider?: string
  sessionId?: string
  limit?: number
} = {}): Promise<IntelligenceSummary> {
  const query = intelligenceParams(params)
  return request<IntelligenceSummary>(`/intelligence/summary${query ? `?${query}` : ''}`)
}

export function compressIntelligenceMemories(params: {
  provider?: string
  sessionId?: string
  limit?: number
  maxChars?: number
} = {}): Promise<IntelligenceCompression> {
  return request<IntelligenceCompression>('/intelligence/compress', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

export function fetchIntelligenceClusters(params: {
  provider?: string
  sessionId?: string
  limit?: number
} = {}): Promise<IntelligenceClusters> {
  const query = intelligenceParams(params)
  return request<IntelligenceClusters>(`/intelligence/clusters${query ? `?${query}` : ''}`)
}

export function fetchIntelligenceContradictions(params: {
  provider?: string
  sessionId?: string
  limit?: number
} = {}): Promise<IntelligenceContradictions> {
  const query = intelligenceParams(params)
  return request<IntelligenceContradictions>(`/intelligence/contradictions${query ? `?${query}` : ''}`)
}
