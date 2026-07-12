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
          ref="tooltipElement"
          class="tour-tooltip"
          :class="'tooltip-' + tooltipPlacement"
          :style="tooltipStyle"
        >
          <div class="tooltip-header">
            <span class="tooltip-icon">{{ currentStep.icon }}</span>
            <div class="tooltip-title-group">
              <div class="tooltip-step">第 {{ currentStepIndex + 1 }} / {{ steps.length }} 步</div>
              <div class="tooltip-title">{{ currentStep.title }}</div>
            </div>
            <button class="tooltip-close" aria-label="关闭引导" @click="skipTour">✕</button>
          </div>
          <div class="tooltip-body">
            {{ currentStep.description }}
          </div>
          <div class="tooltip-footer">
            <button class="btn-skip" @click="skipTour">{{ $t('i18n.onboarding.skip_tour') }}</button>
            <div class="nav-dots">
              <span
                v-for="(_, i) in steps"
                :key="i"
                class="dot"
                :class="{ active: i === currentStepIndex }"
              />
            </div>
            <div class="nav-btns">
              <button v-if="!isFirstStep" class="btn-nav" @click="goToPreviousStep">← {{ $t('i18n.common.back') }}</button>
              <button class="btn-nav btn-next" @click="goToNextStep">
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
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useOnboarding, type TourStep } from '@/composables/useOnboarding'
import {
  findAvailableStepIndex,
  resolveTooltipPosition,
  type TooltipPlacement,
} from '@/utils/onboarding-position'

const {
  steps,
  isActive,
  currentStepIndex,
  currentStep,
  isLastStep,
  isFirstStep,
  checkFirstVisit,
  startTour,
  skipTour,
  finishTour,
} = useOnboarding()

const spotlightTarget = ref<HTMLElement | null>(null)
const tooltipElement = ref<HTMLElement | null>(null)
const spotlightStyle = ref<Record<string, string>>({})
const tooltipStyle = ref<Record<string, string>>({ visibility: 'hidden' })
const tooltipPlacement = ref<TooltipPlacement>('bottom')

const LAYOUT_SETTLE_DELAY = 260
let positionFrame = 0
let positionSettleTimer: ReturnType<typeof setTimeout> | null = null
let startTimer: ReturnType<typeof setTimeout> | null = null
let positionRequestId = 0

function getVisibleTarget(step: TourStep) {
  const element = document.querySelector<HTMLElement>(step.target)
  if (!element) return null

  const rect = element.getBoundingClientRect()
  const style = window.getComputedStyle(element)
  if (
    rect.width <= 0 ||
    rect.height <= 0 ||
    style.display === 'none' ||
    style.visibility === 'hidden'
  ) {
    return null
  }

  return { element, rect }
}

function findVisibleStepIndex(startIndex: number, direction: 1 | -1) {
  return findAvailableStepIndex({
    startIndex,
    direction,
    totalSteps: steps.length,
    isAvailable: (index) => Boolean(getVisibleTarget(steps[index])),
  })
}

function goToNextStep() {
  const nextIndex = findVisibleStepIndex(currentStepIndex.value + 1, 1)
  if (nextIndex >= 0) {
    currentStepIndex.value = nextIndex
  } else {
    finishTour()
  }
}

function goToPreviousStep() {
  const previousIndex = findVisibleStepIndex(currentStepIndex.value - 1, -1)
  if (previousIndex >= 0) currentStepIndex.value = previousIndex
}

async function positionElements() {
  if (!isActive.value) return
  const requestId = ++positionRequestId
  await nextTick()
  if (!isActive.value || requestId !== positionRequestId) return

  const target = getVisibleTarget(currentStep.value)
  if (!target) {
    const nextIndex = findVisibleStepIndex(currentStepIndex.value + 1, 1)
    const fallbackIndex = nextIndex >= 0
      ? nextIndex
      : findVisibleStepIndex(currentStepIndex.value - 1, -1)

    if (fallbackIndex >= 0) {
      currentStepIndex.value = fallbackIndex
    } else {
      finishTour()
    }
    return
  }

  spotlightTarget.value = target.element
  spotlightStyle.value = {
    width: `${target.rect.width}px`,
    height: `${target.rect.height}px`,
    top: `${target.rect.top}px`,
    left: `${target.rect.left}px`,
  }

  await nextTick()
  if (!isActive.value || requestId !== positionRequestId || !tooltipElement.value) return

  const tooltipRect = tooltipElement.value.getBoundingClientRect()
  const resolved = resolveTooltipPosition({
    preferred: currentStep.value.position,
    target: target.rect,
    tooltip: tooltipRect,
    viewportWidth: window.innerWidth,
    viewportHeight: window.innerHeight,
  })
  tooltipPlacement.value = resolved.placement
  tooltipStyle.value = {
    top: `${resolved.top}px`,
    left: `${resolved.left}px`,
    transform: 'none',
    visibility: 'visible',
  }
}

