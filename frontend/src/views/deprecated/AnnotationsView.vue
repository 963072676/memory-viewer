<template>
  <div class="annotations-view">
    <div class="annotations-header">
      <h2>💬 协作标注</h2>
      <div class="header-actions">
        <select v-model="filterType" class="filter-select">
          <option value="">全部类型</option>
          <option value="comment">💬 评论</option>
          <option value="flag">🚩 待审</option>
          <option value="suggest">💡 建议</option>
        </select>
        <button class="btn-refresh" @click="loadAnnotations">🔄 刷新</button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">加载标注...</div>
    <div v-else-if="annotations.length === 0" class="empty-state">
      <p>💬 暂无标注</p>
      <p class="empty-hint">在记忆详情中添加评论和标注</p>
    </div>
    <div v-else class="annotations-list">
      <div v-for="group in groupedAnnotations" :key="group.memoryId" class="memory-group">
        <div class="group-header">
          <span class="group-title">{{ group.memoryTitle || group.memoryId }}</span>
          <span class="group-count">{{ group.annotations.length }} 条标注</span>
        </div>
        <AnnotationThread
          :annotations="group.annotations"
          @reply="handleReply"
          @resolve="handleResolve"
          @delete="handleDelete"
        />
        <AnnotationInput
          placeholder="添加评论..."
          submit-label="发送"
          @submit="(data) => addAnnotation(group.memoryId, data)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'
import AnnotationThread from '@/components/Layout/AnnotationThread.vue'
import AnnotationInput from '@/components/Layout/AnnotationInput.vue'

const toast = useToast()
const loading = ref(false)
const annotations = ref<any[]>([])
const filterType = ref('')

const groupedAnnotations = computed(() => {
  const groups: Record<string, any> = {}
  const filtered = filterType.value
    ? annotations.value.filter(a => a.type === filterType.value)
    : annotations.value

  for (const ann of filtered) {
    const mid = ann.memory_id
    if (!groups[mid]) groups[mid] = { memoryId: mid, memoryTitle: ann.memory_title, annotations: [] }
    groups[mid].annotations.push(ann)
  }
  return Object.values(groups)
})

async function loadAnnotations() {
  loading.value = true
  try {
    const res = await request<any>('/annotations')
    annotations.value = res.annotations || []
  } catch (e: any) {
    toast.error('加载失败: ' + e.message)
  } finally {
    loading.value = false
  }
}

async function addAnnotation(memoryId: string, data: any) {
  try {
    await request(`/memories/${memoryId}/annotations`, { method: 'POST', body: data })
    toast.success('已添加')
    await loadAnnotations()
  } catch (e: any) {
    toast.error('添加失败: ' + e.message)
  }
}

async function handleReply(parentId: string) {
  // For simplicity, handled via the AnnotationInput on the group level
  toast.info('请在下方输入框中输入回复内容')
}

async function handleResolve(annId: string) {
  try {
    await request(`/annotations/${annId}/resolve`, { method: 'POST' })
    toast.success('已解决')
    await loadAnnotations()
  } catch (e: any) {
    toast.error('操作失败')
  }
}

async function handleDelete(annId: string) {
  if (!confirm('确定删除此标注?')) return
  try {
    await request(`/annotations/${annId}`, { method: 'DELETE' })
    toast.success('已删除')
    await loadAnnotations()
  } catch (e: any) {
    toast.error('删除失败')
  }
}

onMounted(loadAnnotations)
</script>

<style scoped>
.annotations-view { padding: 20px; }
.annotations-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-actions { display: flex; gap: 8px; }
.filter-select { padding: 6px 12px; border: 1px solid var(--border, #ddd); border-radius: 6px; font-size: 13px; background: var(--card-bg, #fff); }
.btn-refresh { padding: 6px 12px; border: 1px solid var(--border, #ddd); border-radius: 6px; background: var(--card-bg, #f8f9fa); cursor: pointer; font-size: 13px; }
.memory-group { background: var(--card-bg, #fff); border: 1px solid var(--border, #e0e0e0); border-radius: 12px; padding: 16px; margin-bottom: 12px; }
.group-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid var(--border, #eee); }
.group-title { font-weight: 600; font-size: 15px; }
.group-count { font-size: 12px; color: #666; background: var(--card-bg, #f0f0f0); padding: 2px 8px; border-radius: 10px; }
.loading-state { text-align: center; padding: 40px; color: #999; }
.empty-state { text-align: center; padding: 60px; color: #999; }
.empty-hint { font-size: 13px; color: #bbb; margin-top: 4px; }
</style>
