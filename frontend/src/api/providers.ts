import { request } from '@/api/index'

export interface ProviderInfo {
  name: string
  type: string
  enabled: boolean
  active: boolean
  fallback: boolean
  capabilities: string[]
}

export interface ProviderStrategy {
  activeProvider: string
  fallbackProviders: string[]
  parallelQuery: boolean
  timeoutSeconds: number
  retryAttempts: number
  retryBackoffSeconds: number
  debugRawResponse: boolean
}

export interface ProviderHealthInfo {
  type: string
  active: boolean
  fallback: boolean
  healthy: boolean
  error: Record<string, unknown> | null
}

export interface ProvidersResponse {
  providers: ProviderInfo[]
  strategy: ProviderStrategy
  health: Record<string, ProviderHealthInfo>
}

export type ProviderStrategyUpdate = Partial<ProviderStrategy>

export function fetchProviders(): Promise<ProvidersResponse> {
  return request<ProvidersResponse>('/providers')
}

export function fetchProviderHealth(): Promise<{ health: Record<string, ProviderHealthInfo> }> {
  return request<{ health: Record<string, ProviderHealthInfo> }>('/providers/health')
}

export function updateProviderStrategy(update: ProviderStrategyUpdate): Promise<{ strategy: ProviderStrategy }> {
  return request<{ strategy: ProviderStrategy }>('/providers/strategy', {
    method: 'PATCH',
    body: JSON.stringify(update),
  })
}

export function switchProvider(activeProvider: string): Promise<{ strategy: ProviderStrategy }> {
  return request<{ strategy: ProviderStrategy }>('/providers/switch', {
    method: 'POST',
    body: JSON.stringify({ activeProvider }),
  })
}
