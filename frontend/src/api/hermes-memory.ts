import { request } from './index'

export interface HermesProfileData {
  memory: string[]
  user: string[]
}

export interface HermesMemoryResponse {
  global: HermesProfileData
  profiles: Record<string, HermesProfileData>
}

export function fetchHermesMemory(): Promise<HermesMemoryResponse> {
  return request<HermesMemoryResponse>('/hermes-memory')
}
