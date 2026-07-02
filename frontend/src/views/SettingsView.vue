<template>
  <div class="settings-view">
    <h1 class="settings-title">⚙️ {{ $t('i18n.settings') }}</h1>

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

      <div v-if="activeTab === 'providers'" class="settings-panel">
        <ProviderPanel />
      </div>

      <!-- Webhook -->
      <div v-if="activeTab === 'webhook'" class="settings-panel">
        <h2 class="section-title">🔗 Webhook {{ $t('i18n.config') }}</h2>
        <div class="form-section">
          <div class="form-field">
            <label>{{ $t('en_webhook_url') }}</label>
            <input
              v-model="webhookUrl"
              type="url"
              :placeholder="$t('en_webhook_url_hint')"
              class="form-input"
            />
          </div>
          <div class="form-field">
            <label>{{ $t('en_secret') }}</label>
            <input
              v-model="webhookSecret"
              type="password"
              :placeholder="$t('i18n.optional')"
              class="form-input"
            />
          </div>
          <div class="form-field row">
            <label>{{ $t('i18n.enable') }}</label>
            <button
              class="toggle-btn"
              :class="{ active: webhookEnabled }"
              @click="webhookEnabled = !webhookEnabled"
            >
              {{ webhookEnabled ? 'ON' : 'OFF' }}
            </button>
          </div>
          <div class="form-field">
            <label>{{ $t('i18n.event') }}</label>
            <div class="events-grid">
              <label v-for="evt in eventKeys" :key="evt" class="checkbox-label">
                <input type="checkbox" v-model="webhookEvents[evt]" />
                <span>{{ evt }}</span>
              </label>
            </div>
          </div>
          <div class="form-actions">
            <button class="action-btn action-btn--accent" @click="saveWebhook" :disabled="webhookSaving">
              {{ webhookSaving ? $t('i18n.saving') : $t('i18n.save') }}
            </button>
            <span v-if="webhookSaved" class="save-ok">✓ {{ $t('i18n.saved') }}</span>
          </div>
        </div>
      </div>

      <!-- 通知 -->
      <div v-if="activeTab === 'notifications'" class="settings-panel">
        <h2 class="section-title">🔔 {{ $t('i18n.notification_config') }}</h2>
        <div class="form-section">
          <div class="form-field">
            <label>{{ $t('i18n.feishu') }} Webhook URL</label>
            <input
              v-model="feishuUrl"
              type="url"
              :placeholder="$t('en_feishu_url_hint')"
              class="form-input"
            />
          </div>
          <div class="form-field">
            <label>{{ $t('i18n.feishu') }} Secret（{{ $t('i18n.signature_check') }}）</label>
            <input
              v-model="feishuSecret"
              type="password"
              :placeholder="$t('i18n.optional')"
              class="form-input"
            />
          </div>
          <div class="form-field row">
            <label>{{ $t('i18n.enable_feishu') }}</label>
            <button
              class="toggle-btn"
              :class="{ active: feishuEnabled }"
              @click="feishuEnabled = !feishuEnabled"
            >
              {{ feishuEnabled ? 'ON' : 'OFF' }}
            </button>
          </div>
          <div class="form-field">
            <label>{{ $t('i18n.notification_event') }}</label>
            <div class="events-grid">
              <label v-for="evt in feishuEventKeys" :key="evt" class="checkbox-label">
                <input type="checkbox" v-model="feishuEvents[evt]" />
                <span>{{ evt }}</span>
              </label>
            </div>
          </div>
          <div class="form-actions">
            <button class="action-btn action-btn--accent" @click="saveFeishu" :disabled="feishuSaving">
              {{ feishuSaving ? $t('i18n.saving') : $t('i18n.save') }}
            </button>
            <span v-if="feishuSaved" class="save-ok">✓ {{ $t('i18n.saved') }}</span>
          </div>
        </div>
      </div>

      <!-- 关于 -->
      <div v-if="activeTab === 'about'" class="settings-panel">
        <h2 class="section-title">ℹ️ {{ $t('i18n.about') }}</h2>
        <div class="about-section">
          <div class="about-row">
            <span class="about-label">{{ $t('i18n.apply') }}</span>
            <span class="about-value">{{ $t('en_app_v2') }}</span>
          </div>
          <div class="about-row">
            <span class="about-label">{{ $t('i18n.version') }}</span>
            <span class="about-value">{{ appVersion }}</span>
          </div>
          <div class="about-row">
            <span class="about-label">{{ $t('i18n.framework') }}</span>
            <span class="about-value">{{ $t('en_stack_info') }}</span>
          </div>
          <div class="about-row">
            <span class="about-label">{{ $t('i18n.license') }}</span>
            <span class="about-value">MIT</span>
          </div>
          <div class="about-links">
            <a href="https://github.com/NousResearch" target="_blank" class="about-link">{{ $t('en_github') }}</a>
            <a href="/api-docs" class="about-link">API {{ $t('i18n.document') }}</a>
            <router-link to="/api-playground" class="about-link">{{ $t('en_api_playground') }}</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, defineAsyncComponent } from 'vue'
