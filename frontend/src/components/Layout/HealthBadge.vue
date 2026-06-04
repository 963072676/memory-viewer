<template>
  <div class="health-badge" :class="colorClass" :title="tooltip">
    <svg :width="size" :height="size" viewBox="0 0 36 36" class="health-ring">
      <!-- Background ring -->
      <circle cx="18" cy="18" r="15.5" fill="none" stroke="var(--border)" stroke-width="3" />
      <!-- Progress ring -->
      <circle cx="18" cy="18" r="15.5" fill="none"
        :stroke="ringColor"
        stroke-width="3"
        stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        transform="rotate(-90 18 18)" />
    </svg>
    <span class="health-value">{{ score }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  score: number
  color: 'green' | 'yellow' | 'red'
}>()

// P45 r1: ring size 32px → 36px, 与 MemoryCard r15 strength ring 44px 形成
// "detail 缩小、list 主显" 的视觉等级。中心字号 0.55rem → 0.625rem 让数字更可读。
const size = 36
const radius = 15.5
const circumference = 2 * Math.PI * radius

const colorClass = computed(() => `health-${props.color}`)
// P45 r1: 6 处硬编码 hex (#22c55e / #eab308 / #ef4444 × SVG stroke + text) → 全站 token
// 之前 P36-P38 系列 sweep 漏了 HealthBadge, 导致 dark 模式 --health-* token 切换时
// 这里不会跟随. 现在统一, dark 模式下 3 档健康度颜色与全站 token 契约保持一致.
const ringColor = computed(() => {
  if (props.color === 'green') return 'var(--health-good)'
  if (props.color === 'yellow') return 'var(--health-warn)'
  return 'var(--health-bad)'
})

const dashOffset = computed(() => {
  const pct = Math.max(0, Math.min(100, props.score)) / 100
  return circumference * (1 - pct)
})

const tooltip = computed(() => `健康度: ${props.score}/100`)
</script>

<style scoped>
.health-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: relative;
  width: 36px;
  height: 36px;
  transition: transform 0.2s ease;
}

.health-badge:hover {
  transform: scale(1.1);
}

.health-ring {
  position: absolute;
  top: 0;
  left: 0;
  transition: stroke-dashoffset 0.6s ease;
}

.health-value {
  /* P45 r1: 0.55rem → 0.625rem — 32px ring 中心 0.55rem 数字在 chrome 12px 下渲染模糊,
     36px ring 配 0.625rem (10px) 仍紧凑但清晰可读. 数字仍占 ring 内圈 ~60% 宽度. */
  font-size: 0.625rem;
  font-weight: 700;
  color: var(--primary);
  z-index: 1;
  font-variant-numeric: tabular-nums;
  font-family: var(--font);
  letter-spacing: -0.02em;
}

/* P45 r1: text color 与 SVG stroke 同源 (--health-good/--health-warn/--health-bad),
   之前 #22c55e/#eab308/#ef4444 硬编码在 dark 模式不会跟随 token 翻转.
   现在用 var(--primary) 作 fallback: light 模式数字黑/白, color-override 来自 .health-* 类. */
.health-green .health-value { color: var(--health-good); }
.health-yellow .health-value { color: var(--health-warn); }
.health-red .health-value { color: var(--health-bad); }
</style>
