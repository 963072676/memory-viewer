<template>
  <header class="app-header">
    <div class="header-content">
      <button class="sidebar-toggle" @click="$emit('toggle-sidebar')" title="切换侧边栏">
        <span>☰</span>
      </button>
      <div class="header-title">
        <h1>Memory Viewer</h1>
        <p>Hermes Agent 记忆系统全景视图</p>
      </div>
      <div class="header-right">
        <button class="theme-toggle" @click="toggleTheme" :title="modeLabel()">
          <span>{{ modeIcon() }}</span>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'
const { toggleTheme, modeLabel, modeIcon } = useTheme()

defineEmits<{
  'toggle-sidebar': []
}>()
</script>

<style scoped>
/* P37: Header 视觉边界 — sticky + blur + border */
.app-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--header-bg);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid var(--header-border);
  padding: 0;
  transition: background 0.2s ease;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-title {
  flex: 1;
  text-align: center;
  min-width: 0; /* 允许收缩 */
}

.header-title h1 {
  font-size: 1.6rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-title p {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-toggle {
  background: var(--tag-bg);
  border: none;
  border-radius: 10px;
  width: 38px;
  height: 38px;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  transition: all 0.2s;
  flex-shrink: 0;
}

.sidebar-toggle:hover {
  background: var(--border);
  transform: scale(1.05);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.theme-toggle {
  background: var(--tag-bg);
  border: none;
  border-radius: 50%;
  width: 38px;
  height: 38px;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.theme-toggle:hover {
  transform: scale(1.1);
}

@media (max-width: 767px) {
  .app-header {
    padding: 12px 0 8px;
  }

  .header-title h1 {
    font-size: 1.2rem;
  }

  .header-title p {
    font-size: 0.75rem;
  }
  
  .sidebar-toggle,
  .theme-toggle {
    width: 34px;
    height: 34px;
    font-size: 1rem;
  }
}
</style>
