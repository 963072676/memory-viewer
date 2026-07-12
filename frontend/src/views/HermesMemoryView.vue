<template>
  <div class="hermes-view">
    <HermesMemoryExplorer :profile="profile" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import HermesMemoryExplorer from '@/components/Layout/HermesMemoryExplorer.vue'

const route = useRoute()
const profile = computed(() => {
  const value = route.query.profile
  return Array.isArray(value) ? value[0] || '' : value || ''
})
</script>

<style scoped>
.hermes-view {
  padding-bottom: 40px;
}
</style>
