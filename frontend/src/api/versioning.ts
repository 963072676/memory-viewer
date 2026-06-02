import { request } from './index'

// Types for versioning API

export interface VersionInfo {
  version: number
  content: string
  title: string
  created_at: string
  session_id?: string
}

export interface VersionListResponse {
  memory_id: string
  current_version: number
  versions: VersionInfo[]
}

export interface VersionSingleResponse {
  memory_id: string
  version: VersionInfo
}

export interface RollbackResponse {
  success: boolean
  memory_id: string
  new_version: number
  rolled_back_to: number
}

export interface VersionDiffResponse {
  memory_id: string
  from_version: number
  to_version: number
  diff: {
    title_changed: boolean
    content_changed: boolean
    title_diff?: string
    content_diff?: string
  }
}

/**
 * Get all versions for a memory
 * GET /api/versioning/{memory_id}/versions
 */
export function getVersions(memoryId: string): Promise<VersionListResponse> {
  return request<VersionListResponse>(`/versioning/${memoryId}/versions`)
}

/**
 * Get a specific version of a memory
 * GET /api/versioning/{memory_id}/versions/{version}
 */
export function getVersion(memoryId: string, version: number): Promise<VersionSingleResponse> {
  return request<VersionSingleResponse>(`/versioning/${memoryId}/versions/${version}`)
}

/**
 * Rollback a memory to a specific version
 * POST /api/versioning/{memory_id}/versions/{version}/rollback
 */
export function rollbackVersion(memoryId: string, version: number): Promise<RollbackResponse> {
  return request<RollbackResponse>(`/versioning/${memoryId}/versions/${version}/rollback`, {
    method: 'POST',
  })
}

/**
 * Get diff between two versions
 * GET /api/versioning/{memory_id}/versions/diff?from={from}&to={to}
 */
export function getVersionDiff(
  memoryId: string,
  fromVersion: number,
  toVersion: number
): Promise<VersionDiffResponse> {
  return request<VersionDiffResponse>(
    `/versioning/${memoryId}/versions/diff?from=${fromVersion}&to=${toVersion}`
  )
}