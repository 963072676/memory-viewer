<template>
  <div class="settings-view">
    <h1 class="settings-title">⚙️ 设置</h1>

    <div class="settings-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="settings-tab"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        {{ tab.icon }} {{ tab.label }}
      </button>
    </div>

    <div class="settings-content">
      <!-- 记忆源 -->
      <div v-if="activeTab === 'sources'" class="settings-panel">
        <SourcesView />
      </div>

      <!-- Webhook -->
      <div v-if="activeTab === 'webhook'" class="settings-panel">
        <h2>🔗 Webhook 配置</h2>
        <div class="form-section">
          <div class="form-field">
            <label>Webhook URL</label>
            <input
              v-model="webhookUrl"
              type="url"
              placeholder="https://example.com/webhook"
              class="form-input"
            />
          </div>
          <div class="form-field">
            <label>Secret</label>
            <input
              v-model="webhookSecret"
              type="password"
              placeholder="可选"
              class="form-input"
            />
          </div>
          <div class="form-field row">
            <label>启用</label>
            <button
              class="toggle-btn"
              :class="{ active: webhookEnabled }"
              @click="webhookEnabled = !webhookEnabled"
            >
              {{ webhookEnabled ? 'ON' : 'OFF' }}
            </button>
          </div>
          <div class="form-field">
            <label>事件</label>
            <div class="events-grid">
              <label v-for="evt in eventKeys" :key="evt" class="checkbox-label">
                <input type="checkbox" v-model="webhookEvents[evt]" />
                <span>{{ evt }}</span>
              </label>
            </div>
          </div>
          <div class="form-actions">
            <button class="btn-primary" @click="saveWebhook" :disabled="webhookSaving">
              {{ webhookSaving ? '保存中...' : '保存' }}
            </button>
            <span v-if="webhookSaved" class="save-ok">✓ 已保存</span>
          </div>
        </div>
      </div>

      <!-- 通知 -->
      <div v-if="activeTab === 'notifications'" class="settings-panel">
        <h2>🔔 通知配置</h2>
        <div class="form-section">
          <div class="form-field">
            <label>飞书 Webhook URL</label>
            <input
              v-model="feishuUrl"
              type="url"
              placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/..."
              class="form-input"
            />
          </div>
          <div class="form-field">
            <label>飞书 Secret（签名校验）</label>
            <input
              v-model="feishuSecret"
              type="password"
              placeholder="可选"
              class="form-input"
            />
          </div>
          <div class="form-field row">
            <label>启用飞书通知</label>
            <button
              class="toggle-btn"
              :class="{ active: feishuEnabled }"
              @click="feishuEnabled = !feishuEnabled"
            >
              {{ feishuEnabled ? 'ON' : 'OFF' }}
            </button>
          </div>
          <div class="form-field">
            <label>通知事件</label>
            <div class="events-grid">
              <label v-for="evt in feishuEventKeys" :key="evt" class="checkbox-label">
                <input type="checkbox" v-model="feishuEvents[evt]" />
                <span>{{ evt }}</span>
              </label>
            </div>
          </div>
          <div class="form-actions">
            <button class="btn-primary" @click="saveFeishu" :disabled="feishuSaving">
              {{ feishuSaving ? '保存中...' : '保存' }}
            </button>
            <span v-if="feishuSaved" class="save-ok">✓ 已保存</span>
          </div>
        </div>
      </div>

      <!-- 关于 -->
      <div v-if="activeTab === 'about'" class="settings-panel">
        <h2>ℹ️ 关于</h2>
        <div class="about-section">
          <div class="about-row">
            <span class="about-label">应用</span>
            <span class="about-value">Memory Viewer v2</span>
          </div>
          <div class="about-row">
            <span class="about-label">版本</span>
            <span class="about-value">{{ appVersion }}</span>
          </div>
          <div class="about-row">
            <span class="about-label">框架</span>
            <span class="about-value">Vue 3 + TypeScript + Vite</span>
          </div>
          <div class="about-row">
            <span class="about-label">许可证</span>
            <span class="about-value">MIT</span>
          </div>
          <div class="about-links">
            <a href="https://github.com/NousResearch" target="_blank" class="about-link">GitHub</a>
            <a href="/api-docs" class="about-link">API 文档</a>
            <router-link to="/api-playground" class="about-link">API Playground</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, defineAsyncComponent } from 'vue'
import { fetchWebhookConfig, updateWebhookConfig } from '@/api/webhook'

const SourcesView = defineAsyncComponent(() => import('@/views/SourcesView.vue'))

const tabs = [
  { id: 'sources' as const, icon: '🔌', label: '记忆源' },
  { id: 'webhook' as const, icon: '🔗', label: 'Webhook' },
  { id: 'notifications' as const, icon: '🔔', label: '通知' },
  { id: 'about' as const, icon: 'ℹ️', label: '关于' },
]

const activeTab = ref<'sources' | 'webhook' | 'notifications' | 'about'>('sources')

// Webhook config
const webhookUrl = ref('')
const webhookSecret = ref('')
const webhookEnabled = ref(false)
const webhookEvents = reactive<Record<string, boolean>>({
  create: true,
  update: true,
  delete: true,
})
const webhookSaving = ref(false)
const webhookSaved = ref(false)
const eventKeys = ['create', 'update', 'delete']