function schedulePositionElements() {
  if (!isActive.value) return
  if (positionFrame) cancelAnimationFrame(positionFrame)
  positionFrame = requestAnimationFrame(() => {
    positionFrame = 0
    positionElements()
  })
}

function handleViewportResize() {
  schedulePositionElements()
  if (positionSettleTimer) clearTimeout(positionSettleTimer)
  positionSettleTimer = setTimeout(() => {
    positionSettleTimer = null
    schedulePositionElements()
  }, LAYOUT_SETTLE_DELAY)
}

watch([isActive, currentStepIndex], ([active]) => {
  tooltipStyle.value = { visibility: 'hidden' }
  if (!active) {
    positionRequestId++
    spotlightTarget.value = null
    return
  }
  schedulePositionElements()
})

// Click on highlighted element to advance — single watcher with proper cleanup
watch(spotlightTarget, (newEl, oldEl) => {
  if (oldEl) {
    oldEl.removeEventListener('click', handleSpotlightClick)
  }
  if (newEl) {
    newEl.addEventListener('click', handleSpotlightClick)
  }
})

function handleSpotlightClick() {
  goToNextStep()
}

// Auto-start on mount if first visit
onMounted(() => {
  window.addEventListener('resize', handleViewportResize, { passive: true })
  window.addEventListener('orientationchange', handleViewportResize, { passive: true })
  window.addEventListener('scroll', schedulePositionElements, { passive: true, capture: true })
  window.visualViewport?.addEventListener('resize', handleViewportResize, { passive: true })
  window.visualViewport?.addEventListener('scroll', schedulePositionElements, { passive: true })

  if (checkFirstVisit()) {
    startTimer = setTimeout(() => {
      startTour()
      schedulePositionElements()
    }, 500)
  }
})

onUnmounted(() => {
  positionRequestId++
  if (positionFrame) cancelAnimationFrame(positionFrame)
  if (positionSettleTimer) clearTimeout(positionSettleTimer)
  if (startTimer) clearTimeout(startTimer)
  spotlightTarget.value?.removeEventListener('click', handleSpotlightClick)
  window.removeEventListener('resize', handleViewportResize)
  window.removeEventListener('orientationchange', handleViewportResize)
  window.removeEventListener('scroll', schedulePositionElements, true)
  window.visualViewport?.removeEventListener('resize', handleViewportResize)
  window.visualViewport?.removeEventListener('scroll', schedulePositionElements)
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
  box-sizing: border-box;
  min-width: min(280px, calc(100vw - 24px));
  max-width: min(320px, calc(100vw - 24px));
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
  background: var(--accent-subtle);
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
  /* P45 r2: #999 → var(--text-tertiary). 之前硬编码 60% 灰, dark 模式不变,
     light 模式与系统灰基本一致但与 token 契约脱节. */
  color: var(--text-tertiary);
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
  /* P45 r2: #ddd → var(--border). */
  background: var(--border);
}

.dot.active {
  /* P45 r2: #007aff → var(--accent). */
  background: var(--accent);
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
  background: var(--bg-recessed);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-nav:hover {
  background: var(--border, #e0e0e0);
}

.btn-next {
  /* P45 r2: #007aff / white → var(--accent) / var(--card). 与 P38 r17/r33 决策一致,
     这次扩展到 OnboardingTour 内的 "下一步" 按钮. 之前 OnboardingTour 漏了
     token sweep, 现在统一. */
  background: var(--accent);
  color: var(--card);
  border: none;
}

.btn-next:hover {
  /* P45 r2: #0066dd → color-mix(--accent 88%, --primary 12%). 与 P44 SettingsView
     决策同源 (SettingsView btn hover 也用 12% 黑色混合 → "深蓝" hover). */
  background: color-mix(in srgb, var(--accent) 88%, var(--primary) 12%);
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
