import { request } from './index'

export interface HealthScanResult {
  overall_score: number
  total_memories: number
  scanned_at: string
  issues: HealthIssue[]
  breakdown: HealthScanBreakdown
}

export interface HealthIssue {
  id: string
  severity: 'critical' | 'warning' | 'info'
  category: string
  title: string
  description: string
  affected_count: number
  suggestion?: string
}

export interface HealthScanBreakdown {
  strength_avg: number
  stale_count: number
  duplicate_count: number
  missing_concepts_count: number
  missing_tags_count: number
  low_health_count: number
  orphan_count: number
}

export function runHealthScan(): Promise<HealthScanResult> {
  return request<HealthScanResult>('/health-scan', { method: 'POST' })
}

export function getLastScan(): Promise<HealthScanResult | null> {
  return request<HealthScanResult | null>('/health-scan/last')
}
