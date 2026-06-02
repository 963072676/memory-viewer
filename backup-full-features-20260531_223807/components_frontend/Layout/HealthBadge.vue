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

const size = 32
const radius = 15.5
const circumference = 2 * Math.PI * radius

const colorClass = computed(() => `health-${props.color}`)
const ringColor = computed(() => {
  if (props.color === 'green') return '#22c55e'
  if (props.color === 'yellow') return '#eab308'
  return '#ef4444'
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
  width: 32px;
  height: 32px;
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
  font-size: 0.55rem;
  font-weight: 700;
  color: var(--primary);
  z-index: 1;
}

.health-green .health-value { color: #22c55e; }
.health-yellow .health-value { color: #eab308; }
.health-red .health-value { color: #ef4444; }
</style>
