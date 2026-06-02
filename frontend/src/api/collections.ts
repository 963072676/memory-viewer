import { request } from './index'

export interface Collection {
  id: string
  name: string
  description: string
  icon: string
  color: string
  memory_count: number
  filters: CollectionFilters
  created_at: string
  updated_at: string
}

export interface CollectionFilters {
  type?: string
  tags?: string[]
  strength_min?: number
  strength_max?: number
  query?: string
}

export interface CollectionsResponse {
  collections: Collection[]
  total: number
}

export function getCollections(): Promise<CollectionsResponse> {
  return request<CollectionsResponse>('/collections')
}

export function getCollection(id: string): Promise<Collection> {
  return request<Collection>(`/collections/${id}`)
}

export function createCollection(data: {
  name: string
  description?: string
  icon?: string
  color?: string
  filters?: CollectionFilters
}): Promise<Collection> {
  return request<Collection>('/collections', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function updateCollection(id: string, data: {
  name?: string
  description?: string
  icon?: string
  color?: string
  filters?: CollectionFilters
}): Promise<Collection> {
  return request<Collection>(`/collections/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export function deleteCollection(id: string): Promise<{ success: boolean }> {
  return request(`/collections/${id}`, { method: 'DELETE' })
}

export function getCollectionMemories(id: string, params?: {
  limit?: number
  offset?: number
}): Promise<{ memories: any[]; total: number }> {
  const searchParams = new URLSearchParams()
  if (params?.limit) searchParams.set('limit', String(params.limit))
  if (params?.offset) searchParams.set('offset', String(params.offset))
  return request(`/collections/${id}/memories?${searchParams}`)
}
