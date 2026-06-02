<template>
  <div class="decay-chart" v-if="data">
    <div class="chart-header">
      <span class="chart-title">📉 衰减曲线</span>
      <span v-if="data.current_strength <= 0" class="forgotten-badge">已遗忘</span>
    </div>
    <svg :viewBox="`0 0 ${svgW} ${svgH}`" class="chart-svg">
      <!-- Grid lines -->
      <line v-for="i in 4" :key="'g'+i"
        :x1="padL" :y1="padT + (i * (chartH / 4))"
        :x2="svgW - padR" :y2="padT + (i * (chartH / 4))"
        stroke="var(--border)" stroke-width="0.5" />
      <!-- Y axis labels -->
      <text v-for="i in 5" :key="'yl'+i"
        :x="padL - 4" :y="padT + ((5-i) * chartH / 4) + 3"
        class="axis-label" text-anchor="end">{{ Math.round(i * 2) }}</text>
      <!-- Decay line -->
      <polyline
        :points="polylinePoints"
        fill="none" stroke="var(--accent)" stroke-width="1.5"
        stroke-linejoin="round" />
      <!-- Current position marker -->
      <circle
        :cx="currentX" :cy="currentY"
        r="4" fill="var(--accent)" stroke="white" stroke-width="1.5" />
      <!-- Zero line label -->
      <text :x="svgW - padR + 2" :y="zeroY + 3" class="axis-label">0</text>
    </svg>
    <div class="chart-footer">
      <span>当前: {{ data.current_strength.toFixed(1) }}</span>
      <span v-if="data.predicted_zero_date">预计归零: {{ data.predicted_zero_date }}</span>
      <span v-else>已遗忘</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DecayResponse } from '@/types'

const props = defineProps<{
  data: DecayResponse
}>()

const svgW = 260
const svgH = 100
const padL = 24
const padR = 10
const padT = 8
const padB = 16
const chartW = svgW - padL - padR
const chartH = svgH - padT - padB

const maxStrength = computed(() => props.data.initial_strength || 10)
const curveLen = computed(() => props.data.decay_curve.length)

const zeroY = computed(() => padT + chartH)

const polylinePoints = computed(() => {
  const pts = props.data.decay_curve.map((pt, i) => {
    const x = padL + (i / Math.max(curveLen.value - 1, 1)) * chartW
    const y = padT + chartH - (pt.strength / maxStrength.value) * chartH
    return `${x},${y}`
  })
  return pts.join(' ')
})

const currentX = computed(() => {
  const dayIdx = props.data.days_since_created
  const totalDays = curveLen.value - 1
  if (totalDays <= 0) return padL
  const idx = Math.min(dayIdx, totalDays)
  return padL + (idx / totalDays) * chartW
})

const currentY = computed(() => {
  return padT + chartH - (props.data.current_strength / maxStrength.value) * chartH
})
</script>

<style scoped>
.decay-chart {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.chart-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary);
}

.forgotten-badge {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 8px;
  background: #fee2e2;
  color: #dc2626;
}

.chart-svg {
  width: 100%;
  height: auto;
  display: block;
}

.axis-label {
  font-size: 7px;
  fill: var(--text-secondary);
  font-family: var(--font);
}

.chart-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.65rem;
  color: var(--text-secondary);
  margin-top: 6px;
}
</style>
