<template>
  <Teleport to="body">
    <transition name="tour-fade">
      <div v-if="isActive" class="onboarding-tour-overlay" @click.self="skipTour">
        <!-- Spotlight highlight -->
        <div
          v-if="spotlightTarget"
          class="tour-spotlight"
          :class="'position-' + currentStep.position"
          :style="spotlightStyle"
        >
          <div class="spotlight-gap" />
        </div>

        <!-- Tour tooltip -->
        <div
          v-if="spotlightTarget"
          class="tour-tooltip"
          :class="'tooltip-' + currentStep.position"
          :style="tooltipStyle"
        >
          <div class="tooltip-header">
            <span class="tooltip-icon">{{ currentStep.icon }}</span>
            <div class="tooltip-title-group">
              <div class="tooltip-step">第 {{ currentStepIndex + 1 }} / {{ steps.length }} 步</div>
              <div class="tooltip-title">{{ currentStep.title }}</div>
            </div>
            <button class="tooltip-close" @click="skipTour">✕</button>
          </div>
          <div class="tooltip-body">
            {{ currentStep.description }}
          </div>
          <div class="tooltip-footer">
            <button class="btn-skip" @click="skipTour">跳过引导</button>
            <div class="nav-dots">
              <span
                v-for="(_, i) in steps"
                :key="i"
                class="dot"
                :class="{ active: i === currentStepIndex }"
              />
            </div>
            <div class="nav-btns">
              <button v-if="!isFirstStep" class="btn-nav" @click="prevStep">← 上一步</button>
              <button class="btn-nav btn-next" @click="nextStep">
                {{ isLastStep ? '完成' : '下一步 →' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { useOnboarding } from '@/composables/useOnboarding'

const {
  steps,
  isActive,
  currentStepIndex,
  currentStep,
  isLastStep,
  isFirstStep,
  checkFirstVisit,
  nextStep,
  prevStep,
  skipTour,
  finishTour,
} = useOnboarding()

const spotlightTarget = ref<HTMLElement | null>(null)
const spotlightStyle = ref<Record<string, string>>({})
const tooltipStyle = ref<Record<string, string>>({})

const TOOLTIP_MARGIN = 16

function positionElements() {
  if (!isActive.value) return
  nextTick(() => {
    const targetEl = document.querySelector(currentStep.value.target)
    if (!targetEl) {
      spotlightTarget.value = null
      return
    }
    spotlightTarget.value = targetEl as HTMLElement
    const rect = targetEl.getBoundingClientRect()
    const vw = window.innerWidth
    const vh = window.innerHeight

    // Spotlight: highlight box around target with dark overlay around it
    spotlightStyle.value = {
      width: `${rect.width}px`,
      height: `${rect.height}px`,
      top: `${rect.top}px`,
      left: `${rect.left}px`,
    }

    // Tooltip: position relative to target based on step position
    let ts: Record<string, string> = {}
    switch (currentStep.value.position) {
      case 'bottom':
        ts = {
          top: `${rect.bottom + TOOLTIP_MARGIN}px`,
          left: `${rect.left + rect.width / 2}px`,
          transform: 'translateX(-50%)',
        }
        break
      case 'top':
        ts = {
          bottom: `${vh - rect.top + TOOLTIP_MARGIN}px`,
          left: `${rect.left + rect.width / 2}px`,
          transform: 'translateX(-50%)',
        }
        break
      case 'right':
        ts = {
          top: `${rect.top + rect.height / 2}px`,
          left: `${rect.right + TOOLTIP_MARGIN}px`,
          transform: 'translateY(-50%)',
        }
        break
      case 'left':
        ts = {
          top: `${rect.top + rect.height / 2}px`,
          right: `${vw - rect.left + TOOLTIP_MARGIN}px`,
          transform: 'translateY(-50%)',
        }
        break
    }
    tooltipStyle.value = ts
  })
}

watch([isActive, currentStepIndex], () => {
  positionElements()
})

// Click on highlighted element to advance
watch(spotlightTarget, (el) => {
  if (el) {
    el.addEventListener('click', handleSpotlightClick)
  }
})

function handleSpotlightClick() {
  nextStep()
}

watch(() => spotlightTarget.value, (el) => {
  if (el) {
    el.removeEventListener('click', handleSpotlightClick)
  }
})

// Auto-start on mount if first visit
import { onMounted } from 'vue'
onMounted(() => {
  if (checkFirstVisit()) {
    // Delay slightly to let app render
    setTimeout(() => {
      isActive.value = true
      positionElements()
    }, 500)
  }
})
</script>

<style scoped>
.onboarding-tour-overlay {
  position: fixed;
  inset: 0;
  z-index: 9998;
  pointer-events: none;
}

.tour-spotlight {
  position: fixed;
  border-radius: 12px;
  box-shadow: 0 0 0 9999px var(--modal-backdrop);
  pointer-events: auto;
  transition: all 0.3s ease;
}

.spotlight-gap {
  /* The gap is the transparent area showing the target */
}

.tour-tooltip {
  position: fixed;
  background: var(--card, #fff);
  border-radius: 16px;
  padding: 16px 20px;
  min-width: 280px;
  max-width: 320px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
  pointer-events: auto;
  z-index: 9999;
}

.tooltip-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.tooltip-icon {
  font-size: 32px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--card-bg, #f0f7ff);
  border-radius: 12px;
}

.tooltip-title-group {
  flex: 1;
}

.tooltip-step {
  font-size: 11px;
  color: #999;
  margin-bottom: 2px;
}

.tooltip-title {
  font-weight: 700;
  font-size: 16px;
  color: var(--text, #1a1a1a);
}

.tooltip-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #999;
  cursor: pointer;
  padding: 4px;
}

.tooltip-body {
  font-size: 14px;
  color: #555;
  line-height: 1.5;
  margin-bottom: 16px;
}

.tooltip-footer {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-skip {
  background: none;
  border: none;
  color: #999;
  font-size: 13px;
  cursor: pointer;
  padding: 4px 8px;
}

.nav-dots {
  display: flex;
  gap: 4px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ddd;
}

.dot.active {
  background: #007aff;
  width: 18px;
  border-radius: 3px;
}

.nav-btns {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.btn-nav {
  padding: 6px 16px;
  border-radius: 8px;
  border: 1px solid var(--border, #e0e0e0);
  background: var(--card-bg, #f8f9fa);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-nav:hover {
  background: var(--border, #e0e0e0);
}

.btn-next {
  background: #007aff;
  color: white;
  border: none;
}

.btn-next:hover {
  background: #0066dd;
}

/* Transitions */
.tour-fade-enter-active,
.tour-fade-leave-active {
  transition: opacity 0.3s ease;
}

.tour-fade-enter-from,
.tour-fade-leave-to {
  opacity: 0;
}
</style>