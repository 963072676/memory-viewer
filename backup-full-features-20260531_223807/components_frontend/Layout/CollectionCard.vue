<template>
  <div class="collection-card" :style="{ borderLeftColor: collection.color }" @click="$emit('click')">
    <div class="card-top">
      <span class="card-icon" :style="{ background: collection.color + '20', color: collection.color }">
        {{ collection.icon }}
      </span>
      <div class="card-actions">
        <button class="btn-icon" title="Edit" @click.stop="$emit('edit')">✏️</button>
        <button class="btn-icon" title="Delete" @click.stop="$emit('delete')">🗑️</button>
      </div>
    </div>
    <h3 class="card-name">{{ collection.name }}</h3>
    <p class="card-desc" v-if="collection.description">{{ collection.description }}</p>
    <div class="card-footer">
      <span class="memory-count">
        <span class="count-number">{{ collection.memory_count }}</span> memories
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Collection } from '@/api/collections'

defineProps<{
  collection: Collection
}>()

defineEmits<{
  (e: 'click'): void
  (e: 'edit'): void
  (e: 'delete'): void
}>()
</script>

<style scoped>
.collection-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-left: 4px solid var(--accent);
  border-radius: var(--radius);
  padding: 16px;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
}

.collection-card:hover {
  box-shadow: var(--shadow);
  transform: translateY(-2px);
}

.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12px;
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  font-size: 1.2rem;
}

.card-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.collection-card:hover .card-actions {
  opacity: 1;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.85rem;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.2s;
}

.btn-icon:hover {
  background: var(--tag-bg);
}

.card-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary);
  margin: 0 0 4px;
}

.card-desc {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin: 0 0 12px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.memory-count {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.count-number {
  font-weight: 700;
  color: var(--primary);
}
</style>
