<template>
  <div class="preferences-step">
    <h3>🎨 {{ $t('i18n.personalized_settings') }}</h3>
    <div class="pref-list">
      <div class="pref-item">
        <div class="pref-label">{{ $t('i18n.theme') }}</div>
        <select v-model="theme" class="pref-select">
          <option value="light">☀️ {{ $t('i18n.light') }}</option>
          <option value="dark">🌙 {{ $t('i18n.dark') }}</option>
          <option value="auto">💻 {{ $t('i18n.system') }}</option>
        </select>
      </div>
      <div class="pref-item">
        <div class="pref-label">{{ $t('i18n.auto_refreshinterval') }}</div>
        <select v-model="refresh" class="pref-select">
          <option value="0">{{ $t('i18n.close') }}</option>
          <option value="15">每 15 {{ $t('i18n.min') }}</option>
          <option value="30">每 30 {{ $t('i18n.min') }}</option>
          <option value="60">{{ $t('i18n.every_hour') }}</option>
        </select>
      </div>
      <div class="pref-item">
        <div class="pref-label">{{ $t('i18n.default_view') }}</div>
        <select v-model="defaultView" class="pref-select">
          <option value="/">{{ $t('i18n.home') }}</option>
          <option value="/agentmemory">Agent 记忆</option>
          <option value="/dashboard">{{ $t('i18n.dashboard') }}</option>
          <option value="/graph">{{ $t('i18n.graph') }}</option>
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
