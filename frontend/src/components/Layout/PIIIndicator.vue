<template>
  <span class="pii-indicator" :class="{ 'pii-indicator--masked': isMasked }">
    <template v-if="isMasked">
      <span class="pii-masked">{{ maskedValue }}</span>
      <button
        v-if="!revealed"
        class="pii-reveal-btn"
        @click.stop="requestReveal"
        :title="`${$t('zh_ef6766')}（${countdown}${$t('zh_6ba6d9')}）`"
      >
        👁️ {{ $t('zh_006711') }}
      </button>
      <template v-else>
        <span class="pii-revealed">{{ revealedValue }}</span>
        <span class="pii-countdown">({{ countdown }}s)</span>
      </template>
    </template>
    <template v-else>
      <slot>{{ value }}</slot>
    </template>

    <!-- Confirm dialog for reveal -->
    <teleport to="body">
      <transition name="fade">
        <div v-if="showConfirm" class="pii-confirm-overlay" @click="cancelReveal">
          <div class="pii-confirm-dialog" @click.stop>
            <div class="pii-confirm-icon">⚠️</div>
            <div class="pii-confirm-title">确认显示敏感信息</div>
            <div class="pii-confirm-desc">即将显示：{{ piiType }}，{{ countdown }}秒后自动隐藏</div>
            <div class="pii-confirm-actions">
              <button class="pii-confirm-cancel" @click="cancelReveal">取消</button>
              <button class="pii-confirm-ok" @click="confirmReveal">确认显示</button>
            </div>
          </div>
        </div>
      </transition>
    </teleport>
  </span>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'

interface Props {
  value: string
  type?: 'credit-card' | 'id-card' | 'phone' | 'email' | 'custom'
  autoHideSeconds?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'custom',
  autoHideSeconds: 30,
})

const revealed = ref(false)
const showConfirm = ref(false)
const countdown = ref(props.autoHideSeconds)

let hideTimer: ReturnType<typeof setTimeout> | null = null
let countdownTimer: ReturnType<typeof setInterval> | null = null

// Regex patterns for PII detection
const PII_PATTERNS = {
  'credit-card': /\b(\d{4}[-\s]?){3}\d{4}\b/g,
  'id-card': /\b\d{17}[\dXx]\b/g,
  'phone': /\b1[3-9]\d{9}\b/g,
  'email': /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
}

// Detect PII type from value if not specified
const piiType = computed(() => {
  if (props.type !== 'custom') return props.type

  for (const [type, pattern] of Object.entries(PII_PATTERNS)) {
    if (pattern.test(props.value)) return type as Props['type']
  }
  return 'custom'
})

// Check if value contains PII
const isPII = computed(() => {
  if (props.type !== 'custom') return true
  return Object.values(PII_PATTERNS).some(p => p.test(props.value))
})

// Mask the value
const maskedValue = computed(() => {
  const val = props.value
  const type = piiType.value

  switch (type) {
    case 'credit-card': {
      // Show last 4 digits: ****-****-****-1234
      const cleaned = val.replace(/[-\s]/g, '')
      const last4 = cleaned.slice(-4)
      return `●●●●-●●●●-●●●●-${last4}`
    }
    case 'id-card': {
      // Show last 8: ******199001011234
      const last8 = val.slice(-8)
      return `●●●●●●${last8}`
    }
    case 'phone': {
      // Show last 4: 138****5678
      const last4 = val.slice(-4)
      const prefix = val.slice(0, 3)
      return `${prefix}****${last4}`
    }
    case 'email': {
      // Partial mask: t***@example.com
      const [user, domain] = val.split('@')
      if (!domain) return '●●●●@●●●●'
      const visible = user.slice(0, 2)
      return `${visible}●●●@${domain}`
    }
    default:
      // Generic: mask middle
      if (val.length <= 4) return '●●●●'
      return val.slice(0, 2) + '●●●●'.repeat(Math.ceil((val.length - 4) / 4)).slice(0, val.length - 4) + val.slice(-2)
  }
})

const isMasked = computed(() => isPII.value && !revealed.value)
const revealedValue = computed(() => props.value)

function requestReveal() {
  showConfirm.value = true
}

function cancelReveal() {
  showConfirm.value = false
}

function confirmReveal() {
  showConfirm.value = false
  revealed.value = true
  startHideTimer()
  startCountdown()
}

function startHideTimer() {
  if (hideTimer) clearTimeout(hideTimer)
  hideTimer = setTimeout(() => {
    revealed.value = false
    stopCountdown()
  }, props.autoHideSeconds * 1000)
}

function startCountdown() {
  countdown.value = props.autoHideSeconds
  if (countdownTimer) clearInterval(countdownTimer)
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer!)
    }
  }, 1000)
}

function stopCountdown() {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

onUnmounted(() => {
  if (hideTimer) clearTimeout(hideTimer)
  stopCountdown()
})
</script>

<style scoped>
.pii-indicator {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-mono);
}

.pii-masked {
  color: var(--text-secondary);
  letter-spacing: 0.5px;
}

.pii-reveal-btn {
  background: rgba(255, 149, 0, 0.1);
  border: 1px solid rgba(255, 149, 0, 0.3);
  border-radius: 4px;
  padding: 1px 6px;
  font-size: 0.75rem;
  cursor: pointer;
  color: #ff9500;
  transition: all 0.2s;
}

.pii-reveal-btn:hover {
  background: rgba(255, 149, 0, 0.2);
}

.pii-revealed {
  color: var(--text-primary);
  background: rgba(255, 149, 0, 0.08);
  padding: 1px 4px;
  border-radius: 3px;
}

.pii-countdown {
  font-size: 0.7rem;
  color: var(--text-secondary);
}

/* Confirm dialog */
.pii-confirm-overlay {
  position: fixed;
  inset: 0;
  background: var(--modal-backdrop);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.pii-confirm-dialog {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  max-width: 320px;
  text-align: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.pii-confirm-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}

.pii-confirm-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.pii-confirm-desc {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.pii-confirm-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.pii-confirm-cancel,
.pii-confirm-ok {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.pii-confirm-cancel {
  background: var(--tag-bg);
  border: 1px solid var(--border);
  color: var(--text-secondary);
}

.pii-confirm-cancel:hover {
  background: var(--border);
}

.pii-confirm-ok {
  background: #ff9500;
  border: none;
  /* P38 r33: on-accent 文字 token 化 — 旧 #fff 改为 var(--card), 
     修复 future 改 #ff9500 时的 dark 模式不一致风险 (虽然当前 #ff9500 不随主题变).
     防御性修复, 0 视觉变化. */
  color: var(--card);
}

.pii-confirm-ok:hover {
  background: #e68600;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>