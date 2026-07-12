<template>
  <button
    class="provider-status"
    :class="{ unhealthy: isUnhealthy, loading: providerStore.loading }"
    type="button"
    :title="statusTitle"
    :aria-label="statusTitle"
    @click="openProviderSettings"
  >
    <span class="provider-dot" :class="dotClass" aria-hidden="true"></span>
    <span class="provider-label">{{ activeLabel }}</span>
  </button>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useProviderStore } from '@/stores/providers'

const router = useRouter()
const providerStore = useProviderStore()
const { t } = useI18n()

const activeLabel = computed(() => providerStore.activeProvider || t('i18n.provider_badge_none'))
const activeHealth = computed(() => (
  providerStore.activeProvider ? providerStore.health[providerStore.activeProvider] : null
))
const isUnhealthy = computed(() => activeHealth.value?.healthy === false)
const dotClass = computed(() => {
  if (providerStore.loading && !providerStore.loaded) return 'pending'
  if (!activeHealth.value) return 'unknown'
  return activeHealth.value.healthy ? 'healthy' : 'unhealthy'
})
const statusTitle = computed(() => {
  if (!providerStore.loaded) return t('i18n.provider_badge_status')
  const health = activeHealth.value
    ? t(activeHealth.value.healthy ? 'i18n.healthy' : 'i18n.unhealthy')
    : t('i18n.provider_health_unknown')
  return t('i18n.provider_badge_active', { provider: activeLabel.value, status: health })
})

function openProviderSettings() {
  router.push({ path: '/settings', query: { tab: 'providers' } })
}

onMounted(() => {
  if (!providerStore.loaded && !providerStore.loading) {
    providerStore.load().catch(() => {
      // The store keeps the user-facing error.
    })
  }
})
</script>

<style scoped>
.provider-status {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-width: 118px;
  max-width: 180px;
  height: 34px;
  padding: 0 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--primary);
  cursor: pointer;
  box-shadow: var(--shadow-press);
}

.provider-status:hover {
  background: var(--tag-bg);
  border-color: var(--border-strong);
}

.provider-status.unhealthy {
  border-color: color-mix(in srgb, var(--error-text) 35%, var(--border));
}

.provider-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex: 0 0 auto;
  background: var(--text-secondary);
}

.provider-dot.healthy {
  background: var(--success-text);
  box-shadow: 0 0 6px color-mix(in srgb, var(--success-text) 45%, transparent);
}

.provider-dot.unhealthy {
  background: var(--error-text);
  box-shadow: 0 0 6px color-mix(in srgb, var(--error-text) 45%, transparent);
}

.provider-dot.pending {
  background: var(--warning);
}

.provider-label {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.78rem;
  font-weight: 600;
  line-height: 1;
}

@media (max-width: 767px) {
  .provider-status {
    min-width: 34px;
    width: 34px;
    padding: 0;
    justify-content: center;
  }

  .provider-label {
    display: none;
  }
}
</style>
