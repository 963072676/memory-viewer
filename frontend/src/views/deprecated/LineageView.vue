<template>
  <div class="lineage-view">
    <div class="lineage-header">
      <h2>🌳 记忆谱系</h2>
      <p class="lineage-subtitle">查看记忆的来源与衍生关系</p>
    </div>
    <LineageGraph />
  </div>
</template>

<script setup lang="ts">
import LineageGraph from '@/components/Layout/LineageGraph.vue'
</script>

<style scoped>
.lineage-view {
  padding-bottom: 40px;
}

.lineage-header {
  margin-bottom: 24px;
}

.lineage-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary, #007aff);
  margin: 0 0 4px;
}

.lineage-subtitle {
  font-size: 0.85rem;
  color: var(--text-secondary, #86868b);
  margin: 0;
}
</style>
