<template>
  <div class="health-gauge" :class="colorClass">
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
      <!-- Background circle -->
      <circle
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        :stroke="bgStroke"
        :stroke-width="strokeWidth"
      />
      <!-- Progress arc -->
      <circle
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        :stroke="gaugeColor"
        :stroke-width="strokeWidth"
        stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        :transform="`rotate(-90 ${center} ${center})`"
        class="progress-ring"
      />
    </svg>
    <div class="gauge-content">
      <span class="gauge-score">{{ score }}</span>
      <span class="gauge-label">{{ label }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  score: number
  size?: number
  strokeWidth?: number
  label?: string
}>(), {
  size: 160,
  strokeWidth: 12,
  label: 'Health Score',
})

const center = computed(() => props.size / 2)
const radius = computed(() => (props.size - props.strokeWidth) / 2 - 4)
const circumference = computed(() => 2 * Math.PI * radius.value)

const normalizedScore = computed(() => Math.max(0, Math.min(100, props.score)))

const dashOffset = computed(() => {
  const pct = normalizedScore.value / 100
  return circumference.value * (1 - pct)
})

const gaugeColor = computed(() => {
  if (normalizedScore.value >= 80) return '#22c55e'
  if (normalizedScore.value >= 50) return '#eab308'
  return '#ef4444'
})

const colorClass = computed(() => {
  if (normalizedScore.value >= 80) return 'gauge-green'
  if (normalizedScore.value >= 50) return 'gauge-yellow'
  return 'gauge-red'
})

const bgStroke = computed(() => 'var(--border)')
</script>

<style scoped>
.health-gauge {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

svg {
  display: block;
}

.progress-ring {
  transition: stroke-dashoffset 0.8s ease-in-out, stroke 0.3s;
}

.gauge-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.gauge-score {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
}

.gauge-green .gauge-score { color: #22c55e; }
.gauge-yellow .gauge-score { color: #eab308; }
.gauge-red .gauge-score { color: #ef4444; }

.gauge-label {
  font-size: 0.65rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
}
</style>
