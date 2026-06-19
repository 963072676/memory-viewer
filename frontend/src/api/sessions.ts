import { request } from '@/api/index'

export interface MemorySession {
  id: string
  agentId?: string | null
  provider: string
  metadata: Record<string, unknown>
}

export interface SessionsResponse {
  sessions: MemorySession[]
  total: number
  providers: string[]
  activeProvider: string
}

export function fetchSessions(provider?: string): Promise<SessionsResponse> {
  const qs = new URLSearchParams()
  if (provider) qs.set('provider', provider)
  const query = qs.toString()
  return request<SessionsResponse>(`/sessions${query ? `?${query}` : ''}`)
}
