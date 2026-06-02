import { request } from './index'

export function fetchProfiles(): Promise<string[]> {
  return request<string[]>('/profiles')
}
