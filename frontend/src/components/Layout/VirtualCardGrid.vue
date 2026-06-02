<template>
  <RecycleScroller
    class="virtual-grid"
    :items="items"
    :item-size="itemSize"
    :key-field="keyField"
    :grid-items="gridCols"
    :item-secondary-size="colWidth"
    :buffer="400"
    v-slot="{ item }"
  >
    <slot :item="item" />
  </RecycleScroller>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { RecycleScroller } from 'vue-virtual-scroller'

const props = withDefaults(defineProps<{
  items: any[]
  itemSize?: number
  keyField?: string
  minColWidth?: number
}>(), {
  itemSize: 200,
  keyField: 'id',
  minColWidth: 340,
})

const containerWidth = ref(1200)

const gridCols = computed(() => {
  return Math.max(1, Math.floor(containerWidth.value / props.minColWidth))
})

const colWidth = computed(() => {
  return containerWidth.value / gridCols.value
})

function onResize() {
  containerWidth.value = window.innerWidth - 240 // subtract sidebar width
}

onMounted(() => {
  onResize()
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
})
</script>

<style scoped>
.virtual-grid {
  height: calc(100vh - 300px);
  overflow-y: auto;
}
</style>
