<template>
  <div class="playground-view">
    <div class="pg-header">
      <h2>🧪 API Playground</h2>
      <div class="pg-actions">
        <button class="btn-clear" @click="clearHistory">Clear History</button>
        <button class="btn-import" @click="showCurlImport = true">Import cURL</button>
      </div>
    </div>

    <div class="pg-layout">
      <!-- Left: Request Builder + History -->
      <div class="pg-left">
        <!-- Templates -->
        <div class="templates-bar">
          <span class="templates-label">Templates:</span>
          <button v-for="t in templates" :key="t.name" class="template-btn" @click="applyTemplate(t)">
            {{ t.name }}
          </button>
        </div>

        <!-- Request Builder -->
        <div class="request-builder">
          <div class="method-url">
            <select v-model="req.method" class="method-select" :class="req.method">
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="DELETE">DELETE</option>
              <option value="PATCH">PATCH</option>
            </select>
            <input v-model="req.url" class="url-input" placeholder="/api/health" @keydown.enter="sendRequest" />
            <button class="btn-send" @click="sendRequest" :disabled="sending">
              {{ sending ? '⏳' : '▶ Send' }}
            </button>
          </div>

          <!-- Tabs: Headers, Body, Params -->
          <div class="builder-tabs">
            <button :class="{ active: builderTab === 'headers' }" @click="builderTab = 'headers'">
              Headers ({{ req.headers.length }})
            </button>
            <button :class="{ active: builderTab === 'params' }" @click="builderTab = 'params'">
              Params ({{ req.params.length }})
            </button>
            <button :class="{ active: builderTab === 'body' }" @click="builderTab = 'body'">Body</button>
          </div>

          <!-- Headers -->
          <div v-if="builderTab === 'headers'" class="kv-editor">
            <div v-for="(h, i) in req.headers" :key="i" class="kv-row">
              <input v-model="h.key" placeholder="Header name" />
              <input v-model="h.value" placeholder="Value" />
              <button class="btn-remove" @click="req.headers.splice(i, 1)">✕</button>
            </div>
            <button class="btn-add" @click="req.headers.push({ key: '', value: '' })">+ Add Header</button>
          </div>

          <!-- Params -->
          <div v-if="builderTab === 'params'" class="kv-editor">
            <div v-for="(p, i) in req.params" :key="i" class="kv-row">
              <input v-model="p.key" placeholder="Parameter name" />
              <input v-model="p.value" placeholder="Value" />
              <button class="btn-remove" @click="req.params.splice(i, 1)">✕</button>
            </div>
            <button class="btn-add" @click="req.params.push({ key: '', value: '' })">+ Add Parameter</button>
          </div>

          <!-- Body -->
          <div v-if="builderTab === 'body'" class="body-editor">
            <textarea v-model="req.body" placeholder='{"key": "value"}' rows="8" spellcheck="false"></textarea>
          </div>
        </div>

        <!-- History -->
        <div class="history-panel">
          <h4>📜 History ({{ history.length }})</h4>
          <div class="history-list">
            <div v-for="(h, i) in history" :key="i" class="history-item" @click="loadFromHistory(h)">
              <span class="hist-method" :class="h.method">{{ h.method }}</span>
              <span class="hist-url">{{ h.url }}</span>
              <span class="hist-status" :class="statusClass(h.status)">{{ h.status }}</span>
              <span class="hist-time">{{ h.duration }}ms</span>
            </div>
            <div v-if="!history.length" class="hist-empty">No requests yet</div>
          </div>
        </div>
      </div>

      <!-- Right: Response Viewer -->
      <div class="pg-right">
        <div v-if="response" class="response-viewer">
          <div class="response-header">
            <span class="resp-status" :class="statusClass(response.status)">
              {{ response.status }} {{ response.statusText }}
            </span>
            <span class="resp-meta">
              ⏱ {{ response.duration }}ms | 📦 {{ response.size }}
            </span>
          </div>

          <div class="response-tabs">
            <button :class="{ active: respTab === 'body' }" @click="respTab = 'body'">Body</button>
            <button :class="{ active: respTab === 'headers' }" @click="respTab = 'headers'">
              Headers ({{ Object.keys(response.headers || {}).length }})
            </button>
          </div>

          <div v-if="respTab === 'body'" class="response-body">
            <pre><code>{{ response.body }}</code></pre>
          </div>

          <div v-if="respTab === 'headers'" class="response-headers">
            <div v-for="(val, key) in response.headers" :key="key" class="header-row">
              <span class="header-key">{{ key }}:</span>
              <span class="header-val">{{ val }}</span>
            </div>
          </div>
        </div>

        <div v-else class="response-empty">
          <p>🔬 Send a request to see the response</p>
        </div>
      </div>
    </div>

    <!-- cURL Import Modal -->
    <div v-if="showCurlImport" class="modal-overlay" @click.self="showCurlImport = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Import cURL Command</h3>
          <button class="btn-close" @click="showCurlImport = false">✕</button>
        </div>
        <div class="modal-body">
          <textarea v-model="curlInput" placeholder="curl -X POST /api/agentmemory -H 'Content-Type: application/json' -d '{...}'" rows="5"></textarea>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showCurlImport = false">Cancel</button>
          <button class="btn-save" @click="importCurl">Import</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const templates = [
  { name: 'Health', method: 'GET', url: '/api/health', body: '' },
  { name: 'List Memories', method: 'GET', url: '/api/agentmemory', body: '' },
  { name: 'Search', method: 'GET', url: '/api/search?q=test', body: '' },
  { name: 'Create Memory', method: 'POST', url: '/api/agentmemory', body: JSON.stringify({ content: 'Test memory', title: 'Test', profile: 'dev-worker' }, null, 2) },
  { name: 'Stats', method: 'GET', url: '/api/stats', body: '' },
]

