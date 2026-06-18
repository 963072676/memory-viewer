import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import {
  fetchProviders,
  fetchProviderHealth,
  switchProvider as apiSwitchProvider,
  updateProviderStrategy,
  type ProviderHealthInfo,
  type ProviderInfo,
  type ProviderStrategy,
  type ProviderStrategyUpdate,
} from '@/api/providers'

export const useProviderStore = defineStore('providers', () => {
  const providers = ref<ProviderInfo[]>([])
  const strategy = ref<ProviderStrategy | null>(null)
  const health = ref<Record<string, ProviderHealthInfo>>({})
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<string | null>(null)
  const loaded = ref(false)
  const lastFetch = ref<Date | null>(null)

  const activeProvider = computed(() => (
    strategy.value?.activeProvider
    || providers.value.find(provider => provider.active)?.name
    || ''
  ))

  const fallbackProviders = computed(() => (
    strategy.value?.fallbackProviders
    || providers.value.filter(provider => provider.fallback).map(provider => provider.name)
  ))

  const enabledProviders = computed(() => providers.value.filter(provider => provider.enabled))
  const healthyCount = computed(() => Object.values(health.value).filter(item => item.healthy).length)
  const unhealthyCount = computed(() => Math.max(0, providers.value.length - healthyCount.value))

  function applyStrategy(nextStrategy: ProviderStrategy) {
    strategy.value = nextStrategy
    providers.value = providers.value.map(provider => ({
      ...provider,
      active: provider.name === nextStrategy.activeProvider,
      fallback: nextStrategy.fallbackProviders.includes(provider.name),
    }))
    health.value = Object.fromEntries(
      Object.entries(health.value).map(([name, info]) => [
        name,
        {
          ...info,
          active: name === nextStrategy.activeProvider,
          fallback: nextStrategy.fallbackProviders.includes(name),
        },
      ]),
    )
  }

  async function load() {
    loading.value = true
    error.value = null
    try {
      const response = await fetchProviders()
      providers.value = response.providers
      strategy.value = response.strategy
      health.value = response.health
      loaded.value = true
      lastFetch.value = new Date()
    } catch (e: any) {
      error.value = e?.message || 'Failed to load providers'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function refreshHealth() {
    try {
      const response = await fetchProviderHealth()
      health.value = response.health
    } catch (e: any) {
      error.value = e?.message || 'Failed to refresh provider health'
      throw e
    }
  }

  async function saveStrategy(update: ProviderStrategyUpdate) {
    saving.value = true
    error.value = null
    try {
      const response = await updateProviderStrategy(update)
      applyStrategy(response.strategy)
    } catch (e: any) {
      error.value = e?.message || 'Failed to save provider strategy'
      throw e
    } finally {
      saving.value = false
    }
  }

  async function switchActiveProvider(name: string) {
    saving.value = true
    error.value = null
    try {
      const response = await apiSwitchProvider(name)
      applyStrategy(response.strategy)
    } catch (e: any) {
      error.value = e?.message || 'Failed to switch provider'
      throw e
    } finally {
      saving.value = false
    }
  }

  return {
    providers,
    strategy,
    health,
    loading,
    saving,
    error,
    loaded,
    lastFetch,
    activeProvider,
    fallbackProviders,
    enabledProviders,
    healthyCount,
    unhealthyCount,
    load,
    refreshHealth,
    saveStrategy,
    switchActiveProvider,
  }
})
