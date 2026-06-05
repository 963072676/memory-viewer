<template>
  <div class="collections-view">
    <div class="cv-header">
      <h2 class="section-title">{{ $t('en_collections') }}</h2>
      <button class="action-btn action-btn--primary" @click="openEditor(null)">{{ $t('en_new_collection') }}</button>
    </div>

    <div v-if="loading" class="loading-state">{{ $t('en_loading_collections') }}</div>

    <div v-else-if="collections.length === 0" class="empty-state">
      <p>{{ $t('en_no_collections') }}</p>
      <button class="action-btn action-btn--primary" @click="openEditor(null)">{{ $t('en_first_collection') }}</button>
    </div>

    <div v-else class="collections-grid">
      <CollectionCard
        v-for="col in collections"
        :key="col.id"
        :collection="col"
        @click="viewCollection(col)"
        @edit="openEditor(col)"
        @delete="handleDelete(col)"
      />
    </div>

    <CollectionEditor
      v-if="showEditor"
      :collection="editingCollection"
      @close="showEditor = false"
      @saved="handleSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCollections, createCollection, updateCollection, deleteCollection } from '@/api/collections'
import type { Collection } from '@/api/collections'
import { useToast } from '@/composables/useToast'
import { migrateCollectionColor } from '@/utils/collection-color'
import CollectionCard from '@/components/Layout/CollectionCard.vue'
import CollectionEditor from '@/components/Layout/CollectionEditor.vue'

const router = useRouter()
const toast = useToast()

const loading = ref(false)
const collections = ref<Collection[]>([])
const showEditor = ref(false)
const editingCollection = ref<Collection | null>(null)

async function loadCollections() {
  loading.value = true
  try {
    const res = await getCollections()
    // P49 r3: legacy hex → var() 自动迁移 — 让旧 collection 也享受 dark 模式正确渲染.
    // 仅"显示时"迁移, 不写回 backend (避免 P48 r2 设计好的"两套数据共存"破裂).
    collections.value = res.collections.map(c => ({
      ...c,
      color: migrateCollectionColor(c.color),
    }))
  } catch {
    collections.value = []
  } finally {
    loading.value = false
  }
}

function openEditor(collection: Collection | null) {
  editingCollection.value = collection
  showEditor.value = true
}

function viewCollection(col: Collection) {
  router.push({ path: '/', query: { collection: col.id } })
}

async function handleSave(data: any) {
  try {
    if (editingCollection.value) {
      await updateCollection(editingCollection.value.id, data)
      toast.success('Collection updated')
    } else {
      await createCollection(data)
      toast.success('Collection created')
    }
    showEditor.value = false
    await loadCollections()
  } catch (e: any) {
    toast.error('Failed to save collection: ' + (e.message || ''))
  }
}

async function handleDelete(col: Collection) {
  if (!confirm(`Delete collection "${col.name}"?`)) return
  try {
    await deleteCollection(col.id)
    toast.success('Collection deleted')
    await loadCollections()
  } catch (e: any) {
    toast.error('Failed to delete collection: ' + (e.message || ''))
  }
}

onMounted(loadCollections)
</script>

<style scoped>
.collections-view {
  padding-bottom: 40px;
}

.cv-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-header-gap);
  gap: var(--space-3);
}

.cv-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary);  /* P41: 去误导的 #007aff fallback — --primary 已是黑/白文字色 */
  margin: 0;
}

/* P38 r20: section-title 左侧 3px accent bar — 与全站其他 view 同源 (r15 模式). */
.cv-header h2.section-title { position: relative; padding-left: 12px; }
.cv-header h2.section-title::before { content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%); width: 3px; height: 60%; background: var(--accent); border-radius: 0 2px 2px 0; }

/* P38 r21: button system unification — .action-btn + .action-btn--primary
   now defined globally in styles/main.css. Local rules removed. */

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px var(--space-5);
  color: var(--text-secondary);
  font-size: 1rem;
}

.empty-state p {
  margin-bottom: var(--space-4);
}

.collections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-5);
}

@media (max-width: 767px) {
  .collections-grid {
    grid-template-columns: 1fr;
  }
}
</style>
