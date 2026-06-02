import { request } from './index'

export interface FavoriteItem {
  memory_id: string
  title: string
  type: string
  added_at: string
}

export interface FavoritesResponse {
  favorites: FavoriteItem[]
  total: number
}

export function getFavorites(): Promise<FavoritesResponse> {
  return request<FavoritesResponse>('/favorites')
}

export function addFavorite(memoryId: string): Promise<{ success: boolean }> {
  return request(`/favorites/${memoryId}`, { method: 'POST' })
}

export function removeFavorite(memoryId: string): Promise<{ success: boolean }> {
  return request(`/favorites/${memoryId}`, { method: 'DELETE' })
}

export function checkFavorite(memoryId: string): Promise<{ favorited: boolean }> {
  return request<{ favorited: boolean }>(`/favorites/${memoryId}/check`)
}
