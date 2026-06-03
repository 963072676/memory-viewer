<template>
  <div class="memory-detail-view">
    <div class="view-header">
      <button class="back-btn" @click="goBack">
        ← 返回
      </button>
      <div class="view-actions">
        <!-- P38 (round 3): 5 个按钮层级化 — 之前全用 accent 实色 → 5 个"假 primary"同时喊叫。
             改为：编辑 = primary（最常用操作） / 展开 + 分享 + 历史 = ghost 描边（次级 utility） / 删除 = danger（破坏性，红字 + 红描边）。
             注：折叠/展开按钮 + 分享 + 历史 都是"看+导航"类，不改变记忆内容 → ghost 更合适。 -->
        <button class="action-btn action-btn--ghost" @click="toggleExpand">
          {{ isExpanded ? '折叠' : '展开' }}
        </button>
        <button class="action-btn action-btn--ghost" @click="router.push(`/memory/${route.params.id}/history`)">历史</button>
        <button class="action-btn action-btn--ghost" @click="showShareModal = true">分享</button>
        <button class="action-btn action-btn--primary" @click="showEditModal = true">编辑</button>
        <button class="action-btn action-btn--danger" @click="confirmDelete = true">删除</button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="skeleton-card"></div>
    </div>

    <div v-else-if="error" class="error-state">
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <button class="action-btn" @click="loadMemory">重试</button>
    </div>

    <div v-else-if="memory" class="memory-content">
      <div class="memory-header">
        <div class="title-row">
          <h1>{{ memory.title }}</h1>
          <span class="memory-type" :class="'type-' + memory.type">{{ memory.type }}</span>
          <span v-if="memory.archived" class="archived-badge">已归档</span>
        </div>
        <div class="meta-row">
          <HealthBadge v-if="healthDisplay" :score="healthDisplay.health_score" :color="healthDisplay.color" />
          <span class="strength-bar">
            <span class="strength-fill" :style="{ width: (memory.strength * 10) + '%' }"></span>
          </span>
          <span class="meta-text">Strength: {{ memory.strength * 10 }}%</span>
        </div>
      </div>

      <div class="memory-body" :class="{ expanded: isExpanded }">
        <div class="card-content" v-html="sanitizedContent"></div>
      </div>

      <div class="memory-details">
        <div class="detail-section">
          <h4>Concepts</h4>
          <div class="tags" v-if="memory.concepts && memory.concepts.length">
            <span class="tag" v-for="c in memory.concepts" :key="c">{{ c }}</span>
          </div>
          <span v-else class="no-data">无</span>
        </div>

        <div class="detail-section">
          <h4>标签</h4>
          <TagManager
            v-if="allTagNames.length"
            :tags="memory.tags || []"
            :all-tags="allTagNames"
            @update:tags="onTagsUpdate"
          />
          <span v-else class="no-data">无</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Created</span>
          <span>{{ formatDate(memory.createdAt) }}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Updated</span>
          <span>{{ formatDate(memory.updatedAt) }}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">ID</span>
          <span class="memory-id">{{ memory.id }}</span>
        </div>

        <div class="detail-row" v-if="memory.version">
          <span class="detail-label">Version</span>
          <span>{{ memory.version }}</span>
        </div>
      </div>

      <!-- Health breakdown -->
      <div class="health-section" v-if="healthData">
        <h4>健康度详情</h4>
        <div class="health-breakdown">
          <div class="breakdown-item">
            <span class="breakdown-label">强度</span>
            <span class="breakdown-value">{{ healthData.breakdown.strength_score }}</span>
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label">年龄</span>
            <span class="breakdown-value">{{ healthData.breakdown.age_score }}</span>
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label">概念</span>
            <span class="breakdown-value">{{ healthData.breakdown.concepts_score }}</span>
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label">推荐</span>
            <span class="breakdown-value">{{ healthData.breakdown.recommendation_score }}</span>
          </div>
        </div>
      </div>

      <!-- Related memories -->
      <RelatedMemories :memory-id="memory.id" />

      <!-- Decay chart -->
      <DecayChart v-if="decayData" :data="decayData" />
    </div>

    <ConfirmDialog
      v-if="confirmDelete"
      title="确认删除"
      message="确定要删除这条记忆吗？此操作不可撤销。"
      confirm-text="删除"
      cancel-text="取消"
      @confirm="handleDelete"
      @cancel="confirmDelete = false"
    />

    <EditMemoryModal
      v-if="showEditModal && memory"
      :memory="memory"
      @close="showEditModal = false"
      @updated="onMemoryUpdated"
    />

    <ShareModal
      v-if="showShareModal && memory"
      :memoryId="memory.id"
      @close="showShareModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchAgentMemoryById, setMemoryTags, deleteAgentMemory } from '@/api/agentmemory'
