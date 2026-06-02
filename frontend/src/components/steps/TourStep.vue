<template>
  <div class="tour-step">
    <h3>🗺️ 功能导览</h3>
    <p class="desc">点击下方功能卡片查看它在界面上的位置</p>
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
