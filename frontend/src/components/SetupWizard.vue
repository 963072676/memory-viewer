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
        <button v-if="currentStep > 0" class="btn-prev" @click="prev">← {{ $t('zh_0cdd24') }}</button>
        <div class="nav-spacer" />
        <button class="btn-skip" @click="skip">{{ $t('zh_006c46') }}</button>
        <button v-if="currentStep < steps.length - 1" class="btn-next" @click="next">{{ $t('zh_0cdd29') }} →</button>
        <button v-else class="btn-finish" @click="finish">🎉 {{ $t('zh_b1fdbb') }}</button>
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
/* P46: SetupWizard 颜色 token 化 + dark mode 适配 — 旧实现 10+ 处硬编码 hex (Apple #007aff/#34c759/#e0e0e0/#666/#333/#999/#fff/#ddd/#f0f0f0) + rgba(0,0,0,0.6) 遮罩，dark 模式 0% 覆盖（首装用户在 dark 主题首次打开会看到亮色 wizard）。
   替换策略：
   - #e0e0e0 (inactive step dot) → var(--tag-bg)（与全站非活跃/无填充背景一致）
   - #007aff (active step) → var(--accent)（与全站蓝统一 — 之前是 Apple system 蓝，与项目 --accent #0072f5 略有色差）
   - #34c759 (done step) → var(--success)（与全站成功色统一）
   - "color: white" (on-accent) → var(--card)（on-accent 文字 token 决策树第 7 个文件，与 P45 r2 同源）
   - #666 (dot label) → var(--text-secondary)（让步骤标签在 dark 模式可读）
   - #f0f0f0 (btn-prev bg) → var(--tag-bg)（与 disabled/secondary 按钮背景一致）
   - #333 (btn-prev text) → var(--text-primary)（在 dark 模式自动反转为 #fafafa）
   - #ddd (btn-prev border) → var(--border)（dark 模式 #ebebeb → #2a2a2a）
   - #999 (btn-skip) → var(--text-tertiary)（与全站弱化文字一致）
   - rgba(0,0,0,0.6) (overlay) → var(--modal-backdrop)（自动 dark 模式 0.5 → 0.7）
   - var(--card-bg, #fff) 硬编码 fallback 全部删除（变量已在 :root 和 [data-theme='dark'] 都定义）
   - var(--border, #eee) / var(--border, #ddd) 硬编码 fallback 全部删除 */
.setup-wizard-overlay { position: fixed; inset: 0; background: var(--modal-backdrop); display: flex; align-items: center; justify-content: center; z-index: 2000; backdrop-filter: blur(4px); }
.wizard-container { background: var(--card); border-radius: 20px; width: 90%; max-width: 640px; max-height: 85vh; display: flex; flex-direction: column; overflow: hidden; box-shadow: var(--shadow-modal); }
.wizard-progress { display: flex; justify-content: center; gap: 24px; padding: 20px 20px 12px; border-bottom: 1px solid var(--border); }
.step-dot { display: flex; flex-direction: column; align-items: center; gap: 4px; opacity: 0.4; transition: all 0.3s; }
.step-dot.active { opacity: 1; }
.step-dot.done { opacity: 0.7; }
.dot-number { width: 28px; height: 28px; border-radius: 50%; background: var(--tag-bg); color: var(--text-secondary); display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; }
.step-dot.active .dot-number { background: var(--accent); color: var(--card); }
.step-dot.done .dot-number { background: var(--success); color: var(--card); }
.dot-label { font-size: 11px; color: var(--text-secondary); }
.wizard-content { flex: 1; padding: 24px; overflow-y: auto; }
.wizard-nav { display: flex; align-items: center; padding: 16px 24px; border-top: 1px solid var(--border); gap: 12px; }
.nav-spacer { flex: 1; }
.btn-prev, .btn-skip, .btn-next, .btn-finish { padding: 8px 20px; border-radius: 8px; font-size: 14px; font-family: var(--font); cursor: pointer; border: none; transition: background 0.15s, border-color 0.15s, color 0.15s, transform 0.1s; }
.btn-prev { background: var(--tag-bg); color: var(--text-primary); border: 1px solid var(--border); }
.btn-prev:hover { background: var(--card-hover); border-color: var(--border-strong); }
.btn-skip { background: none; color: var(--text-tertiary); }
.btn-skip:hover { color: var(--text-secondary); }
.btn-next { background: var(--accent); color: var(--card); }
.btn-next:hover { background: var(--accent-hover); }
.btn-finish { background: var(--success); color: var(--card); font-weight: 600; }
.btn-finish:hover { background: color-mix(in srgb, var(--success) 88%, var(--primary) 12%); }
.btn-prev:active, .btn-skip:active, .btn-next:active, .btn-finish:active { transform: translateY(1px); }
</style>
