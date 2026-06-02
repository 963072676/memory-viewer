import { request } from './index'

export interface MemoryItem {
  id: string
  title: string
  content: string
  type: string
  concepts: string[]
  strength: number
}

export interface CompareResult {
  left_only: MemoryItem[]
  right_only: MemoryItem[]
  common: MemoryItem[]
  similarity_score: number
}

export async function fetchProfiles(): Promise<string[]> {
  return request<string[]>('/profiles')
}

export async function compareProfiles(left: string, right: string): Promise<CompareResult> {
  return request<CompareResult>(`/compare/profiles?left=${encodeURIComponent(left)}&right=${encodeURIComponent(right)}`)
}