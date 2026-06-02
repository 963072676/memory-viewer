<template>
  <div class="api-playground">
    <div class="playground-header">
      <h1>🔗 API Playground</h1>
      <p class="subtitle">Interactive API explorer — test endpoints directly from the browser</p>
    </div>

    <div class="playground-layout">
      <!-- Endpoint List -->
      <div class="endpoint-list">
        <div class="endpoint-search">
          <input v-model="searchQuery" placeholder="Search endpoints..." class="search-input" />
        </div>
        <div class="endpoint-groups">
          <div v-for="(endpoints, tag) in filteredEndpoints" :key="tag" class="endpoint-group">
            <div class="group-header" @click="toggleGroup(tag)">
              <span class="group-arrow" :class="{ expanded: expandedGroups[tag] }">▶</span>
              <span class="group-name">{{ tag }}</span>
              <span class="group-count">{{ endpoints.length }}</span>
            </div>
            <div v-if="expandedGroups[tag]" class="group-items">
              <div
                v-for="ep in endpoints"
                :key="ep.path + ep.method"
                class="endpoint-item"
                :class="{ active: selectedEndpoint?.path === ep.path && selectedEndpoint?.method === ep.method }"
                @click="selectEndpoint(ep)"
              >
                <span :class="['method-badge', ep.method]">{{ ep.method.toUpperCase() }}</span>
                <span class="endpoint-path">{{ ep.path }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Request Builder -->
      <div class="request-panel">
        <div class="request-header">
          <span :class="['method-badge', selectedEndpoint?.method]">{{ selectedEndpoint?.method.toUpperCase() || 'GET' }}</span>
          <input v-model="requestUrl" class="url-input" placeholder="Select an endpoint or enter URL" />
          <button class="btn-send" @click="sendRequest" :disabled="loading">
            {{ loading ? '⏳ Sending...' : '▶ Send' }}
          </button>
        </div>

        <!-- Request Tabs -->
        <div class="request-tabs">
          <button
            v-for="tab in ['Headers', 'Body', 'Auth']"
            :key="tab"
            class="tab-btn"
            :class="{ active: activeTab === tab }"
            @click="activeTab = tab"
          >
            {{ tab }}
          </button>
        </div>

        <div class="tab-content">
          <div v-if="activeTab === 'Headers'" class="headers-editor">
            <div v-for="(h, i) in requestHeaders" :key="i" class="header-row">
              <input v-model="h.key" placeholder="Header name" class="header-key" />
              <input v-model="h.value" placeholder="Value" class="header-value" />
              <button class="btn-remove" @click="requestHeaders.splice(i, 1)">✕</button>
            </div>
            <button class="btn-add" @click="requestHeaders.push({ key: '', value: '' })">+ Add Header</button>
          </div>
          <div v-if="activeTab === 'Body'" class="body-editor">
            <textarea v-model="requestBody" placeholder='{"key": "value"}' rows="8" class="body-textarea"></textarea>
          </div>
          <div v-if="activeTab === 'Auth'" class="auth-editor">
            <div class="auth-field">
              <label>API Key</label>
              <input v-model="apiKey" type="password" placeholder="Enter API key" class="auth-input" />
            </div>
            <div class="auth-field">
              <label>Bearer Token</label>
              <input v-model="bearerToken" type="password" placeholder="Enter bearer token" class="auth-input" />
            </div>
          </div>
        </div>
      </div>

      <!-- Response Viewer -->
      <div class="response-panel">
        <div class="response-header">
          <span class="response-title">Response</span>
          <div v-if="response" class="response-meta">
            <span :class="['status-badge', response.status < 400 ? 'success' : 'error']">
              {{ response.status }} {{ response.statusText }}
            </span>
            <span class="timing">{{ response.time }}ms</span>
            <span class="size">{{ formatSize(response.size) }}</span>
          </div>
        </div>

        <div v-if="response" class="response-tabs">
          <button
            v-for="tab in ['Body', 'Headers']"
            :key="tab"
            class="tab-btn"
            :class="{ active: responseTab === tab }"
            @click="responseTab = tab"
          >
            {{ tab }}
          </button>
        </div>

        <div class="response-content">
          <pre v-if="response && responseTab === 'Body'" class="response-body">{{ formatResponse(response.body) }}</pre>
          <div v-if="response && responseTab === 'Headers'" class="response-headers">
            <div v-for="(val, key) in response.headers" :key="key" class="header-line">
              <span class="header-name">{{ key }}:</span>
              <span class="header-val">{{ val }}</span>
            </div>
          </div>
          <div v-if="!response" class="empty-response">
            <span class="empty-icon">📡</span>
            <p>Send a request to see the response</p>
          </div>
        </div>
      </div>
    </div>

    <!-- History -->
    <div class="history-panel">
      <h3>📜 Request History</h3>
      <div class="history-list">
        <div v-for="(item, i) in history" :key="i" class="history-item" @click="loadFromHistory(item)">
          <span :class="['method-badge', item.method]">{{ item.method.toUpperCase() }}</span>
          <span class="history-url">{{ item.url }}</span>
          <span :class="['status-badge', item.status < 400 ? 'success' : 'error']">{{ item.status }}</span>
          <span class="history-time">{{ item.time }}ms</span>
        </div>
        <div v-if="history.length === 0" class="empty-history">No requests yet</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Endpoint {
  method: string
  path: string
  summary?: string
  tag?: string
}

interface HistoryItem {
  method: string
  url: string
  status: number
  time: number
  body?: string
}

const searchQuery = ref('')
const selectedEndpoint = ref<Endpoint | null>(null)
const requestUrl = ref('')
const requestHeaders = ref([{ key: 'Content-Type', value: 'application/json' }])
const requestBody = ref('')
const apiKey = ref('')
const bearerToken = ref('')
const activeTab = ref('Headers')
const responseTab = ref('Body')
const loading = ref(false)
const response = ref<any>(null)
const history = ref<HistoryItem[]>([])
const expandedGroups = ref<Record<string, boolean>>({})
const endpoints = ref<Endpoint[]>([])

const filteredEndpoints = computed(() => {
  const groups: Record<string, Endpoint[]> = {}
  for (const ep of endpoints.value) {
    const tag = ep.tag || 'Other'
    if (searchQuery.value && !ep.path.includes(searchQuery.value) && !ep.summary?.includes(searchQuery.value)) continue
    if (!groups[tag]) groups[tag] = []
    groups[tag].push(ep)
  }
  return groups
})

function toggleGroup(tag: string) {
  expandedGroups.value[tag] = !expandedGroups.value[tag]
}

function selectEndpoint(ep: Endpoint) {
  selectedEndpoint.value = ep
  requestUrl.value = `/api${ep.path}`
}

async function sendRequest() {
  loading.value = true
  const start = performance.now()
  try {
    const headers: Record<string, string> = {}
    for (const h of requestHeaders.value) {
      if (h.key) headers[h.key] = h.value
    }
    if (apiKey.value) headers['X-API-Key'] = apiKey.value
    if (bearerToken.value) headers['Authorization'] = `Bearer ${bearerToken.value}`

    const res = await fetch(requestUrl.value, {
      method: selectedEndpoint.value?.method.toUpperCase() || 'GET',
      headers,
      body: ['POST', 'PUT', 'PATCH'].includes(selectedEndpoint.value?.method || '') ? requestBody.value : undefined,
    })

    const body = await res.text()
    const time = Math.round(performance.now() - start)
    const resHeaders: Record<string, string> = {}
    res.headers.forEach((v, k) => { resHeaders[k] = v })

    response.value = {
      status: res.status,
      statusText: res.statusText,
      body,
      headers: resHeaders,
      time,
      size: body.length,
    }

    history.value.unshift({
      method: selectedEndpoint.value?.method || 'GET',
      url: requestUrl.value,
      status: res.status,
      time,
      body,
    })
    if (history.value.length > 50) history.value.pop()
  } catch (e: any) {
    response.value = {
      status: 0,
      statusText: 'Network Error',
      body: e.message,
      headers: {},
      time: Math.round(performance.now() - start),
      size: 0,
    }
  } finally {
    loading.value = false
  }
}

function loadFromHistory(item: HistoryItem) {
  requestUrl.value = item.url
  selectedEndpoint.value = { method: item.method.toLowerCase(), path: item.url }
  response.value = { status: item.status, body: item.body, headers: {}, time: item.time, size: item.body?.length || 0 }
}

function formatResponse(body: string) {
  try { return JSON.stringify(JSON.parse(body), null, 2) } catch { return body }
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  return `${(bytes / 1024).toFixed(1)} KB`
}

onMounted(async () => {
  try {
    const res = await fetch('/api/openapi.json')
    const spec = await res.json()
    for (const [path, methods] of Object.entries(spec.paths || {})) {
      for (const [method, detail] of Object.entries(methods as any)) {
        const d = detail as any
        endpoints.value.push({
          method,
          path,
          summary: d.summary || '',
          tag: d.tags?.[0] || 'Other',
        })
      }
    }
  } catch { /* openapi not available */ }
})
</script>

<style scoped>
.api-playground { padding: 20px; max-width: 100%; }
.playground-header h1 { font-size: 1.5rem; margin-bottom: 4px; }
.subtitle { color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 20px; }
.playground-layout { display: grid; grid-template-columns: 240px 1fr 1fr; gap: 16px; margin-bottom: 20px; }
.endpoint-list { background: var(--card); border-radius: var(--radius); border: 1px solid var(--border); overflow: hidden; }
.search-input { width: 100%; padding: 10px; border: none; border-bottom: 1px solid var(--border); background: var(--bg); color: var(--primary); font-size: 0.85rem; box-sizing: border-box; }
.endpoint-groups { max-height: 400px; overflow-y: auto; }
.group-header { padding: 8px 12px; cursor: pointer; display: flex; align-items: center; gap: 8px; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); }
.group-header:hover { background: var(--tag-bg); }
.group-arrow { font-size: 0.6rem; transition: transform 0.2s; }
.group-arrow.expanded { transform: rotate(90deg); }
.group-count { margin-left: auto; font-size: 0.7rem; opacity: 0.5; }
.endpoint-item { padding: 6px 12px 6px 28px; cursor: pointer; display: flex; align-items: center; gap: 8px; font-size: 0.75rem; }
.endpoint-item:hover { background: var(--tag-bg); }
.endpoint-item.active { background: var(--accent); color: white; border-radius: 4px; }
.method-badge { font-size: 0.65rem; font-weight: 700; padding: 2px 6px; border-radius: 3px; min-width: 40px; text-align: center; }
.method-badge.get { background: #e3f2fd; color: #1565c0; }
.method-badge.post { background: #e8f5e9; color: #2e7d32; }
.method-badge.put { background: #fff3e0; color: #e65100; }
.method-badge.delete { background: #fce4ec; color: #c62828; }
.endpoint-path { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.request-panel, .response-panel { background: var(--card); border-radius: var(--radius); border: 1px solid var(--border); overflow: hidden; }
.request-header { display: flex; align-items: center; gap: 8px; padding: 10px; border-bottom: 1px solid var(--border); }
.url-input { flex: 1; padding: 8px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--primary); font-size: 0.85rem; }
.btn-send { padding: 8px 16px; background: var(--accent); color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 0.85rem; }
.btn-send:disabled { opacity: 0.6; cursor: not-allowed; }
.request-tabs, .response-tabs { display: flex; border-bottom: 1px solid var(--border); }
.tab-btn { padding: 8px 16px; background: none; border: none; cursor: pointer; font-size: 0.8rem; color: var(--text-secondary); border-bottom: 2px solid transparent; }
.tab-btn.active { color: var(--accent); border-bottom-color: var(--accent); }
.tab-content { padding: 12px; }
.header-row { display: flex; gap: 8px; margin-bottom: 8px; }
.header-key, .header-value { flex: 1; padding: 6px 8px; border: 1px solid var(--border); border-radius: 4px; background: var(--bg); color: var(--primary); font-size: 0.8rem; }
.btn-remove { background: none; border: none; cursor: pointer; color: var(--error-text); font-size: 0.8rem; }
.btn-add { background: none; border: 1px dashed var(--border); cursor: pointer; padding: 6px; width: 100%; border-radius: 4px; color: var(--text-secondary); font-size: 0.8rem; }
.body-textarea { width: 100%; padding: 8px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--primary); font-family: monospace; font-size: 0.8rem; resize: vertical; box-sizing: border-box; }
.auth-field { margin-bottom: 12px; }
.auth-field label { display: block; font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 4px; }
.auth-input { width: 100%; padding: 8px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--primary); font-size: 0.8rem; box-sizing: border-box; }
.response-header { padding: 10px; border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 12px; }
.response-title { font-weight: 600; font-size: 0.9rem; }
.response-meta { display: flex; gap: 8px; align-items: center; }
.status-badge { font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
.status-badge.success { background: #e8f5e9; color: #2e7d32; }
.status-badge.error { background: #fce4ec; color: #c62828; }
.timing, .size { font-size: 0.75rem; color: var(--text-secondary); }
.response-content { padding: 12px; max-height: 400px; overflow-y: auto; }
.response-body { font-family: monospace; font-size: 0.8rem; white-space: pre-wrap; word-break: break-all; }
.response-headers { font-size: 0.8rem; }
.header-line { padding: 4px 0; border-bottom: 1px solid var(--border); }
.header-name { font-weight: 600; margin-right: 8px; }
.empty-response { text-align: center; padding: 40px; color: var(--text-secondary); }
.empty-icon { font-size: 2rem; }
.history-panel { background: var(--card); border-radius: var(--radius); border: 1px solid var(--border); padding: 12px; }
.history-panel h3 { margin: 0 0 10px; font-size: 0.9rem; }
.history-list { max-height: 200px; overflow-y: auto; }
.history-item { display: flex; align-items: center; gap: 8px; padding: 6px 8px; cursor: pointer; border-radius: 4px; font-size: 0.8rem; }
.history-item:hover { background: var(--tag-bg); }
.history-url { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.history-time { font-size: 0.7rem; color: var(--text-secondary); }
.empty-history { text-align: center; color: var(--text-secondary); font-size: 0.8rem; padding: 20px; }
</style>
