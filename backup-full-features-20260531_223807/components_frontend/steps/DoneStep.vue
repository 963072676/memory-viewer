<template>
  <div class="done-step">
    <div class="done-icon">🎉</div>
    <h2>一切就绪！</h2>
    <p class="done-desc">你已掌握 Memory Viewer 的核心功能</p>
    <div class="quick-links">
      <div class="link-card" @click="$router.push('/agentmemory')">📝 浏览记忆</div>
      <div class="link-card" @click="$router.push('/dashboard')">📊 查看仪表盘</div>
      <div class="link-card" @click="$router.push('/conflicts')">⚠️ 检测冲突</div>
      <div class="link-card" @click="$router.push('/workflows')">⚙️ 设置自动化</div>
    </div>
    <p class="hint">随时可在设置中重新启动此向导</p>
  </div>
</template>

<style scoped>
.done-step { text-align: center; }
.done-icon { font-size: 64px; margin-bottom: 16px; }
.done-desc { color: #666; font-size: 16px; margin-bottom: 24px; }
.quick-links { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
.link-card { padding: 16px; background: var(--card-bg, #f8f9fa); border-radius: 12px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.2s; border: 2px solid transparent; }
.link-card:hover { border-color: #007aff; background: #f0f7ff; }
.hint { color: #999; font-size: 13px; }
</style>
