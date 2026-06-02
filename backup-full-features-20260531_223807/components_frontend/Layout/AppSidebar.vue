<template>
  <aside class="sidebar" :class="{ collapsed: uiStore.sidebarCollapsed, 'mobile-open': mobileOpen }">
    <!-- Mobile overlay -->
    <div v-if="mobileOpen" class="sidebar-overlay" @click="mobileOpen = false"></div>

    <!-- Mobile hamburger button -->
    <button class="mobile-hamburger" @click="mobileOpen = !mobileOpen" :class="{ active: mobileOpen }">
      <span class="hamburger-line"></span>
      <span class="hamburger-line"></span>
      <span class="hamburger-line"></span>
    </button>

    <!-- Desktop collapse toggle -->
    <button class="sidebar-collapse-btn" @click="uiStore.toggleSidebar()" :title="uiStore.sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'">
      <span class="collapse-icon" :class="{ rotated: uiStore.sidebarCollapsed }">‹</span>
    </button>

    <nav>
      <!-- 📋 记忆浏览 -->
      <div class="nav-group">
        <div class="nav-group-header" @click="toggleGroup('browse')">
          <span class="nav-group-icon">📋</span>
          <span class="nav-group-title">记忆浏览</span>
          <span class="nav-group-arrow" :class="{ open: groupOpen.browse }">▶</span>
        </div>
        <transition name="group-expand">
          <div v-show="groupOpen.browse" class="nav-group-items">
            <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
              <span class="nav-icon">📋</span>
              <span class="nav-label">全部记忆</span>
            </router-link>
            <router-link to="/agentmemory" class="nav-item" :class="{ active: $route.path === '/agentmemory' }">
              <span class="nav-icon">🤖</span>
              <span class="nav-label">AgentMemory</span>
            </router-link>
            <router-link to="/hermes" class="nav-item" :class="{ active: $route.path === '/hermes' }">
              <span class="nav-icon">🧠</span>
              <span class="nav-label">Hermes Memory</span>
            </router-link>
            <router-link to="/profiles" class="nav-item" :class="{ active: $route.path === '/profiles' }">
              <span class="nav-icon">👤</span>
              <span class="nav-label">Profiles</span>
            </router-link>
          </div>
        </transition>
      </div>

      <!-- SmartCollections & FavoritesPanel -->
      <div v-show="!uiStore.sidebarCollapsed">
        <SmartCollections />
        <FavoritesPanel />
      </div>

      <!-- 🔍 智能分析 -->
      <div class="nav-group">
        <div class="nav-group-header" @click="toggleGroup('analysis')">
          <span class="nav-group-icon">🔍</span>
          <span class="nav-group-title">智能分析</span>
          <span class="nav-group-arrow" :class="{ open: groupOpen.analysis }">▶</span>
        </div>
        <transition name="group-expand">
          <div v-show="groupOpen.analysis" class="nav-group-items">
            <router-link to="/dashboard" class="nav-item" :class="{ active: $route.path === '/dashboard' }">
              <span class="nav-icon">📊</span>
              <span class="nav-label">统计仪表盘</span>
            </router-link>
            <router-link to="/timeline" class="nav-item" :class="{ active: $route.path === '/timeline' }">
              <span class="nav-icon">📅</span>
              <span class="nav-label">时间线</span>
            </router-link>
            <router-link to="/graph" class="nav-item" :class="{ active: $route.path === '/graph' }">
              <span class="nav-icon">🕸️</span>
              <span class="nav-label">关联图谱</span>
            </router-link>
            <router-link to="/clusters" class="nav-item" :class="{ active: $route.path === '/clusters' }">
              <span class="nav-icon">🫧</span>
              <span class="nav-label">记忆聚类</span>
            </router-link>
            <router-link to="/anomalies" class="nav-item" :class="{ active: $route.path === '/anomalies' }">
              <span class="nav-icon">🚨</span>
              <span class="nav-label">异常检测</span>
            </router-link>
            <router-link to="/cross-agent" class="nav-item" :class="{ active: $route.path === '/cross-agent' }">
              <span class="nav-icon">🤝</span>
              <span class="nav-label">跨 Agent 洞察</span>
            </router-link>
          </div>
        </transition>
      </div>

      <!-- 📝 管理 -->
      <div class="nav-group">
        <div class="nav-group-header" @click="toggleGroup('manage')">
          <span class="nav-group-icon">📝</span>
          <span class="nav-group-title">管理</span>
          <span class="nav-group-arrow" :class="{ open: groupOpen.manage }">▶</span>
        </div>
        <transition name="group-expand">
          <div v-show="groupOpen.manage" class="nav-group-items">
            <router-link to="/compare" class="nav-item" :class="{ active: $route.path === '/compare' }">
              <span class="nav-icon">🔍</span>
              <span class="nav-label">记忆对比</span>
            </router-link>
            <router-link to="/templates" class="nav-item" :class="{ active: $route.path === '/templates' }">
              <span class="nav-icon">📝</span>
              <span class="nav-label">记忆模板</span>
            </router-link>
            <router-link to="/workspaces" class="nav-item" :class="{ active: $route.path === '/workspaces' }">
              <span class="nav-icon">🏢</span>
              <span class="nav-label">工作空间</span>
            </router-link>
            <router-link to="/governance" class="nav-item" :class="{ active: $route.path === '/governance' }">
              <span class="nav-icon">📜</span>
              <span class="nav-label">治理策略</span>
            </router-link>
            <router-link to="/snapshots" class="nav-item" :class="{ active: $route.path === '/snapshots' }">
              <span class="nav-icon">📸</span>
              <span class="nav-label">快照管理</span>
            </router-link>
            <router-link to="/collections" class="nav-item" :class="{ active: $route.path === '/collections' }">
              <span class="nav-icon">📚</span>
              <span class="nav-label">Collections</span>
            </router-link>
          </div>
        </transition>
      </div>

      <!-- 🔧 工具 -->
      <div class="nav-group">
        <div class="nav-group-header" @click="toggleGroup('tools')">
          <span class="nav-group-icon">🔧</span>
          <span class="nav-group-title">工具</span>
          <span class="nav-group-arrow" :class="{ open: groupOpen.tools }">▶</span>
        </div>
        <transition name="group-expand">
          <div v-show="groupOpen.tools" class="nav-group-items">
            <router-link to="/digest" class="nav-item" :class="{ active: $route.path === '/digest' }">
              <span class="nav-icon">📋</span>
              <span class="nav-label">AI Digest</span>
            </router-link>
            <router-link to="/llm-usage" class="nav-item" :class="{ active: $route.path === '/llm-usage' }">
              <span class="nav-icon">💰</span>
              <span class="nav-label">LLM 用量</span>
            </router-link>
            <router-link to="/api-playground" class="nav-item" :class="{ active: $route.path === '/api-playground' }">
              <span class="nav-icon">🔗</span>
              <span class="nav-label">API Playground</span>
            </router-link>
            <router-link to="/health-scan" class="nav-item" :class="{ active: $route.path === '/health-scan' }">
              <span class="nav-icon">🩺</span>
              <span class="nav-label">Health Scanner</span>
            </router-link>
            <router-link to="/reports" class="nav-item" :class="{ active: $route.path === '/reports' }">
              <span class="nav-icon">📊</span>
              <span class="nav-label">Reports</span>
            </router-link>
            <router-link to="/custom-dashboard" class="nav-item" :class="{ active: $route.path === '/custom-dashboard' }">
              <span class="nav-icon">🧩</span>
              <span class="nav-label">自定义面板</span>
            </router-link>
          </div>
        </transition>
      </div>

      <div class="nav-divider"></div>

      <!-- ⚡ 操作 -->
      <div class="nav-group">
        <div class="nav-group-header" @click="toggleGroup('actions')">
          <span class="nav-group-icon">⚡</span>
          <span class="nav-group-title">操作</span>
          <span class="nav-group-arrow" :class="{ open: groupOpen.actions }">▶</span>
        </div>
        <transition name="group-expand">
          <div v-show="groupOpen.actions" class="nav-group-items">
            <router-link to="/subscriptions" class="nav-item" :class="{ active: $route.path === '/subscriptions' }">
              <span class="nav-icon">📡</span>
              <span class="nav-label">Webhook 订阅</span>
            </router-link>
            <button class="nav-item nav-button" @click="sendSummary">
              <span class="nav-icon">📊</span>
              <span class="nav-label">发送摘要</span>
            </button>
          </div>
        </transition>
      </div>

      <!-- ⚙️ 设置 -->
      <div class="nav-group">
        <div class="nav-group-header" @click="toggleGroup('settings')">
          <span class="nav-group-icon">⚙️</span>
          <span class="nav-group-title">设置</span>
          <span class="nav-group-arrow" :class="{ open: groupOpen.settings }">▶</span>
        </div>
        <transition name="group-expand">
          <div v-show="groupOpen.settings" class="nav-group-items">
            <router-link to="/sources" class="nav-item" :class="{ active: $route.path === '/sources' }">
              <span class="nav-icon">🔌</span>
              <span class="nav-label">记忆源</span>
            </router-link>
            <router-link to="/diagnostics" class="nav-item" :class="{ active: $route.path === '/diagnostics' }">
              <span class="nav-icon">🩺</span>
              <span class="nav-label">诊断</span>
            </router-link>
            <router-link to="/audit" class="nav-item" :class="{ active: $route.path === '/audit' }">
              <span class="nav-icon">📋</span>
              <span class="nav-label">审计日志</span>
            </router-link>
            <button class="nav-item nav-button" @click="showWebhookPanel = !showWebhookPanel">
              <span class="nav-icon">🔗</span>
              <span class="nav-label">Webhook 配置</span>
            </button>
            <router-link to="/api-docs" class="nav-item" :class="{ active: $route.path === '/api-docs' }">
              <span class="nav-icon">📖</span>
              <span class="nav-label">API Docs</span>
            </router-link>
            <router-link to="/settings" class="nav-item" :class="{ active: $route.path === '/settings' }">
              <span class="nav-icon">⚙️</span>
              <span class="nav-label">设置</span>
            </router-link>
            <button class="nav-item nav-button" @click="openChangelog">
              <span class="nav-icon">🎉</span>
              <span class="nav-label">更新日志</span>
              <span v-if="hasUpdate" class="update-dot"></span>
            </button>
          </div>
        </transition>
      </div>
    </nav>

    <!-- Webhook Config Panel (inline) -->
    <transition name="slide">
      <div v-if="showWebhookPanel && !uiStore.sidebarCollapsed" class="webhook-panel">
        <h4>Webhook 配置</h4>
        <div class="webhook-field">
          <label>URL</label>
          <input
            v-model="webhookUrl"
            type="url"
            placeholder="https://example.com/webhook"
            class="webhook-input"
          />
        </div>
        <div class="webhook-field">
          <label>Secret</label>
          <input
            v-model="webhookSecret"
            type="password"
            placeholder="可选"
            class="webhook-input"
          />
        </div>
        <div class="webhook-field row">
          <label>启用</label>
          <button
            class="toggle-btn"
            :class="{ active: webhookEnabled }"
            @click="webhookEnabled = !webhookEnabled"
          >
            {{ webhookEnabled ? 'ON' : 'OFF' }}
          </button>
        </div>
        <div class="webhook-events">
          <label v-for="evt in eventKeys" :key="evt" class="checkbox-label">
            <input type="checkbox" v-model="webhookEvents[evt]" />
            <span>{{ evt }}</span>
          </label>
        </div>
        <div class="webhook-actions">
          <button class="btn-save" @click="saveWebhook" :disabled="webhookSaving">
            {{ webhookSaving ? '保存中...' : '保存' }}
          </button>
          <span v-if="webhookSaved" class="save-ok">✓ 已保存</span>
        </div>
      </div>
    </transition>
  </aside>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUIStore } from '@/stores/ui'
