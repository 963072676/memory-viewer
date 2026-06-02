import { useToast } from '@/composables/useToast'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    let errorMessage = `API Error ${response.status}`
    try {
      const body = await response.text()
      // Try to parse as JSON to extract meaningful error message
      try {
        const json = JSON.parse(body)
        errorMessage = json.detail || json.message || json.error || body
      } catch {
        // Not JSON, use raw text if available
        if (body) {
          errorMessage = body
        }
      }
    } catch {
      // Could not read body
    }

    // Show toast notification for 4xx/5xx errors
    try {
      const toast = useToast()
      toast.error(errorMessage)
    } catch {
      // Toast not available (e.g., outside Vue context)
    }

    throw new Error(errorMessage)
  }

  return response.json()
}

export { request, API_BASE }
