<template>
  <!-- ============ DESKTOP SIDEBAR (≥ 768px) ============ -->
  <!-- 顶栏 ☰ 按钮已统一处理 desktop 收/展 + mobile 打开 more 抽屉,
       侧栏内的 collapse 按钮是冗余的(同一功能,占用 24×24 空间),
       因此移除 -->
  <aside class="sidebar desktop-only" :class="{ collapsed: uiStore.sidebarCollapsed }">

    <div class="sidebar-brand">
      <span class="brand-logo">🧠</span>
      <span class="brand-text" v-show="!uiStore.sidebarCollapsed">{{ $t('en_app_title') }}</span>
    </div>

    <nav>
      <div v-for="section in navSections" :key="section.titleKey" class="nav-section">
        <div v-show="!uiStore.sidebarCollapsed" class="nav-section-title">{{ $t(section.titleKey) }}</div>
        <router-link v-for="item in section.items" :key="item.path" :to="item.path" class="nav-item" :class="{ active: $route.path === item.path }" :data-tour="item.path">
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ $t(item.labelKey) }}</span>
        </router-link>
      </div>
    </nav>
  </aside>

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
      <span class="tab-label">{{ $t(tab.labelKey) }}</span>
    </router-link>
    <button class="tab-item more-btn" @click="showMoreSheet = true">
      <span class="tab-icon">☰</span>
      <span class="tab-label">{{ $t('i18n.more') }}</span>
    </button>
  </nav>

  <!-- ============ MOBILE MORE SHEET (Bottom Sheet) ============ -->
  <Teleport to="body">
    <Transition name="sheet">
      <div v-if="showMoreSheet" class="bottom-sheet-overlay" @click="showMoreSheet = false">
        <div class="bottom-sheet" @click.stop>
          <div class="sheet-handle"></div>
          <h3 class="sheet-title">{{ $t('i18n.all_pages') }}</h3>
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
              <span class="sheet-label">{{ $t(item.labelKey) }}</span>
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

// 暴露给父组件（App.vue）调用的方法
function openMoreSheet() { showMoreSheet.value = true }
function closeMobileSidebar() { showMoreSheet.value = false }
defineExpose({ openMoreSheet, closeMobileSidebar })

// All nav items in display order
const allNavItems = [
  { path: '/', icon: '🏠', labelKey: 'en_nav_home' },
  { path: '/agentmemory', icon: '🤖', labelKey: 'en_nav_agentmemory' },
  { path: '/hermes', icon: '🧠', labelKey: 'en_nav_hermes' },
  { path: '/profiles', icon: '👤', labelKey: 'en_nav_profiles' },
  { path: '/dashboard', icon: '📊', labelKey: 'en_nav_dashboard' },
  { path: '/graph', icon: 'G', labelKey: 'i18n.memory_graph' },
  { path: '/collections', icon: '📚', labelKey: 'en_nav_collections' },
  { path: '/compare', icon: '🔍', labelKey: 'en_nav_compare' },
  { path: '/sources', icon: '🔌', labelKey: 'en_nav_sources' },
  { path: '/plugins', icon: 'P', labelKey: 'en_nav_plugins' },
  { path: '/settings', icon: '⚙️', labelKey: 'en_nav_settings' },
]

// Group items for desktop sidebar
const navSections = [
  {
    titleKey: 'en_nav_section_browse',
    items: allNavItems.filter(i => ['/', '/agentmemory', '/hermes', '/profiles'].includes(i.path))
  },
  {
    titleKey: 'en_nav_section_features',
    items: allNavItems.filter(i => ['/dashboard', '/graph', '/collections', '/compare', '/sources'].includes(i.path))
  },
  {
    titleKey: 'en_nav_section_system',
    items: allNavItems.filter(i => ['/plugins', '/settings'].includes(i.path))
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
  /* P1-1 PM-20260612-001 cleanup: 改用 --nav-section-title-color（light 6.4:1 / dark 7.66:1），
     替代 --text-secondary（light 仅 3.10:1，AC-6 不达标）。 */
  color: var(--nav-section-title-color);
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

/* 桌面收/展按钮已并入顶栏 ☰ 按钮(AppHeader.onToggleSidebar),
   这里不再需要 sidebar-collapse-btn 相关样式
.sidebar-collapse-btn { ... 删除 ... }
.collapse-icon { ... 删除 ... }
.collapse-icon.rotated { ... 删除 ... */

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
  box-shadow: 0 -2px 8px var(--shadow-toolbar);
}

.tab-item {
  position: relative;
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
  transition: color 0.15s, background 0.15s;
  -webkit-tap-highlight-color: transparent;
}

/* P38 (round 8): 移动端 tab 激活态强化 — 对齐 desktop 侧栏的 "rail 指示器" 语言。
   之前只改 color，弱于 desktop 的 left rail + bottom-sheet 的 filled bg。
   镜像设计：desktop 用 3px left rail，mobile 用 3px top rail（iOS segmented 风格）。
   同时追加 subtle 背景色（与 sheet-item 选中态一致），形成"全站 3 套选中态统一"的视觉语言：
     - desktop sidebar nav-item: 3px left rail + accent-subtle bg
     - mobile bottom tab:       3px top rail + accent-subtle bg
     - mobile bottom sheet:     filled accent bg + white text */
.tab-item.active {
  color: var(--accent);
  background: var(--accent-subtle);
  font-weight: 600;
}

.tab-item.active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 3px;
  border-radius: 0 0 2px 2px;
  background: var(--accent);
}

.tab-icon {
  font-size: 1.4rem;
  line-height: 1;
  display: block;
  margin-bottom: 2px;
}

.tab-label {
  font-weight: 500;
  display: block;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
  font-size: 0.65rem;
  line-height: 1.2;
}

@media (max-width: 767px) {
  .tab-item {
    padding: 4px 2px;
  }
  .tab-icon {
    font-size: 1.3rem;
    margin-bottom: 1px;
  }
  .tab-label {
    font-size: 0.62rem;
  }
}

/* ============ Bottom Sheet (More menu) ============ */
.bottom-sheet-overlay {
  position: fixed;
  inset: 0;
  background: var(--modal-backdrop);
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
  box-shadow: 0 -4px 20px var(--shadow-modal);
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
  /* P38 r17: 改 hardcoded white → var(--card), 与 QuickAccessBar .quick-btn.active 同源.
     light 模式 sheet-item.active = accent 背景 + 白字 (视觉锚点).
     dark 模式 sheet-item.active = accent 背景 + 深底色字, 避免 dark 上的"白上加白"刺眼. */
  color: var(--card);
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