import { useChangelog } from '@/composables/useChangelog'
import { fetchWebhookConfig, updateWebhookConfig } from '@/api/webhook'
import SmartCollections from './SmartCollections.vue'
import FavoritesPanel from './FavoritesPanel.vue'

const uiStore = useUIStore()
const { hasUpdate, openModal } = useChangelog()

// Mobile state
const mobileOpen = ref(false)

// Close mobile sidebar on navigation
function closeMobileSidebar() {
  mobileOpen.value = false
}

// Expose for parent component
defineExpose({ mobileOpen, closeMobileSidebar })

// Group collapse state — persisted to localStorage
const GROUP_STORAGE_KEY = 'sidebar-group-state'

interface GroupState {
  browse: boolean
  analysis: boolean
  manage: boolean
  tools: boolean
  actions: boolean
  settings: boolean
}

function loadGroupState(): GroupState {
  try {
    const raw = localStorage.getItem(GROUP_STORAGE_KEY)
    if (raw) return JSON.parse(raw) as GroupState
  } catch { /* ignore */ }
  // Defaults: browse open, others closed
  return { browse: true, analysis: false, manage: false, tools: false, actions: false, settings: false }
}

function saveGroupState() {
  localStorage.setItem(GROUP_STORAGE_KEY, JSON.stringify(groupOpen))
}

