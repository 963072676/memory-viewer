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

export interface ProviderOperationStats {
  calls: number
  successes: number
  errors: number
  totalLatencyMs: number
  maxLatencyMs: number
  avgLatencyMs: number
  errorRate: number
}

export interface ProviderStats extends ProviderOperationStats {
  type: string
  retryEvents: number
  fallbackSuccesses: number
  lastSuccessAt: number | null
  lastFailureAt: number | null
  lastError: Record<string, unknown> | null
  operations: Record<string, ProviderOperationStats>
}

export interface ProviderCallEvent {
  timestamp: number
  provider: string
  type: string
  operation: string
  success: boolean
  latencyMs: number
  attempt: number
  error: Record<string, unknown> | null
}

export interface ProviderRouteEvent {
  timestamp: number
  operation: string
  strategy: 'direct' | 'fallback' | 'parallel' | string
  providers: string[]
  successfulProvider: string
  successfulProviders: string[]
  fallbackUsed: boolean
  latencyMs: number
  errors: Array<Record<string, unknown>>
}

export interface ProviderRoutingStats {
  direct: number
  fallback: number
  parallel: number
  fallbackUsed: number
  routeErrors: number
  recentRoutes: ProviderRouteEvent[]
}

export interface ProviderObservability {
  strategy: ProviderStrategy
  providers: Record<string, ProviderStats>
  routing: ProviderRoutingStats
  recentCalls: ProviderCallEvent[]
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

export function fetchProviderObservability(limit = 50): Promise<{ observability: ProviderObservability }> {
  return request<{ observability: ProviderObservability }>(`/providers/observability?limit=${limit}`)
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