// Feishu config
const feishuUrl = ref('')
const feishuSecret = ref('')
const feishuEnabled = ref(false)
const feishuEvents = reactive<Record<string, boolean>>({
  create: true,
  update: true,
  delete: true,
  summary: true,
})
const feishuSaving = ref(false)
const feishuSaved = ref(false)
const feishuEventKeys = ['create', 'update', 'delete', 'summary']

// Version
const appVersion = ref('2.0.0')

onMounted(async () => {
  try {
    const cfg = await fetchWebhookConfig()
    webhookUrl.value = cfg.webhook_url
    webhookEnabled.value = cfg.enabled
    webhookEvents.create = cfg.events.create
    webhookEvents.update = cfg.events.update
    webhookEvents.delete = cfg.events.delete
  } catch {
    // ignore
  }

  // Load feishu config
  try {
    const res = await fetch('/api/notifications/feishu/config')
    if (res.ok) {
      const cfg = await res.json()
      feishuUrl.value = cfg.webhook_url || ''
      feishuEnabled.value = cfg.enabled ?? false
      if (cfg.events) {
        Object.keys(cfg.events).forEach(k => {
          if (k in feishuEvents) feishuEvents[k] = cfg.events[k]
        })
      }
    }
  } catch {
    // ignore
  }
})

async function saveWebhook() {
  webhookSaving.value = true
  webhookSaved.value = false
  try {
    await updateWebhookConfig({
      enabled: webhookEnabled.value,
      webhook_url: webhookUrl.value,
      ...(webhookSecret.value ? { secret: webhookSecret.value } : {}),
      events: { ...webhookEvents },
    })
    webhookSaved.value = true
    setTimeout(() => { webhookSaved.value = false }, 2000)
  } catch (e) {
    console.error('Failed to save webhook config:', e)
  } finally {
    webhookSaving.value = false
  }
}

async function saveFeishu() {
  feishuSaving.value = true
  feishuSaved.value = false
  try {
    const res = await fetch('/api/notifications/feishu/config', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        enabled: feishuEnabled.value,
        webhook_url: feishuUrl.value,
        ...(feishuSecret.value ? { secret: feishuSecret.value } : {}),
        events: { ...feishuEvents },
      }),
    })
    if (res.ok) {
      feishuSaved.value = true
      setTimeout(() => { feishuSaved.value = false }, 2000)
    }
  } catch (e) {
    console.error('Failed to save feishu config:', e)
  } finally {
    feishuSaving.value = false
  }
}
</script>

<style scoped>
.settings-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.settings-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 24px;
}

.settings-tabs {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 24px;
  overflow-x: auto;
}

.settings-tab {
  position: relative;
  padding: 10px 18px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  cursor: pointer;
  font-family: var(--font);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
  white-space: nowrap;
  transition: color 0.15s, background 0.15s, border-color 0.15s;
}

.settings-tab:hover {
  color: var(--primary);
  background: var(--tag-bg);
}

.settings-tab.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
  background: var(--accent-soft);
  font-weight: 600;
}

.settings-content {
  min-height: 400px;
}

.settings-panel h2 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 20px;
}

/* Form */
.form-section {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.form-field.row {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.form-field label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-input {
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--primary);
  font-size: 0.875rem;
  font-family: var(--font);
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.2s ease;
}

/* P38 (round 4): form-input focus ring 与 SearchBar 对齐 — 4px accent glow。
   之前只改 border-color 没有 box-shadow，键盘 Tab 聚焦时输入框没有清晰的"激活"反馈。 */
.form-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-glow);
}

.toggle-btn {
  padding: 6px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.8rem;
  font-family: var(--font);
  font-weight: 600;
  transition: all 0.2s ease;
}

.toggle-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--card);
}

.events-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: var(--primary);
  cursor: pointer;
}

.checkbox-label input[type='checkbox'] {
  width: 16px;
  height: 16px;
  accent-color: var(--accent);
}

.form-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

/* P44: token 化收尾 — color: white → var(--card)。
   --card 是 P39 决策的"按钮文字 token"（亮色 #fff / 暗色 #000），
   与 HomeView .action-btn--primary 保持一致 — 不同页面用同色 token，
   未来调整主题色不用逐文件改。
   注：本文件是"表单保存按钮"，颜色决策（--accent vs --primary）暂保留，
   是 P41 #1 / P43 #2 的设计决策点，不在本轮范围。 */
.btn-primary {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  background: var(--accent);
  color: var(--card);
  cursor: pointer;
  font-size: 0.875rem;
  font-family: var(--font);
  font-weight: 500;
  transition: opacity 0.2s ease, background 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  background: color-mix(in srgb, var(--accent) 88%, var(--primary) 12%);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.save-ok {
  font-size: 0.85rem;
  color: var(--success-text);
  font-weight: 600;
}

/* About */
.about-section {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
}

.about-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}

.about-row:last-of-type {
  border-bottom: none;
}

.about-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.about-value {
  font-size: 0.85rem;
  color: var(--primary);
  font-weight: 600;
}

.about-links {
  display: flex;
  gap: 16px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

.about-link {
  font-size: 0.85rem;
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
}

.about-link:hover {
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 767px) {
  .settings-view {
    padding: 16px;
  }

  .settings-title {
    font-size: 1.25rem;
  }

  .settings-tab {
    padding: 8px 12px;
    font-size: 0.8rem;
  }

  .form-section {
    padding: 16px;
  }
}
</style>
