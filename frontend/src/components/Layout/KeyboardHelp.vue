<template>
  <div class="keyboard-help-overlay" @click.self="uiStore.toggleKeyboardHelp()">
    <div class="keyboard-help">
      <h2>{{ $t('i18n.help.shortcuts') }}</h2>
      <div class="shortcut-list">
        <div class="shortcut-item">
          <kbd>{{ $t('en_ctrl_k') }}</kbd>
          <span>{{ $t('i18n.open_command') }}</span>
        </div>
        <div class="shortcut-item">
          <kbd>/</kbd>
          <span>{{ $t('i18n.focus_search') }}</span>
        </div>
        <div class="shortcut-item">
          <kbd>{{ $t('en_esc') }}</kbd>
          <span>{{ $t('i18n.clear_search') }} / {{ $t('i18n.close_dialog') }}</span>
        </div>
        <div class="shortcut-item">
          <kbd>R</kbd>
          <span>{{ $t('i18n.refresh_data') }}</span>
        </div>
        <div class="shortcut-item">
          <kbd>1</kbd>
          <span>{{ $t('i18n.switch') }}「{{ $t('i18n.all') }}」{{ $t('i18n.label') }}</span>
        </div>
        <div class="shortcut-item">
          <kbd>2</kbd>
          <span>{{ $t('i18n.switch') }}「AgentMemory」{{ $t('i18n.label') }}</span>
        </div>
        <div class="shortcut-item">
          <kbd>3</kbd>
          <span>{{ $t('i18n.switch') }}「Hermes Memory」{{ $t('i18n.label') }}</span>
        </div>
        <div class="shortcut-item">
          <kbd>?</kbd>
          <span>{{ $t('i18n.show') }} / {{ $t('i18n.hide_help') }}</span>
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
