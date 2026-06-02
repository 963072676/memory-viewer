<template>
  <div v-if="visible" class="setup-wizard-overlay">
    <div class="wizard-container">
      <!-- Progress -->
      <div class="wizard-progress">
        <div v-for="(step, i) in steps" :key="i" class="step-dot" :class="{ active: i === currentStep, done: i < currentStep }">
          <span class="dot-number">{{ i < currentStep ? '✓' : i + 1 }}</span>
          <span class="dot-label">{{ step.title }}</span>
        </div>
      </div>

      <!-- Step Content -->
      <div class="wizard-content">
        <component :is="steps[currentStep].component" @skip="skip" />
      </div>

      <!-- Navigation -->
      <div class="wizard-nav">
        <button v-if="currentStep > 0" class="btn-prev" @click="prev">← 上一步</button>
        <div class="nav-spacer" />
        <button class="btn-skip" @click="skip">跳过</button>
        <button v-if="currentStep < steps.length - 1" class="btn-next" @click="next">下一步 →</button>
        <button v-else class="btn-finish" @click="finish">🎉 开始使用</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, markRaw } from 'vue'
import WelcomeStep from './steps/WelcomeStep.vue'
import ConfigStep from './steps/ConfigStep.vue'
import ImportStep from './steps/ImportStep.vue'
import PreferencesStep from './steps/PreferencesStep.vue'
import DoneStep from './steps/DoneStep.vue'

const visible = ref(false)
const currentStep = ref(0)

const steps = [
  { title: '连接', component: markRaw(ConfigStep) },
  { title: '导入', component: markRaw(ImportStep) },
  { title: '偏好', component: markRaw(PreferencesStep) },
  { title: '完成', component: markRaw(DoneStep) },
]

onMounted(async () => {
  const done = localStorage.getItem('setup-wizard-done')
  if (done) return
  // Auto-skip if backend already has configured sources
  try {
    const res = await fetch('/api/sources')
    const data = await res.json()
    if (data.sources && data.sources.length > 0 && data.sources.some((s: any) => s.count > 0)) {
      localStorage.setItem('setup-wizard-done', 'auto')
      return
    }
  } catch { /* ignore */ }
  visible.value = true
})

function next() {
  if (currentStep.value < steps.length - 1) currentStep.value++
}

function prev() {
  if (currentStep.value > 0) currentStep.value--
}

function skip() {
  visible.value = false
  localStorage.setItem('setup-wizard-done', 'skipped')
}

function finish() {
  visible.value = false
  localStorage.setItem('setup-wizard-done', 'true')
}

// Expose restart method
defineExpose({ restart: () => { currentStep.value = 0; visible.value = true } })
</script>

<style scoped>
.setup-wizard-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 2000; backdrop-filter: blur(4px); }
.wizard-container { background: var(--card-bg, #fff); border-radius: 20px; width: 90%; max-width: 640px; max-height: 85vh; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
.wizard-progress { display: flex; justify-content: center; gap: 24px; padding: 20px 20px 12px; border-bottom: 1px solid var(--border, #eee); }
.step-dot { display: flex; flex-direction: column; align-items: center; gap: 4px; opacity: 0.4; transition: all 0.3s; }
.step-dot.active { opacity: 1; }
.step-dot.done { opacity: 0.7; }
.dot-number { width: 28px; height: 28px; border-radius: 50%; background: #e0e0e0; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; }
.step-dot.active .dot-number { background: #007aff; color: white; }
.step-dot.done .dot-number { background: #34c759; color: white; }
.dot-label { font-size: 11px; color: #666; }
.wizard-content { flex: 1; padding: 24px; overflow-y: auto; }
.wizard-nav { display: flex; align-items: center; padding: 16px 24px; border-top: 1px solid var(--border, #eee); gap: 12px; }
.nav-spacer { flex: 1; }
.btn-prev, .btn-skip, .btn-next, .btn-finish { padding: 8px 20px; border-radius: 8px; font-size: 14px; cursor: pointer; border: none; }
.btn-prev { background: var(--card-bg, #f0f0f0); color: #333; border: 1px solid var(--border, #ddd); }
.btn-skip { background: none; color: #999; }
.btn-next { background: #007aff; color: white; }
.btn-finish { background: #34c759; color: white; font-weight: 600; }
</style>
