<template>
  <div class="preferences-step">
    <h3>🎨 个性化设置</h3>
    <div class="pref-list">
      <div class="pref-item">
        <div class="pref-label">主题</div>
        <select v-model="theme" class="pref-select">
          <option value="light">☀️ 浅色</option>
          <option value="dark">🌙 深色</option>
          <option value="auto">💻 跟随系统</option>
        </select>
      </div>
      <div class="pref-item">
        <div class="pref-label">自动刷新间隔</div>
        <select v-model="refresh" class="pref-select">
          <option value="0">关闭</option>
          <option value="15">每 15 分钟</option>
          <option value="30">每 30 分钟</option>
          <option value="60">每小时</option>
        </select>
      </div>
      <div class="pref-item">
        <div class="pref-label">默认视图</div>
        <select v-model="defaultView" class="pref-select">
          <option value="/">首页</option>
          <option value="/agentmemory">Agent 记忆</option>
          <option value="/dashboard">仪表盘</option>
          <option value="/graph">图谱</option>
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
.pref-item { display: flex; justify-content: space-between; align-items: center; padding: 12px; background: var(--card-bg, #f8f9fa); border-radius: 10px; }
.pref-label { font-weight: 600; font-size: 14px; }
.pref-select { padding: 6px 12px; border: 1px solid var(--border, #ddd); border-radius: 6px; font-size: 14px; background: var(--card-bg, #fff); }
</style>
