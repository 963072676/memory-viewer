<template>
  <div class="tour-step">
    <h3>🗺️ {{ $t('i18n.feature_tour') }}</h3>
    <p class="desc">{{ $t('tour.feature_intro') }}</p>
    <FeatureTour @close="onTourClose" />
  </div>
</template>

<script setup lang="ts">
import FeatureTour from '@/components/FeatureTour.vue'
import { useUIStore } from '@/stores/ui'

const uiStore = useUIStore()

function onTourClose() {
  // PM-20260612-002 F2: FeatureTour 弹层点 ✕ -> 关闭整个 tour
  uiStore.setShowTour(false)
}
</script>

<style scoped>
.tour-step h3 { margin-bottom: 8px; }
.desc { color: #666; font-size: 14px; margin-bottom: 16px; }
</style>