const req = reactive({
  method: 'GET',
  url: '/api/health',
  headers: [{ key: 'Content-Type', value: 'application/json' }],
  params: [] as { key: string; value: string }[],
  body: '',
})

const builderTab = ref('headers')
const respTab = ref('body')
const sending = ref(false)
const showCurlImport = ref(false)
const curlInput = ref('')
const response = ref<any>(null)
const history = ref<any[]>([])

function statusClass(status: number): string {
  if (status >= 200 && status < 300) return 's2xx'
  if (status >= 300 && status < 400) return 's3xx'
  if (status >= 400 && status < 500) return 's4xx'
  return 's5xx'
}

function buildUrl(): string {
  let url = req.url
  // Ensure URL starts with /api or full URL
  if (!url.startsWith('http') && !url.startsWith('/')) {
    url = '/' + url
  }

  const params = req.params.filter(p => p.key)
  if (params.length) {
    const qs = params.map(p => `${encodeURIComponent(p.key)}=${encodeURIComponent(p.value)}`).join('&')
    url += (url.includes('?') ? '&' : '?') + qs
  }
  return url
}

async function sendRequest() {
  sending.value = true
  const fullUrl = buildUrl()
  const start = performance.now()

  try {
    const headers: Record<string, string> = {}
    for (const h of req.headers) {
      if (h.key) headers[h.key] = h.value
    }

    const fetchOptions: RequestInit = {
      method: req.method,
      headers,
    }

    if (['POST', 'PUT', 'PATCH'].includes(req.method) && req.body) {
      fetchOptions.body = req.body
    }

    const url = fullUrl.startsWith('http') ? fullUrl : fullUrl
    const res = await fetch(url, fetchOptions)
    const duration = Math.round(performance.now() - start)

    let body = ''
    try {
      body = await res.text()
      // Try to pretty-print JSON
      try {
        body = JSON.stringify(JSON.parse(body), null, 2)
      } catch {}
    } catch {}

    const respHeaders: Record<string, string> = {}
    res.headers.forEach((val, key) => {
      respHeaders[key] = val
    })

    response.value = {
      status: res.status,
      statusText: res.statusText,
      headers: respHeaders,
      body,
      duration,
      size: formatBytes(body.length),
    }

    // Add to history
    history.value.unshift({
      method: req.method,
      url: req.url,
      status: res.status,
      duration,
      timestamp: new Date().toISOString(),
    })
    if (history.value.length > 50) history.value.pop()
    saveHistory()
  } catch (err: any) {
    const duration = Math.round(performance.now() - start)
    response.value = {
      status: 0,
      statusText: 'Network Error',
      headers: {},
      body: err.message || 'Failed to fetch',
      duration,
      size: '0 B',
    }
  }
  sending.value = false
}

