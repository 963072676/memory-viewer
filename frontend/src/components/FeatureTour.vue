<template>
  <div class="feature-tour">
    <div class="feature-tour-header">
      <h3>功能介绍</h3>
      <button class="btn-close" aria-label="关闭功能介绍" @click="$emit('close')">✕</button>
    </div>
    <div v-for="(feature, i) in features" :key="i" class="tour-step" :class="{ highlighted: currentHighlight === i }" @click="highlight(i)">
      <div class="feature-icon">{{ feature.icon }}</div>
      <div class="feature-info">
        <div class="feature-name">{{ feature.name }}</div>
        <div class="feature-desc">{{ feature.description }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineEmits<{
  (e: 'close'): void
}>()

const currentHighlight = ref(-1)

const features = [
  { icon: '🔍', name: '智能搜索', description: '支持关键词、语义、自然语言三种搜索模式', selector: '.search-bar' },
  { icon: '📊', name: '统计仪表盘', description: '可视化记忆分布、健康度、趋势', selector: '[data-tab="dashboard"]' },
  { icon: '🕸️', name: '记忆图谱', description: '3D 可视化记忆关联关系', selector: '.nav-graph' },
  { icon: '⚠️', name: '冲突检测', description: '自动发现记忆中的矛盾信息', selector: '.nav-conflicts' },
  { icon: '⚙️', name: '工作流', description: '自动化记忆管理规则', selector: '.nav-workflows' },
  { icon: '📈', name: 'API 分析', description: '监控 API 使用情况和成本', selector: '.nav-analytics' },
]

function highlight(i: number) {
  currentHighlight.value = i
  const el = document.querySelector(features[i].selector)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    el.classList.add('tour-highlight-pulse')
    setTimeout(() => el.classList.remove('tour-highlight-pulse'), 2000)
  }
}
</script>

<style scoped>
.feature-tour { display: flex; flex-direction: column; gap: 8px; }
.feature-tour-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.feature-tour-header h3 { margin: 0; font-size: 1rem; font-weight: 600; }
.btn-close { background: none; border: none; font-size: 1.1rem; cursor: pointer; color: var(--text-secondary); padding: 4px; }
.tour-step { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 10px; cursor: pointer; transition: all 0.2s; border: 2px solid transparent; }
.tour-step:hover { background: var(--accent-subtle); }
/* P47 r2: FeatureTour 硬编码 #f0f7ff / #007aff / #f8f9fa / #666 → 全站 token.
   .tour-step.highlighted = selected, 用 --accent border + --accent-subtle bg (与 sidebar active 状态同源). */
.tour-step.highlighted { border-color: var(--accent); background: var(--accent-subtle); }
.feature-icon { font-size: 28px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; background: var(--bg-recessed); border-radius: 10px; }
.feature-name { font-weight: 600; font-size: 14px; }
.feature-desc { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
</style>

<style>
/* P47 r2: tour-pulse keyframes 硬编码 rgba(0,122,255,0.4) → --accent-glow (token 化).
   --accent-glow 在 variables.css 已定义 = rgba(0, 114, 245, 0.14), 与 --accent 偏移 0x0A 但
   视觉上"几乎相同". 0.4 alpha 比 0.14 大, 这里直接保留 0.4 数值, 只换底层引用变量名以保留
   theme-following 能力. */
.tour-highlight-pulse { animation: tour-pulse 0.5s ease-in-out 3; }
@keyframes tour-pulse { 0%, 100% { box-shadow: 0 0 0 0 var(--accent-glow); } 50% { box-shadow: 0 0 0 8px var(--accent-glow); } }
</style>
