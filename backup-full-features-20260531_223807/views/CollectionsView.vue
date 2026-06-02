<template>
  <div class="collections-view">
    <div class="cv-header">
      <h2>📚 Collections</h2>
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
  margin-bottom: 24px;
}

.cv-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary, #007aff);
  margin: 0;
}

.btn-create {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  background: var(--accent, #007aff);
  color: #fff;
  font-size: 0.85rem;
  cursor: pointer;
  font-family: var(--font);
  transition: opacity 0.2s;
}

.btn-create:hover {
  opacity: 0.9;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  font-size: 1rem;
}

.empty-state p {
  margin-bottom: 16px;
}

.collections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

@media (max-width: 767px) {
  .collections-grid {
    grid-template-columns: 1fr;
  }
}
</style>
