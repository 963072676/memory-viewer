<template>
  <div class="api-docs-view">
    <div class="docs-header">
      <h2>📖 API Documentation</h2>
      <p class="subtitle">Interactive Swagger UI — powered by FastAPI</p>
      <div class="actions">
        <a :href="docsUrl" target="_blank" class="btn btn-primary">
          ⤴ Open in New Tab
        </a>
        <a :href="redocUrl" target="_blank" class="btn btn-secondary">
          📚 ReDoc
        </a>
      </div>
    </div>
    <div class="iframe-container">
      <iframe
        :src="docsUrl"
        frameborder="0"
        title="Swagger UI API Documentation"
        @load="iframeLoaded = true"
      />
      <div v-if="!iframeLoaded" class="loading">
        <span class="spinner" />
        <p>Loading API docs…</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const docsUrl = '/api/docs'
const redocUrl = '/api/redoc'
const iframeLoaded = ref(false)
</script>

<style scoped>
.api-docs-view {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  gap: 16px;
}

.docs-header {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.docs-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--primary);
}

.docs-header .subtitle {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
  font-family: var(--font);
}

.btn-primary {
  background: var(--accent);
  color: white;
}

.btn-primary:hover {
  opacity: 0.85;
}

.btn-secondary {
  background: var(--tag-bg);
  color: var(--primary);
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  background: var(--border);
}

.iframe-container {
  flex: 1;
  position: relative;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  overflow: hidden;
  background: white;
}

.iframe-container iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: var(--bg);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading p {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin: 0;
}
</style>
