import { request } from './index'

export interface ChangelogEntry {
  version: string
  date: string
  title: string
  changes: {
    title: string
    description: string
    type: 'feature' | 'fix' | 'improvement'
  }[]
}

export interface ChangelogResponse {
  changelog: ChangelogEntry[]
}

export function fetchChangelog(): Promise<ChangelogResponse> {
  return request<ChangelogResponse>('/changelog')
}
