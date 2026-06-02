import { request } from './index'

export interface HealthResponse {
  status: string
  version: string
  uptime_seconds: number
  cache_age_seconds: number
  agentmemory_count: number
  hermes_memory_count: number
}

export function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health')
}