function applyTemplate(t: any) {
  req.method = t.method
  req.url = t.url
  req.body = t.body || ''
}

function loadFromHistory(h: any) {
  req.method = h.method
  req.url = h.url
}

function clearHistory() {
  history.value = []
  localStorage.removeItem('pg_history')
}

function saveHistory() {
  localStorage.setItem('pg_history', JSON.stringify(history.value.slice(0, 50)))
}

function importCurl() {
  const curl = curlInput.value.trim()
  if (!curl) return

  // Parse basic cURL
  const methodMatch = curl.match(/-X\s+(\w+)/)
  req.method = methodMatch ? methodMatch[1].toUpperCase() : 'GET'

  // Extract URL
  const urlMatch = curl.match(/(?:curl\s+)?(?:-\w+\s+\S+\s+)*['"]?(https?:\/\/\S+|\/\S+)['"]?/)
  if (urlMatch) {
    req.url = urlMatch[1].replace(/['"]/g, '')
  }

  // Extract headers
  const headerMatches = curl.matchAll(/-H\s+['"]([^'"]+)['"]/g)
  req.headers = []
  for (const m of headerMatches) {
    const [key, ...valueParts] = m[1].split(':')
    req.headers.push({ key: key.trim(), value: valueParts.join(':').trim() })
  }

  // Extract body
  const bodyMatch = curl.match(/-d\s+['"](.+?)['"]/s)
  if (bodyMatch) {
    req.body = bodyMatch[1]
  }

  showCurlImport.value = false
  curlInput.value = ''
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

onMounted(() => {
  try {
    const saved = localStorage.getItem('pg_history')
    if (saved) history.value = JSON.parse(saved)
  } catch {}
})
</script>

<style scoped>
.playground-view { padding-bottom: 40px; }
.pg-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.pg-header h2 { font-size: 1.5rem; font-weight: 600; margin: 0; }
.pg-actions { display: flex; gap: 8px; }
.btn-clear, .btn-import {
  padding: 6px 14px; border: 1px solid var(--border); border-radius: 6px;
  background: var(--tag-bg); cursor: pointer; font-size: 0.8rem; font-family: var(--font);
}

.pg-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 1024px) { .pg-layout { grid-template-columns: 1fr; } }

.templates-bar {
  display: flex; align-items: center; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;
}
.templates-label { font-size: 0.8rem; color: var(--text-secondary); }
.template-btn {
  padding: 4px 10px; border: 1px solid var(--border); border-radius: 6px;
  background: var(--tag-bg); cursor: pointer; font-size: 0.75rem; font-family: var(--font);
}
.template-btn:hover { background: var(--accent); color: #fff; border-color: var(--accent); }

.request-builder {
  background: var(--card); border: 1px solid var(--border); border-radius: 12px;
  padding: 16px; margin-bottom: 16px;
}
.method-url { display: flex; gap: 8px; margin-bottom: 12px; }
.method-select {
  padding: 8px; border: 1px solid var(--border); border-radius: 8px;
  font-weight: 600; font-family: var(--font); font-size: 0.85rem; width: 90px;
}
.method-select.GET { background: #e3f2fd; color: #1565c0; }
.method-select.POST { background: #e8f5e9; color: #2e7d32; }
.method-select.PUT { background: #fff3e0; color: #e65100; }
.method-select.DELETE { background: #fce4ec; color: #c62828; }
.method-select.PATCH { background: #f3e5f5; color: #7b1fa2; }
.url-input {
  flex: 1; padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px;
  font-family: monospace; font-size: 0.9rem;
}
.btn-send {
  padding: 8px 20px; background: var(--accent); color: #fff; border: none;
  border-radius: 8px; cursor: pointer; font-weight: 600; font-family: var(--font);
}
.btn-send:disabled { opacity: 0.6; }

.builder-tabs { display: flex; gap: 4px; margin-bottom: 12px; }
.builder-tabs button {
  padding: 6px 12px; border: 1px solid var(--border); border-radius: 6px;
  background: var(--card); cursor: pointer; font-size: 0.8rem; font-family: var(--font);
}
.builder-tabs button.active { background: var(--accent); color: #fff; border-color: var(--accent); }

.kv-editor { display: flex; flex-direction: column; gap: 6px; }
.kv-row { display: flex; gap: 6px; }
.kv-row input {
  flex: 1; padding: 6px 8px; border: 1px solid var(--border); border-radius: 6px;
  font-size: 0.8rem; font-family: var(--font);
}
.btn-remove { background: none; border: none; color: var(--error); cursor: pointer; font-size: 1rem; }
.btn-add {
  padding: 4px 10px; background: var(--tag-bg); border: 1px dashed var(--border);
  border-radius: 6px; cursor: pointer; font-size: 0.8rem; font-family: var(--font);
}

.body-editor textarea {
  width: 100%; padding: 8px; border: 1px solid var(--border); border-radius: 8px;
  font-family: monospace; font-size: 0.85rem; resize: vertical; box-sizing: border-box;
}

.history-panel {
  background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 12px;
}
.history-panel h4 { margin: 0 0 8px; font-size: 0.9rem; }
.history-list { max-height: 300px; overflow-y: auto; }
.history-item {
  display: flex; align-items: center; gap: 8px; padding: 6px 8px;
  border-radius: 6px; cursor: pointer; font-size: 0.8rem;
}
.history-item:hover { background: var(--tag-bg); }
.hist-method { font-weight: 600; font-family: monospace; font-size: 0.75rem; width: 50px; }
.hist-method.GET { color: #1565c0; }
.hist-method.POST { color: #2e7d32; }
.hist-method.PUT { color: #e65100; }
.hist-method.DELETE { color: #c62828; }
.hist-url { flex: 1; font-family: monospace; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hist-status { font-weight: 600; }
.hist-status.s2xx { color: #34c759; }
.hist-status.s4xx { color: #ff9500; }
.hist-status.s5xx { color: #ff3b30; }
.hist-time { color: var(--text-secondary); font-size: 0.75rem; }
.hist-empty { text-align: center; padding: 16px; color: var(--text-secondary); font-size: 0.85rem; }

.response-viewer {
  background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 16px;
}
.response-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.resp-status { font-weight: 700; font-size: 1rem; }
.resp-status.s2xx { color: #34c759; }
.resp-status.s3xx { color: #007aff; }
.resp-status.s4xx { color: #ff9500; }
.resp-status.s5xx { color: #ff3b30; }
.resp-meta { font-size: 0.8rem; color: var(--text-secondary); }

.response-tabs { display: flex; gap: 4px; margin-bottom: 12px; }
.response-tabs button {
  padding: 4px 10px; border: 1px solid var(--border); border-radius: 6px;
  background: var(--card); cursor: pointer; font-size: 0.8rem; font-family: var(--font);
}
.response-tabs button.active { background: var(--accent); color: #fff; }

.response-body pre {
  background: var(--bg); border: 1px solid var(--border); border-radius: 8px;
  padding: 12px; overflow: auto; max-height: 500px; font-size: 0.8rem; margin: 0;
}

.response-headers { display: flex; flex-direction: column; gap: 4px; }
.header-row { display: flex; gap: 8px; font-size: 0.8rem; }
.header-key { font-weight: 600; color: var(--accent); }
.header-val { color: var(--text-secondary); word-break: break-all; }

.response-empty {
  display: flex; align-items: center; justify-content: center;
  background: var(--card); border: 1px solid var(--border); border-radius: 12px;
  min-height: 300px; color: var(--text-secondary); font-size: 1rem;
}

.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 100;
  display: flex; align-items: center; justify-content: center; padding: 20px;
}
.modal {
  background: var(--card); border-radius: 16px; width: 100%; max-width: 560px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid var(--border);
}
.modal-header h3 { margin: 0; }
.btn-close { background: none; border: none; font-size: 1.2rem; cursor: pointer; }
.modal-body { padding: 20px; }
.modal-body textarea {
  width: 100%; padding: 8px; border: 1px solid var(--border); border-radius: 8px;
  font-family: monospace; font-size: 0.85rem; resize: vertical; box-sizing: border-box;
}
.modal-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 12px 20px; border-top: 1px solid var(--border);
}
.btn-cancel, .btn-save {
  padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; cursor: pointer; font-family: var(--font);
}
.btn-cancel { background: var(--card); border: 1px solid var(--border); }
.btn-save { background: var(--accent); color: #fff; border: none; }
</style>
