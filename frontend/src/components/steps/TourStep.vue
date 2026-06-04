<template>
  <div class="tour-step">
    <h3>🗺️ {{ $t('zh_abdc6b') }}</h3>
    <p class="desc">{{ $t('zh_8d42b9') }}</p>
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
