import { ref, onMounted, onUnmounted } from 'vue'

export type ConnectionState = 'connecting' | 'connected' | 'disconnected' | 'error'

export interface WebSocketOptions {
  url?: string
  workspaceId?: string
  userId?: string
  reconnectInterval?: number
  maxReconnects?: number
}

export function useWebSocket(options: WebSocketOptions = {}) {
  const {
    url = `ws://${window.location.host}/api/ws/memories`,
    workspaceId = 'default',
    userId = 'anonymous',
    reconnectInterval = 3000,
    maxReconnects = 10,
  } = options

  const state = ref<ConnectionState>('disconnected')
  const lastMessage = ref<any>(null)
  const reconnectCount = ref(0)

  let ws: WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let heartbeatTimer: ReturnType<typeof setInterval> | null = null

  const listeners: Map<string, Set<(data: any) => void>> = new Map()

  function connect() {
    if (ws?.readyState === WebSocket.OPEN) return

    state.value = 'connecting'
    const wsUrl = `${url}?workspace_id=${workspaceId}&user_id=${userId}`

    try {
      ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        state.value = 'connected'
        reconnectCount.value = 0
        // Start heartbeat
        heartbeatTimer = setInterval(() => {
          if (ws?.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }))
          }
        }, 30000)
      }

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          lastMessage.value = msg
          const eventName = msg.event || msg.type
          if (eventName && listeners.has(eventName)) {
            for (const cb of listeners.get(eventName)!) {
              cb(msg.data || msg)
            }
          }
        } catch {}
      }

      ws.onclose = () => {
        state.value = 'disconnected'
        cleanup()
        attemptReconnect()
      }

      ws.onerror = () => {
        state.value = 'error'
      }
    } catch {
      state.value = 'error'
      attemptReconnect()
    }
  }

  function disconnect() {
    cleanup()
    if (ws) {
      ws.close()
      ws = null
    }
    state.value = 'disconnected'
  }

  function cleanup() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
  }

  function attemptReconnect() {
    if (reconnectCount.value >= maxReconnects) return
    reconnectCount.value++
    reconnectTimer = setTimeout(() => {
      connect()
    }, reconnectInterval)
  }

  function on(event: string, callback: (data: any) => void) {
    if (!listeners.has(event)) {
      listeners.set(event, new Set())
    }
    listeners.get(event)!.add(callback)
    return () => {
      listeners.get(event)?.delete(callback)
    }
  }

  function send(data: any) {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data))
    }
  }

  onMounted(() => connect())
  onUnmounted(() => disconnect())

  return {
    state,
    lastMessage,
    reconnectCount,
    connect,
    disconnect,
    on,
    send,
  }
}
