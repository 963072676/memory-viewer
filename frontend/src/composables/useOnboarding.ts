import { ref, computed } from 'vue'

const STORAGE_KEY = 'memory-viewer-onboarding-done'

export interface TourStep {
  id: string
  icon: string
  title: string
  description: string
  target: string // CSS selector or data attribute
  position: 'top' | 'bottom' | 'left' | 'right'
}

const steps: TourStep[] = [
  {
    id: 'search',
    icon: '🔍',
    title: '智能搜索',
    description: '支持关键词、语义和自然语言三种搜索模式',
    target: '.search-bar',
    position: 'bottom',
  },
  {
    id: 'dashboard',
    icon: '📊',
    title: '统计仪表盘',
    description: '可视化记忆分布、健康度和趋势分析',
    target: '[data-tour="/dashboard"]',
    position: 'right',
  },
  {
    id: 'graph',
    icon: '🕸️',
    title: '记忆图谱',
    description: '可视化记忆关联关系',
    target: '[data-tour="/graph"]',
    position: 'right',
  },
  {
    id: 'collections',
    icon: '📚',
    title: 'Collections',
    description: '智能分类和集合管理',
    target: '[data-tour="/collections"]',
    position: 'right',
  },
  {
    id: 'sources',
    icon: '🔌',
    title: '记忆源配置',
    description: '管理记忆数据源和连接设置',
    target: '[data-tour="/sources"]',
    position: 'left',
  },
  {
    id: 'shortcuts',
    icon: '⚡',
    title: '快捷命令',
    description: '按 / 聚焦搜索框，快速访问所有功能',
    target: '.app-header',
    position: 'bottom',
  },
]

const isActive = ref(false)
const currentStepIndex = ref(0)
const hasSeenOnboarding = ref(false)

export function useOnboarding() {
  function checkFirstVisit() {
    const done = localStorage.getItem(STORAGE_KEY)
    if (done) {
      hasSeenOnboarding.value = true
      return false
    }
    return true
  }

  function startTour() {
    currentStepIndex.value = 0
    isActive.value = true
    hasSeenOnboarding.value = true
  }

  function nextStep() {
    if (currentStepIndex.value < steps.length - 1) {
      currentStepIndex.value++
    } else {
      finishTour()
    }
  }

  function prevStep() {
    if (currentStepIndex.value > 0) {
      currentStepIndex.value--
    }
  }

  function skipTour() {
    localStorage.setItem(STORAGE_KEY, 'skipped')
    isActive.value = false
  }

  function finishTour() {
    localStorage.setItem(STORAGE_KEY, 'true')
    isActive.value = false
    hasSeenOnboarding.value = true
  }

  function replayTour() {
    localStorage.removeItem(STORAGE_KEY)
    startTour()
  }

  const currentStep = computed(() => steps[currentStepIndex.value])
  const progress = computed(() => ((currentStepIndex.value + 1) / steps.length) * 100)
  const isLastStep = computed(() => currentStepIndex.value === steps.length - 1)
  const isFirstStep = computed(() => currentStepIndex.value === 0)

  return {
    steps,
    isActive,
    currentStepIndex,
    currentStep,
    progress,
    isLastStep,
    isFirstStep,
    hasSeenOnboarding,
    checkFirstVisit,
    startTour,
    nextStep,
    prevStep,
    skipTour,
    finishTour,
    replayTour,
  }
}