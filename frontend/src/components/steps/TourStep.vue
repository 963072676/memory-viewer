<template>
  <div class="tour-step">
    <h3>🗺️ {{ $t('i18n.feature_tour') }}</h3>
    <p class="desc">{{ $t('tour.feature_intro') }}</p>
    <FeatureTour />
  </div>
</template>

<script setup lang="ts">
import FeatureTour from '@/components/FeatureTour.vue'
</script>

<style scoped>
.tour-step h3 { margin-bottom: 8px; }
.desc { color: #666; font-size: 14px; margin-bottom: 16px; }
</style>