import { getHealth } from '@/api/agentmemory'
import { getDecay } from '@/api/agentmemory'
import { useAgentMemoryStore } from '@/stores/agentmemory'
import { useToast } from '@/composables/useToast'
import HealthBadge from '@/components/Layout/HealthBadge.vue'
import TagManager from '@/components/Layout/TagManager.vue'
import RelatedMemories from '@/components/Layout/RelatedMemories.vue'
import DecayChart from '@/components/Layout/DecayChart.vue'
import ConfirmDialog from '@/components/Layout/ConfirmDialog.vue'
import EditMemoryModal from '@/components/Layout/EditMemoryModal.vue'
import ShareModal from '@/components/Layout/ShareModal.vue'
import type { AgentMemory, HealthResponse, DecayResponse } from '@/types'

const route = useRoute()
const router = useRouter()
const store = useAgentMemoryStore()
const toast = useToast()

const memory = ref<AgentMemory | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const isExpanded = ref(false)
const showEditModal = ref(false)
const showShareModal = ref(false)
const confirmDelete = ref(false)
const healthData = ref<HealthResponse | null>(null)
const decayData = ref<DecayResponse | null>(null)

const allTagNames = computed(() => store.allTags.map(t => t.tag))

const healthDisplay = computed(() => {
  if (!healthData.value) return null
  const score = healthData.value.health_score
  const color = score > 70 ? 'green' : score >= 40 ? 'yellow' : 'red'
  return {
    health_score: score,
    color: color as 'green' | 'yellow' | 'red'
  }
})

const sanitizedContent = computed(() => {
  if (!memory.value?.content) return ''
  // Simple HTML escaping for safety
  return memory.value.content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/\n/g, '<br>')
})

function formatDate(dateStr: string | undefined): string {
  if (!dateStr) return 'N/A'
  try {
    return new Date(dateStr).toLocaleString('zh-CN')
  } catch {
    return dateStr
  }
}

function goBack() {
  router.back()
}

function toggleExpand() {
  isExpanded.value = !isExpanded.value
}

async function loadMemory() {
  const id = route.params.id as string
  if (!id || id === 'collection') {
    error.value = 'Invalid memory ID'
    router.push('/agentmemory')
    return
  }

  loading.value = true
  error.value = null

  try {
    const data = await fetchAgentMemoryById(id)
    if (data.memories && data.memories.length > 0) {
      memory.value = data.memories[0]
      // Load health and decay data
      try {
        healthData.value = await getHealth(id)
      } catch {
        // Health is optional
      }
      try {
        decayData.value = await getDecay(id)
      } catch {
        // Decay is optional
      }
    } else {
      error.value = 'Memory not found'
    }
  } catch (e: any) {
    error.value = e.message || 'Failed to load memory'
  } finally {
    loading.value = false
  }
}

async function onTagsUpdate(newTags: string[]) {
  if (!memory.value) return
  try {
    const updated = await setMemoryTags(memory.value.id, newTags)
    if (updated.memory) {
      memory.value.tags = updated.memory.tags
      toast.success('标签已更新')
    }
  } catch (e: any) {
    toast.error('更新标签失败: ' + e.message)
  }
}

function onMemoryUpdated() {
  showEditModal.value = false
  toast.success('记忆已更新')
  loadMemory()
}

async function handleDelete() {
  if (!memory.value) return
  try {
    await deleteAgentMemory(memory.value.id)
    toast.success('记忆已删除')
    router.push('/agentmemory')
  } catch (e: any) {
    toast.error('删除失败: ' + e.message)
  }
}

onMounted(() => {
  loadMemory()
})
</script>

<style scoped>
.memory-detail-view {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}

.view-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.back-btn {
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.9rem;
}

.view-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

/* P38 (round 3): 重写 button 层级 — 旧实现默认 .action-btn 就是 accent 实色，5 按钮全喊叫。
   新实现：默认是 ghost 描边（"看+导航"类），primary/danger/ghost 三种变体覆盖。 */
.action-btn {
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--primary);
  cursor: pointer;
  font-size: 0.85rem;
  font-family: var(--font);
  font-weight: 500;
  transition: background 0.15s, border-color 0.15s, color 0.15s, transform 0.1s;
}

.action-btn:hover {
  background: var(--tag-bg);
  border-color: var(--border-strong);
}

