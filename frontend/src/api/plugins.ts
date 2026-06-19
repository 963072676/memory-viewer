import { request } from '@/api/index'

export interface PluginCapability {
  name: string
  category: string
  description: string
  hooks: string[]
}

export interface PluginInfo {
  name: string
  version: string
  description: string
  hooks: string[]
  capabilities: PluginCapability[]
  permissions: string[]
  entryPoints: Record<string, string>
  author: string
  enabled: boolean
  loaded_at: string
  path: string
}

export interface PluginCapabilitySummary extends PluginCapability {
  plugins: string[]
}

export interface PluginManifestResponse {
  plugins: PluginInfo[]
  total: number
  capabilities: PluginCapabilitySummary[]
  supportedHooks: string[]
}

export interface PluginLogEntry {
  plugin: string
  hook: string
  success: boolean
  duration_ms: number
  error: string
  timestamp: string
}

export function fetchPlugins(): Promise<{ plugins: PluginInfo[]; total: number }> {
  return request<{ plugins: PluginInfo[]; total: number }>('/plugins')
}

export function fetchPluginManifest(): Promise<PluginManifestResponse> {
  return request<PluginManifestResponse>('/plugins/manifest')
}

export function fetchPluginLogs(limit = 50): Promise<{ logs: PluginLogEntry[] }> {
  return request<{ logs: PluginLogEntry[] }>(`/plugins/logs/recent?limit=${limit}`)
}

export function setPluginEnabled(name: string, enabled: boolean): Promise<{ success: boolean; name: string; enabled: boolean }> {
  const action = enabled ? 'enable' : 'disable'
  return request<{ success: boolean; name: string; enabled: boolean }>(`/plugins/${encodeURIComponent(name)}/${action}`, {
    method: 'POST',
  })
}
