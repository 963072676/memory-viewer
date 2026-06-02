import { request } from './index'

export interface WebhookConfig {
  enabled: boolean
  webhook_url: string
  has_secret: boolean
  events: {
    create: boolean
    update: boolean
    delete: boolean
  }
}

export function fetchWebhookConfig(): Promise<WebhookConfig> {
  return request<WebhookConfig>('/webhook/config')
}

export function updateWebhookConfig(data: {
  enabled?: boolean
  webhook_url?: string
  secret?: string
  events?: { create?: boolean; update?: boolean; delete?: boolean }
}): Promise<WebhookConfig> {
  return request<WebhookConfig>('/webhook/config', {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}