.action-btn:active {
  transform: translateY(1px);
}

.action-btn--primary {
  background: var(--primary);
  color: var(--card);
  border-color: var(--primary);
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.08);
}

.action-btn--primary:hover {
  background: var(--primary-muted);
  border-color: var(--primary-muted);
}

/* P38 (round 3): danger — 改用 --error token (P36 已统一为 #ff3b30)，去掉硬编码 #dc3545。
   红字 + 透明红底 + 1px 红描边 → "危险"提示到位但不会跳出来抢 primary 戏。 */
.action-btn--danger {
  background: transparent;
  color: var(--error);
  border-color: color-mix(in srgb, var(--error) 30%, var(--border));
}

.action-btn--danger:hover {
  background: color-mix(in srgb, var(--error) 8%, var(--card));
  border-color: var(--error);
}

/* ghost 是默认的 .action-btn 形态（描边 card），但用修饰类更显式，方便未来 grep */
.action-btn--ghost {
  /* 完全继承 .action-btn 默认值；这里仅为显式语义标记 */
}

.loading-state {
  padding: 40px;
}

.skeleton-card {
  height: 200px;
  background: var(--tag-bg);
  border-radius: 12px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.error-state {
  text-align: center;
  padding: 40px;
}

.error-state h3 {
  color: var(--danger, #dc3545);
  margin-bottom: 8px;
}

.memory-content {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
}

.memory-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.title-row h1 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.memory-type {
  font-size: 0.75rem;
  padding: 3px 10px;
  border-radius: 12px;
  text-transform: capitalize;
}

/* P38 (round 5): type-chip token 化 — 与 MemoryCard / CommandPalette / DedupModal / MemoryDiffModal 完全对齐。
   之前用 Material Design hex（Google 调色板），与项目自有 --type-* token 撞色，且 dark 模式无适配。
   修复后 dark 模式自动跟随 variables.css 的 [data-theme='dark'] 重定义（无需在此处重复）。 */
.type-pattern { background: var(--type-pattern-bg); color: var(--type-pattern-text); }
.type-fact { background: var(--type-fact-bg); color: var(--type-fact-text); }
.type-preference { background: var(--type-preference-bg); color: var(--type-preference-text); }
.type-bug { background: var(--type-bug-bg); color: var(--type-bug-text); }
.type-workflow { background: var(--type-workflow-bg); color: var(--type-workflow-text); }
.type-architecture { background: var(--type-architecture-bg); color: var(--type-architecture-text); }

.archived-badge {
  font-size: 0.7rem;
  padding: 3px 8px;
  background: var(--tag-bg);
  border-radius: 4px;
  color: var(--text-secondary);
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.strength-bar {
  width: 100px;
  height: 6px;
  background: var(--tag-bg);
  border-radius: 3px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  background: var(--accent);
}

.meta-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.memory-body {
  margin-bottom: 20px;
}

.memory-body.expanded .card-content {
  max-height: none;
}

.card-content {
  font-size: 0.95rem;
  line-height: 1.6;
  color: var(--text-primary);
  max-height: 200px;
  overflow: hidden;
}

.memory-details {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
}

.detail-section {
  padding: 12px;
  background: var(--tag-bg);
  border-radius: 8px;
}

.detail-section h4 {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
}

.detail-label {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.memory-id {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--accent);
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  font-size: 0.75rem;
  padding: 3px 10px;
  border-radius: 12px;
  background: var(--card);
  color: var(--text-primary);
}

.no-data {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.health-section {
  margin-top: 20px;
  padding: 16px;
  background: var(--tag-bg);
  border-radius: 8px;
}

.health-section h4 {
  font-size: 0.9rem;
  margin-bottom: 12px;
}

.health-breakdown {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.breakdown-item {
  text-align: center;
}

.breakdown-label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.breakdown-value {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--accent);
}

/* Responsive */
@media (max-width: 767px) {
  .view-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .view-actions {
    flex-wrap: wrap;
    margin-left: 0;
  }

  .title-row {
    flex-wrap: wrap;
    gap: 8px;
  }

  .title-row h1 {
    font-size: 1.2rem;
    width: 100%;
  }

  .meta-row {
    flex-wrap: wrap;
    gap: 8px;
  }

  .memory-content {
    padding: 16px;
  }

  .health-breakdown {
    grid-template-columns: repeat(2, 1fr);
  }

  .action-btn {
    padding: 8px 12px;
    font-size: 0.8rem;
    min-height: 40px;
  }
}
</style>