import { useRoute } from 'vue-router'
import { fetchWebhookConfig, updateWebhookConfig } from '@/api/webhook'

const SourcesView = defineAsyncComponent(() => import('@/views/SourcesView.vue'))
const ProviderPanel = defineAsyncComponent(() => import('@/components/Layout/ProviderPanel.vue'))

type SettingsTab = 'sources' | 'providers' | 'webhook' | 'notifications' | 'about'

const tabs = [
  { id: 'sources' as const, icon: '🔌', label: '记忆源' },
  { id: 'providers' as const, icon: 'P', label: 'Providers' },
  { id: 'webhook' as const, icon: '🔗', label: 'Webhook' },
  { id: 'notifications' as const, icon: '🔔', label: '通知' },
  { id: 'about' as const, icon: 'ℹ️', label: '关于' },
]

const route = useRoute()
const tabParam = typeof route.query.tab === 'string' ? route.query.tab : ''
const activeTab = ref<SettingsTab>(
  tabs.some(tab => tab.id === tabParam) ? tabParam as SettingsTab : 'providers',
)

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

/* P50 r1: settings-tab active bg --accent-soft → --accent-subtle — 统一 active 视觉语言.
   旧 --accent-soft (rgba(0,114,245,0.05)) 在白卡上几乎不可见 (alpha 5% → 视觉权重 ~0),
   仅有底部 1px border 和文字变色撑起 "active" 语义, 用户视觉上要"找半天才看到选中".
   改用 --accent-subtle (#e6f0ff, 全站 AppSidebar .nav-item.active + bottom sheet active
   都在用), 形成全站 "active = solid 浅蓝填充 + accent 文字 + 1px border" 统一语言. */
.settings-tab.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
  background: var(--accent-subtle);
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

/* P38 r27: section-title 左侧 3px accent bar — 与全站 7 个 view (AgentMemory/HermesMemory/Profiles/Sources/Dashboard/Compare/Collections) 同源.
   之前 SettingsView 3 个 h2 (Webhook/通知/关于) 缺少 class, 与全站 section title 系统不一致.
   复用 r20 模式 (3px rail + 12px padding-left) — 视觉锚点统一. */
.settings-panel h2.section-title {
  position: relative;
  padding-left: 12px;
}

.settings-panel h2.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--accent);
  border-radius: 0 2px 2px 0;
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

/* P38 r21: button system unification — base .action-btn is global in
   styles/main.css. Local --accent override kept here because the page
   needs the blue "submit" affordance (uses --accent, not --primary ink). */
.action-btn--accent {
  background: var(--accent);
  color: var(--card);
  border: none;
}

.action-btn--accent:hover:not(:disabled) {
  background: color-mix(in srgb, var(--accent) 88%, var(--primary) 12%);
}

.action-btn--accent:disabled {
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
