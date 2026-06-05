<template>
  <div class="collection-card" :style="{ borderLeftColor: collection.color }" @click="$emit('click')">
    <div class="card-top">
      <span class="card-icon" :style="{ background: iconBg, color: collection.color }">
        {{ collection.icon }}
      </span>
      <div class="card-actions">
        <button class="btn-icon" :title="$t('en_edit')" @click.stop="$emit('edit')">✏️</button>
        <button class="btn-icon" :title="$t('en_delete')" @click.stop="$emit('delete')">🗑️</button>
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
import { computed } from 'vue'
import type { Collection } from '@/api/collections'

const props = defineProps<{
  collection: Collection
}>()

defineEmits<{
  (e: 'click'): void
  (e: 'edit'): void
  (e: 'delete'): void
}>()

/* P49 r1: CollectionCard 全面 token 化 — card-icon 背景色。
   兼容两层数据：
   - 新 collection（P48 r2 后）：collection.color = 'var(--collection-color-N)' 引用，
     自动用对应的 --collection-color-N-bg token（dark 模式自动跟随 + 4.5:1 对比度保证）。
   - 旧 collection（P48 r2 前）：collection.color = '#0072aff' 字面 hex，
     退回到 hex + '20' 拼接（12.5% alpha）— 与新版的视觉差异极小（都是低饱和度色块）。 */
const iconBg = computed(() => {
  const c = props.collection.color
  if (!c) return 'var(--collection-color-1-bg)'
  // 匹配 var(--collection-color-N) 引用 → 找对应的 -bg token
  const m = c.match(/var\(--collection-color-(\d+)\)/)
  if (m) {
    return `var(--collection-color-${m[1]}-bg)`
  }
  // legacy hex → 拼接 12% alpha（与 0.12 color-mix 视觉等价）
  return c + '20'
})
</script>

<style scoped>
.collection-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-left: 4px solid var(--accent);
  border-radius: var(--radius);
  padding: 16px;
  cursor: pointer;
  /* P38 r12: 与 MemoryCard / DashboardWidget / TemplateCard 4 套 Card hover 视觉同源
     (var(--shadow-hover) + translateY(-2px) + 0.25s cubic-bezier 过渡 + border-strong 强化)
     之前用 var(--shadow) (轻) + translateY(-2px), hover 反馈弱于同站其他 Card */
  transition: box-shadow 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              transform 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              border-color 0.2s ease;
}

.collection-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
  border-left-color: var(--primary);
  border-top-color: var(--border-strong);
  border-right-color: var(--border-strong);
  border-bottom-color: var(--border-strong);
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
