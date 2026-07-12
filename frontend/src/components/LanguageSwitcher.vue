<template>
  <button
    class="lang-switcher"
    :class="{ 'lang-switcher--en': isEnglish }"
    :title="isEnglish ? $t('i18n.switch_to_chinese') : $t('i18n.switch_to_english')"
    :aria-label="isEnglish ? $t('i18n.switch_to_chinese') : $t('i18n.switch_to_english')"
    @click="toggle"
  >
    <span class="lang-switcher__label">{{ isEnglish ? 'EN' : 'CN' }}</span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { loadMessages } from '@/main'

const STORAGE_KEY = 'mv-locale'
const { locale, setLocaleMessage } = useI18n()
const isEnglish = computed(() => locale.value === 'en-US')

async function toggle() {
  const next = isEnglish.value ? 'zh-CN' : 'en-US'
  // AC-11: 按需加载 — loadMessages 会 await import 对应 locale 的 JSON
  const msgs = await loadMessages(next)
  setLocaleMessage(next, msgs)
  locale.value = next
  try { localStorage.setItem(STORAGE_KEY, next) } catch {}
}
</script>

<style scoped>
.lang-switcher {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  transition: background 0.2s, border-color 0.2s, transform 0.15s;
  user-select: none;
}

.lang-switcher:hover {
  background: var(--hover-bg);
  border-color: var(--primary);
  transform: scale(1.05);
}

.lang-switcher:active {
  transform: scale(0.95);
}

.lang-switcher--en {
  color: var(--primary);
  border-color: var(--primary);
}

.lang-switcher__label {
  font-variant-numeric: tabular-nums;
  font-family: var(--font-mono, 'SF Mono', Menlo, monospace);
}
</style>
