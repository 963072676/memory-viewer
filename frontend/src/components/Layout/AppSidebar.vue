<template>
  <!-- ============ DESKTOP SIDEBAR (≥ 768px) ============ -->
  <aside class="sidebar desktop-only" :class="{ collapsed: uiStore.sidebarCollapsed }">
    <button class="sidebar-collapse-btn" @click="uiStore.toggleSidebar()" :title="uiStore.sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'">
      <span class="collapse-icon" :class="{ rotated: uiStore.sidebarCollapsed }">‹</span>
    </button>

    <div class="sidebar-brand">
      <span class="brand-logo">🧠</span>
      <span class="brand-text" v-show="!uiStore.sidebarCollapsed">Memory Viewer</span>
    </div>

    <nav>
      <div v-for="section in navSections" :key="section.title" class="nav-section">
        <div v-show="!uiStore.sidebarCollapsed" class="nav-section-title">{{ section.title }}</div>
        <router-link v-for="item in section.items" :key="item.path" :to="item.path" class="nav-item" :class="{ active: $route.path === item.path }">
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </div>
    </nav>
  </aside>

  <!-- ============ MOBILE TOP HEADER (< 768px) ============ -->
  <header class="mobile-header mobile-only">
    <div class="mobile-brand">
      <span class="brand-logo">🧠</span>
      <span class="brand-text">Memory Viewer</span>
    </div>
    <button v-if="$route.path !== '/'" class="mobile-back-btn" @click="$router.back()" title="返回">
      ‹
    </button>
  </header>

  <!-- ============ MOBILE BOTTOM TAB BAR (< 768px) ============ -->
  <nav class="mobile-tab-bar mobile-only">
    <router-link
      v-for="tab in mobileTabs"
      :key="tab.path"
      :to="tab.path"
      class="tab-item"
      :class="{ active: isTabActive(tab) }"
    >
      <span class="tab-icon">{{ tab.icon }}</span>
      <span class="tab-label">{{ tab.label }}</span>
    </router-link>
    <button class="tab-item more-btn" @click="showMoreSheet = true">
      <span class="tab-icon">☰</span>
      <span class="tab-label">更多</span>
    </button>
  </nav>

  <!-- ============ MOBILE MORE SHEET (Bottom Sheet) ============ -->
  <Teleport to="body">
    <Transition name="sheet">
      <div v-if="showMoreSheet" class="bottom-sheet-overlay" @click="showMoreSheet = false">
        <div class="bottom-sheet" @click.stop>
          <div class="sheet-handle"></div>
          <h3 class="sheet-title">所有页面</h3>
          <div class="sheet-grid">
            <router-link
              v-for="item in allNavItems"
              :key="item.path"
              :to="item.path"
              class="sheet-item"
              :class="{ active: $route.path === item.path }"
              @click="showMoreSheet = false"
            >
              <span class="sheet-icon">{{ item.icon }}</span>
              <span class="sheet-label">{{ item.label }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useUIStore } from '@/stores/ui'

const route = useRoute()
const uiStore = useUIStore()
const showMoreSheet = ref(false)

// All nav items in display order
const allNavItems = [
  { path: '/', icon: '🏠', label: '首页' },
  { path: '/agentmemory', icon: '🤖', label: 'AgentMemory' },
  { path: '/hermes', icon: '🧠', label: 'Hermes Memory' },
  { path: '/profiles', icon: '👤', label: 'Profiles' },
  { path: '/dashboard', icon: '📊', label: '仪表盘' },
  { path: '/collections', icon: '📚', label: '分类' },
  { path: '/compare', icon: '🔍', label: '对比' },
  { path: '/sources', icon: '🔌', label: '数据源' },
  { path: '/settings', icon: '⚙️', label: '设置' },
]

// Group items for desktop sidebar
const navSections = [
  {
    title: '记忆浏览',
    items: allNavItems.filter(i => ['/', '/agentmemory', '/hermes', '/profiles'].includes(i.path))
  },
  {
    title: '功能',
    items: allNavItems.filter(i => ['/dashboard', '/collections', '/compare', '/sources'].includes(i.path))
  },
  {
    title: '系统',
    items: allNavItems.filter(i => ['/settings'].includes(i.path))
  },
]

// Mobile bottom tab bar - 4 most-used + More
const mobileTabs = allNavItems.filter(i => ['/', '/agentmemory', '/hermes', '/profiles'].includes(i.path))

// Tab matches if exact or sub-route
function isTabActive(tab: { path: string }) {
  if (tab.path === '/') return route.path === '/'
  return route.path === tab.path || route.path.startsWith(tab.path + '/')
}
</script>

<style scoped>
/* ============ Visibility helpers ============ */
.desktop-only { display: flex; }
.mobile-only { display: none; }

@media (max-width: 767px) {
  .desktop-only { display: none !important; }
  .mobile-only { display: flex; }
}

