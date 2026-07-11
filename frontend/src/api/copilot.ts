import { request } from '@/api/index'

export type CopilotAction =
  | 'summarize_session'
  | 'compress_memory'
  | 'detect_contradictions'
  | 'optimize_memory_structure'

export interface CopilotRecommendation {
  priority: 'low' | 'medium' | 'high' | string
  kind: string
  title: string
  detail: string
  params?: Record<string, number | string>
}

export interface CopilotRunRequest {
  action: CopilotAction
  provider?: string
  sessionId?: string
  limit?: number
  maxChars?: number
}

export interface CopilotRunResponse {
  action: CopilotAction
  title: string
  status: 'ready' | 'attention' | 'empty' | string
  message: string
  provider: string
  sessionId: string
  memoryCount: number
  providers: string[]
  sessionIds: string[]
  generatedAt: number
  result: Record<string, any>
  recommendations: CopilotRecommendation[]
}

export function runCopilotAction(input: CopilotRunRequest): Promise<CopilotRunResponse> {
  return request<CopilotRunResponse>('/copilot/run', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}