const groupOpen = reactive<GroupState>(loadGroupState())

function toggleGroup(key: keyof GroupState) {
  groupOpen[key] = !groupOpen[key]
  saveGroupState()
}

// Changelog
function openChangelog() {
  openModal()
}

// Feishu summary
async function sendSummary() {
  try {
    const res = await fetch('/api/memory/summary/send-to-feishu', { method: 'POST' })
    const data = await res.json()
    if (data.success) {
      alert('摘要已发送到飞书')
    } else {
      alert('发送失败: ' + (data.error || '未知错误'))
    }
  } catch {
    alert('发送失败')
  }
}

// Webhook config panel
const showWebhookPanel = ref(false)
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

onMounted(async () => {
  try {
    const cfg = await fetchWebhookConfig()
    webhookUrl.value = cfg.webhook_url
    webhookEnabled.value = cfg.enabled
    webhookEvents.create = cfg.events.create
    webhookEvents.update = cfg.events.update
    webhookEvents.delete = cfg.events.delete
  } catch {
    // ignore on first load
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
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 220px;
  height: 100vh;
  background: var(--card);
  border-right: 1px solid var(--border);
  transition: width 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
  overflow-y: auto;
  overflow-x: hidden;
  z-index: 100;
  padding-top: 12px;
  display: flex;
  flex-direction: column;
}

/* ---- Collapse toggle button ---- */
.sidebar-collapse-btn {
  position: absolute;
  top: 14px;
  right: 10px;
  width: 24px;
  height: 24px;
  border: none;
  background: var(--tag-bg);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: all 0.2s ease;
  color: var(--text-secondary);
  font-size: 1.1rem;
  padding: 0;
  line-height: 1;
}

.sidebar-collapse-btn:hover {
  background: var(--border);
  color: var(--primary);
}

.collapse-icon {
  display: inline-block;
  transition: transform 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.collapse-icon.rotated {
  transform: rotate(180deg);
}

/* ---- Collapsed state ---- */
.sidebar.collapsed {
  width: 60px;
}

.sidebar.collapsed .sidebar-collapse-btn {
  top: auto;
  bottom: 16px;
  right: 50%;
  transform: translateX(50%);
}

.sidebar.collapsed .nav-group-title,
.sidebar.collapsed .nav-group-arrow,
.sidebar.collapsed .nav-label,
.sidebar.collapsed .webhook-panel,
.sidebar.collapsed .nav-divider + .nav-group .nav-group-header .nav-group-title {
  display: none;
}

.sidebar.collapsed .nav-group-header {
  justify-content: center;
  padding: 10px 8px;
}

.sidebar.collapsed .nav-group-icon {
  font-size: 1.1rem;
}

.sidebar.collapsed .nav-group-items {
  padding-left: 0;
  align-items: center;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 9px 8px;
  gap: 0;
}

.sidebar.collapsed .nav-item .nav-icon {
  margin: 0;
}

/* Tooltip on hover for collapsed nav items */
.sidebar.collapsed .nav-item {
  position: relative;
}

.sidebar.collapsed .nav-item .nav-icon::after {
  content: attr(data-tooltip);
  display: none;
}

/* Hide SmartCollections & FavoritesPanel when collapsed (handled by v-show) */

/* ---- Nav structure ---- */
nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.nav-group {
  margin-bottom: 2px;
}

.nav-group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  cursor: pointer;
  user-select: none;
  border-radius: var(--radius);
  transition: background 0.15s ease;
}

.nav-group-header:hover {
  background: var(--tag-bg);
}

.nav-group-icon {
  font-size: 0.85rem;
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.nav-group-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  letter-spacing: 0.02em;
  flex: 1;
  white-space: nowrap;
}

.nav-group-arrow {
  font-size: 0.55rem;
  color: var(--text-secondary);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.nav-group-arrow.open {
  transform: rotate(90deg);
}

.nav-group-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-left: 8px;
}

/* Nav items */
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 7px 14px;
  border-radius: var(--radius);
  color: var(--primary);
  text-decoration: none;
  transition: all 0.2s ease;
  font-size: 0.85rem;
  font-weight: 400;
}

.nav-item:hover {
  background: var(--tag-bg);
}

.nav-item.active {
  background: var(--accent);
  color: white;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.2);
}

