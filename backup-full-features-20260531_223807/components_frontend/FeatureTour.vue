<template>
  <div class="feature-tour">
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
.tour-step { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 10px; cursor: pointer; transition: all 0.2s; border: 2px solid transparent; }
.tour-step:hover { background: var(--card-bg, #f0f7ff); }
.tour-step.highlighted { border-color: #007aff; background: #f0f7ff; }
.feature-icon { font-size: 28px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; background: var(--card-bg, #f8f9fa); border-radius: 10px; }
.feature-name { font-weight: 600; font-size: 14px; }
.feature-desc { font-size: 12px; color: #666; margin-top: 2px; }
</style>

<style>
.tour-highlight-pulse { animation: tour-pulse 0.5s ease-in-out 3; }
@keyframes tour-pulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(0,122,255,0.4); } 50% { box-shadow: 0 0 0 8px rgba(0,122,255,0); } }
</style>
