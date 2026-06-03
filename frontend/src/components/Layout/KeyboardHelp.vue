<template>
  <div class="keyboard-help-overlay" @click.self="uiStore.toggleKeyboardHelp()">
    <div class="keyboard-help">
      <h2>键盘快捷键</h2>
      <div class="shortcut-list">
        <div class="shortcut-item">
          <kbd>Ctrl K</kbd>
          <span>打开命令面板</span>
        </div>
        <div class="shortcut-item">
          <kbd>/</kbd>
          <span>聚焦搜索框</span>
        </div>
        <div class="shortcut-item">
          <kbd>Esc</kbd>
          <span>清除搜索 / 关闭弹窗</span>
        </div>
        <div class="shortcut-item">
          <kbd>R</kbd>
          <span>刷新数据</span>
        </div>
        <div class="shortcut-item">
          <kbd>1</kbd>
          <span>切换到「全部」标签</span>
        </div>
        <div class="shortcut-item">
          <kbd>2</kbd>
          <span>切换到「AgentMemory」标签</span>
        </div>
        <div class="shortcut-item">
          <kbd>3</kbd>
          <span>切换到「Hermes Memory」标签</span>
        </div>
        <div class="shortcut-item">
          <kbd>?</kbd>
          <span>显示 / 隐藏此帮助</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUIStore } from '@/stores/ui'
const uiStore = useUIStore()
</script>

<style scoped>
.keyboard-help-overlay {
  position: fixed;
  inset: 0;
  background: var(--modal-backdrop);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.keyboard-help {
  background: var(--card);
  border-radius: 16px;
  padding: 32px;
  width: 90%;
  max-width: 400px;
}

h2 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 24px;
  text-align: center;
}

.shortcut-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.shortcut-item kbd {
  min-width: 48px;
  text-align: center;
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--tag-bg);
  color: var(--primary);
  font-size: 0.875rem;
  font-family: var(--font-mono);
  font-weight: 500;
}

.shortcut-item span {
  color: var(--text-secondary);
  font-size: 0.875rem;
}
</style>