.nav-button {
  background: none;
  border: none;
  cursor: pointer;
  font-family: var(--font);
  font-size: 0.85rem;
  position: relative;
  width: 100%;
  text-align: left;
}

.nav-icon {
  font-size: 1rem;
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-divider {
  height: 1px;
  background: var(--border);
  margin: 6px 8px;
}

.update-dot {
  position: absolute;
  top: 8px;
  right: 12px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* Group expand transition */
.group-expand-enter-active,
.group-expand-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.group-expand-enter-from,
.group-expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.group-expand-enter-to,
.group-expand-leave-from {
  opacity: 1;
  max-height: 500px;
}

/* Webhook panel */
.webhook-panel {
  margin-top: 8px;
  padding: 12px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.webhook-panel h4 {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 10px;
}

.webhook-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
}

.webhook-field.row {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.webhook-field label {
  font-size: 0.7rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.webhook-input {
  padding: 6px 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--primary);
  font-size: 0.75rem;
  font-family: var(--font);
  width: 100%;
  box-sizing: border-box;
}

.toggle-btn {
  padding: 4px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.7rem;
  font-family: var(--font);
  font-weight: 600;
}

.toggle-btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}

.webhook-events {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.7rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.checkbox-label input[type='checkbox'] {
  width: 14px;
  height: 14px;
  accent-color: var(--accent);
}

.webhook-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-save {
  padding: 6px 14px;
  border: none;
  border-radius: 6px;
  background: var(--accent);
  color: white;
  cursor: pointer;
  font-size: 0.75rem;
  font-family: var(--font);
  font-weight: 500;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.save-ok {
  font-size: 0.7rem;
  color: var(--success-text);
  font-weight: 600;
}

/* Slide transition */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
  margin-top: 0;
}

.slide-enter-to,
.slide-leave-from {
  opacity: 1;
  max-height: 400px;
}

/* Mobile overlay */
.sidebar-overlay {
  display: none;
}

/* Mobile hamburger button */
.mobile-hamburger {
  display: none;
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 101;
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 8px;
  background: var(--accent);
  color: white;
  cursor: pointer;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.hamburger-line {
  display: block;
  width: 22px;
  height: 2px;
  background: white;
  border-radius: 1px;
  transition: all 0.3s ease;
}

.mobile-hamburger.active .hamburger-line:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}

.mobile-hamburger.active .hamburger-line:nth-child(2) {
  opacity: 0;
}

.mobile-hamburger.active .hamburger-line:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

/* Responsive */
@media (max-width: 767px) {
  .sidebar {
    width: 0;
    overflow: hidden;
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 100;
    background: var(--card);
    border-right: 1px solid var(--border);
    transition: width 0.3s ease, box-shadow 0.3s ease;
    padding: 0;
  }

  .sidebar:not(.collapsed) {
    width: 0;
  }

  .sidebar.collapsed {
    width: 0;
    padding: 0;
  }

  .sidebar.mobile-open {
    width: 240px;
    box-shadow: 4px 0 20px rgba(0,0,0,0.3);
    z-index: 100;
    overflow: visible;
    padding: 16px 0;
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: transparent;
    z-index: 99;
    pointer-events: none;
  }

  nav {
    position: relative;
    z-index: 100;
    overflow-y: auto;
    overflow-x: hidden;
    height: 100vh;
    padding-top: 50px; /* Space for hamburger button */
  }

  .nav-item {
    position: relative;
    z-index: 100;
    pointer-events: auto;
  }

  .nav-group-header {
    position: relative;
    z-index: 100;
    pointer-events: auto;
  }

  .nav-label {
    font-size: 0.85rem;
  }

  .sidebar-collapse-btn {
    display: none;
  }

  .mobile-hamburger {
    display: flex;
    position: fixed;
    top: 12px;
    left: 12px;
    z-index: 101;
  }

  /* Adjust layout when sidebar is open */
  .sidebar.mobile-open + .main-content,
  .has-sidebar .main-content {
    margin-left: 0;
  }
}
</style>
