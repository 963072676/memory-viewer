<template>
  <div class="keyboard-help-overlay" @click.self="uiStore.toggleKeyboardHelp()">
    <div class="keyboard-help">
      <h2>{{ $t('zh_d65312') }}</h2>
      <div class="shortcut-list">
        <div class="shortcut-item">
          <kbd>{{ $t('en_ctrl_k') }}</kbd>
          <span>{{ $t('zh_49d894') }}</span>
        </div>
        <div class="shortcut-item">
          <kbd>/</kbd>
          <span>{{ $t('zh_5a6229') }}</span>
        </div>
        <div class="shortcut-item">
          <kbd>{{ $t('en_esc') }}</kbd>
          <span>{{ $t('zh_bb3e9f') }} / {{ $t('zh_ab9156') }}</span>
        </div>
        <div class="shortcut-item">
          <kbd>R</kbd>
          <span>{{ $t('zh_ab3052') }}</span>
        </div>
        <div class="shortcut-item">
          <kbd>1</kbd>
          <span>{{ $t('zh_0cf0c4') }}「{{ $t('zh_006479') }}」{{ $t('zh_00674e') }}</span>
        </div>
        <div class="shortcut-item">
          <kbd>2</kbd>
          <span>{{ $t('zh_0cf0c4') }}「AgentMemory」{{ $t('zh_00674e') }}</span>
        </div>
        <div class="shortcut-item">
          <kbd>3</kbd>
          <span>{{ $t('zh_0cf0c4') }}「Hermes Memory」{{ $t('zh_00674e') }}</span>
        </div>
        <div class="shortcut-item">
          <kbd>?</kbd>
          <span>{{ $t('zh_006711') }} / {{ $t('zh_f7bd91') }}</span>
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
