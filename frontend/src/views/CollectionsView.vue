<template>
  <div class="collections-view">
    <div class="cv-header">
      <h2 class="section-title">📚 Collections</h2>
      <button class="btn-create" @click="openEditor(null)">+ New Collection</button>
    </div>

    <div v-if="loading" class="loading-state">Loading collections...</div>

    <div v-else-if="collections.length === 0" class="empty-state">
      <p>📁 No collections yet</p>
      <button class="btn-create" @click="openEditor(null)">Create your first collection</button>
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
    collections.value = res.collections
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

/* P41: 与 P39 HomeView 的 .action-btn--primary 对齐 — 主 CTA 用 --primary 黑/白药丸，
   避免与侧栏激活态/链接的蓝色信号混淆。 */
.btn-create {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: var(--space-2) var(--space-4);
  border: 1px solid transparent;
  border-radius: var(--radius-pill);
  background: var(--primary);
  color: var(--bg);
  font-size: 0.85rem;
  font-weight: 500;
  font-family: var(--font);
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  transition: background 0.15s, box-shadow 0.15s, transform 0.05s;
}

.btn-create:hover {
  background: var(--primary-muted);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.btn-create:active {
  transform: translateY(1px);
}

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
