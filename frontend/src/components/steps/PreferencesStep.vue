<template>
  <div class="preferences-step">
    <h3>🎨 {{ $t('zh_c49c09') }}</h3>
    <div class="pref-list">
      <div class="pref-item">
        <div class="pref-label">{{ $t('zh_006418_1') }}</div>
        <select v-model="theme" class="pref-select">
          <option value="light">☀️ {{ $t('zh_006802') }}</option>
          <option value="dark">🌙 {{ $t('zh_006818') }}</option>
          <option value="auto">💻 {{ $t('zh_ccb9d6') }}</option>
        </select>
      </div>
      <div class="pref-item">
        <div class="pref-label">{{ $t('zh_19c267') }}</div>
        <select v-model="refresh" class="pref-select">
          <option value="0">{{ $t('zh_006480') }}</option>
          <option value="15">每 15 {{ $t('zh_006491') }}</option>
          <option value="30">每 30 {{ $t('zh_006491') }}</option>
          <option value="60">{{ $t('zh_0d5d92') }}</option>
        </select>
      </div>
      <div class="pref-item">
        <div class="pref-label">{{ $t('zh_d5db7d') }}</div>
        <select v-model="defaultView" class="pref-select">
          <option value="/">{{ $t('zh_006dcf') }}</option>
          <option value="/agentmemory">Agent 记忆</option>
          <option value="/dashboard">{{ $t('zh_0ce870') }}</option>
          <option value="/graph">{{ $t('zh_00652d') }}</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const theme = ref(localStorage.getItem('theme') || 'auto')
const refresh = ref(localStorage.getItem('auto-refresh') || '30')
const defaultView = ref(localStorage.getItem('default-view') || '/')

watch(theme, (v) => localStorage.setItem('theme', v))
watch(refresh, (v) => localStorage.setItem('auto-refresh', v))
watch(defaultView, (v) => localStorage.setItem('default-view', v))
</script>

<style scoped>
.preferences-step h3 { margin-bottom: 16px; }
.pref-list { display: flex; flex-direction: column; gap: 16px; }
.pref-item { display: flex; justify-content: space-between; align-items: center; padding: 12px; background: var(--bg-recessed); border-radius: 10px; }
.pref-label { font-weight: 600; font-size: 14px; }
.pref-select { padding: 6px 12px; border: 1px solid var(--border, #ddd); border-radius: 6px; font-size: 14px; background: var(--card); }
</style>