/* ============ Desktop Sidebar (≥ 768px) ============ */
.sidebar {
  width: 220px;
  min-width: 220px;
  background: var(--card);
  border-right: 1px solid var(--border);
  height: 100vh;
  position: sticky;
  top: 0;
  flex-direction: column;
  padding: 16px 0;
  transition: width 0.3s cubic-bezier(0.25, 0.1, 0.25, 1), min-width 0.3s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.sidebar.collapsed {
  width: 64px;
  min-width: 64px;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px 16px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 12px;
}

.brand-logo {
  font-size: 1.6rem;
  flex-shrink: 0;
}

.brand-text {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
}

.sidebar nav {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 8px 0 16px;
}

.nav-section {
  margin-bottom: 12px;
}

.nav-section-title {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-secondary);
  padding: 6px 12px 4px;
  letter-spacing: 0.05em;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  color: var(--text-primary);
  text-decoration: none;
  font-size: 0.9rem;
  transition: background 0.15s, color 0.15s;
  margin-bottom: 2px;
}

.nav-item:hover {
  background: var(--tag-bg);
}

.nav-item.active {
  background: var(--accent-subtle);
  color: var(--accent);
  font-weight: 600;
}

/* P38: 激活态左侧 rail 指示器 — Geist 风格（v 站侧边栏常见） */
.nav-item.active::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 8px;
  bottom: 8px;
  width: 3px;
  border-radius: 0 2px 2px 0;
  background: var(--accent);
  transition: background 0.2s;
}

.sidebar.collapsed .nav-item.active::before {
  left: 0;
  top: 6px;
  bottom: 6px;
}

.nav-icon {
  font-size: 1.1rem;
  flex-shrink: 0;
  width: 24px;
  text-align: center;
}

.nav-label {
  white-space: nowrap;
  overflow: hidden;
}

.sidebar.collapsed .nav-label,
.sidebar.collapsed .nav-section-title,
.sidebar.collapsed .brand-text {
  display: none;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 12px;
}

.sidebar-collapse-btn {
  position: absolute;
  top: 14px;
  right: 10px;
  width: 24px;
  height: 24px;
  border: none;
  background: var(--tag-bg);
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all 0.2s;
  z-index: 5;
}

.sidebar-collapse-btn:hover {
  background: var(--border);
}

.collapse-icon {
  font-size: 16px;
  transition: transform 0.3s;
  display: inline-block;
}

.collapse-icon.rotated {
  transform: rotate(180deg);
}

/* ============ Mobile Top Header (< 768px) ============ */
.mobile-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: var(--card);
  border-bottom: 1px solid var(--border);
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  z-index: 50;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.mobile-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mobile-header .brand-logo {
  font-size: 1.4rem;
}

.mobile-header .brand-text {
  font-size: 0.95rem;
  font-weight: 600;
}

.mobile-back-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.5rem;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.mobile-back-btn:hover {
  background: var(--border);
}

/* ============ Mobile Bottom Tab Bar (< 768px) ============ */
.mobile-tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--card);
  border-top: 1px solid var(--border);
  align-items: center;
  justify-content: space-around;
  padding: 0 4px env(safe-area-inset-bottom, 0);
  z-index: 50;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.06);
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  flex: 1;
  height: 100%;
  text-decoration: none;
  color: var(--text-secondary);
  font-size: 0.65rem;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 6px 0;
  transition: color 0.15s;
  -webkit-tap-highlight-color: transparent;
}

.tab-item.active {
  color: var(--accent);
}

.tab-icon {
  font-size: 1.4rem;
  line-height: 1;
}

.tab-label {
  font-weight: 500;
}

/* ============ Bottom Sheet (More menu) ============ */
.bottom-sheet-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 200;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.bottom-sheet {
  width: 100%;
  max-width: 500px;
  background: var(--card);
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
  padding: 12px 16px 32px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.15);
}

.sheet-handle {
  width: 40px;
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  margin: 0 auto 16px;
}

.sheet-title {
  margin: 0 0 16px;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.sheet-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.sheet-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 14px 8px;
  border-radius: 12px;
  text-decoration: none;
  color: var(--text-primary);
  background: var(--tag-bg);
  transition: all 0.15s;
  -webkit-tap-highlight-color: transparent;
}

.sheet-item:active {
  transform: scale(0.96);
}

.sheet-item.active {
  background: var(--accent);
  color: white;
}

.sheet-icon {
  font-size: 1.5rem;
}

.sheet-label {
  font-size: 0.7rem;
  font-weight: 500;
  text-align: center;
}

/* ============ Sheet Transition ============ */
.sheet-enter-active,
.sheet-leave-active {
  transition: opacity 0.25s ease;
}

.sheet-enter-active .bottom-sheet,
.sheet-leave-active .bottom-sheet {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.sheet-enter-from,
.sheet-leave-to {
  opacity: 0;
}

.sheet-enter-from .bottom-sheet,
.sheet-leave-to .bottom-sheet {
  transform: translateY(100%);
}
</style>
