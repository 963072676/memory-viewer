import { request } from './index'

export interface MemoryLink {
  id: string
  source_id: string
  target_id: string
  relation_type: string
  label?: string
  created_at: string
}

export interface LinksResponse {
  links: MemoryLink[]
  total: number
}

export function getLinks(memoryId?: string): Promise<LinksResponse> {
  const params = memoryId ? `?memory_id=${memoryId}` : ''
  return request<LinksResponse>(`/links${params}`)
}

export function createLink(data: {
  source_id: string
  target_id: string
  relation_type: string
  label?: string
}): Promise<MemoryLink> {
  return request<MemoryLink>('/links', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function deleteLink(id: string): Promise<{ success: boolean }> {
  return request(`/links/${id}`, { method: 'DELETE' })
}

export function getLinkGraph(): Promise<{
  nodes: Array<{ id: string; label: string; type: string }>
  edges: Array<{ source: string; target: string; relation_type: string; label?: string }>
}> {
  return request('/links/graph')
}
