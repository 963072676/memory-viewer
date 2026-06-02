<template>
  <div class="welcome-step">
    <div class="welcome-icon">🧠</div>
    <h2>欢迎使用 Memory Viewer v2</h2>
    <p class="welcome-desc">智能记忆管理平台 — 帮助你理解、组织和优化 Agent 记忆系统</p>
    <div class="feature-grid">
      <div class="feature-item"><span>🔍</span> 智能搜索 & 自然语言查询</div>
      <div class="feature-item"><span>🕸️</span> 记忆图谱 & 聚类分析</div>
      <div class="feature-item"><span>⚠️</span> 冲突检测 & 异常告警</div>
      <div class="feature-item"><span>⚙️</span> 自动化工作流</div>
    </div>
    <p class="welcome-hint">接下来几个步骤将帮助你快速上手</p>
  </div>
</template>

<style scoped>
.welcome-step { text-align: center; }
.welcome-icon { font-size: 64px; margin-bottom: 16px; }
.welcome-desc { color: #666; font-size: 16px; margin-bottom: 24px; }
.feature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px; }
.feature-item { padding: 12px; background: var(--card-bg, #f8f9fa); border-radius: 10px; font-size: 14px; text-align: left; }
.feature-item span { margin-right: 8px; }
.welcome-hint { color: #999; font-size: 13px; }
</style>
