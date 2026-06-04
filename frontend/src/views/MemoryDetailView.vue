<template>
  <div class="memory-detail-view">
    <div class="view-header">
      <button class="back-btn" @click="goBack">
        ← {{ $t('zh_006c4b') }}
      </button>
      <div class="view-actions">
        <!-- P38 (round 3): 5 个按钮层级化 — 之前全用 accent 实色 → 5 个"假 primary"同时喊叫。
             改为：编辑 = primary（最常用操作） / 展开 + 分享 + 历史 = ghost 描边（次级 utility） / 删除 = danger（破坏性，红字 + 红描边）。
             注：折叠/展开按钮 + 分享 + 历史 都是"看+导航"类，不改变记忆内容 → ghost 更合适。 -->
        <button class="action-btn action-btn--ghost" @click="toggleExpand">
          {{ isExpanded ? $t('zh_006673') : $t('zh_0065b0') }}
        </button>
        <button class="action-btn action-btn--ghost" @click="router.push(`/memory/${route.params.id}/history`)">{{ $t('zh_006482') }}</button>
        <button class="action-btn action-btn--ghost" @click="showShareModal = true">{{ $t('zh_00644b') }}</button>
        <button class="action-btn action-btn--primary" @click="showEditModal = true">{{ $t('zh_006a5b') }}</button>
        <button class="action-btn action-btn--danger" @click="confirmDelete = true">删除</button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="skeleton-card"></div>
    </div>

    <div v-else-if="error" class="error-state">
      <h3>{{ $t('zh_ac1a4d') }}</h3>
      <p>{{ error }}</p>
      <button class="action-btn" @click="loadMemory">{{ $t('zh_006cc1') }}</button>
    </div>

    <div v-else-if="memory" class="memory-content">
      <div class="memory-header">
        <div class="title-row">
          <h1>{{ memory.title }}</h1>
          <span class="memory-type" :class="'type-' + memory.type">{{ memory.type }}</span>
          <span v-if="memory.archived" class="archived-badge">{{ $t('zh_0d2307') }}</span>
        </div>
        <div class="meta-row">
          <HealthBadge v-if="healthDisplay" :score="healthDisplay.health_score" :color="healthDisplay.color" />
          <!-- P38 r16: strength bar → 44px ring，对齐 MemoryCard r15。
               旧 strength-bar + meta-text 是"线性进度条 + 文字"双重表达，
               与 MemoryCard r15 收尾后的"单一 ring"语言不一致，用户在 list→detail
               之间会感到"换了一套表达"。ring 配 tier 颜色 + 中心数字，一眼可读。 -->
          <div
            class="strength-ring"
            :class="['strength-ring--' + strengthTier, { 'strength-ring--perfect': strengthPercent === 100 }]"
            :title="`强度 ${strengthPercent}%`"
            role="img"
            :aria-label="`记忆强度 ${strengthPercent}%`"
          >
            <svg class="strength-ring__svg" viewBox="0 0 36 36" aria-hidden="true">
              <circle class="strength-ring__track" cx="18" cy="18" r="15.5" />
              <circle
                class="strength-ring__fill"
                cx="18" cy="18" r="15.5"
                :stroke-dasharray="`${strengthPercent}, 100`"
              />
            </svg>
            <span class="strength-ring__num">{{ strengthPercent }}</span>
          </div>
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
          <h4>{{ $t('zh_00674e') }}</h4>
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
        <h4>{{ $t('zh_ec5ffb') }}</h4>
        <div class="health-breakdown">
          <div class="breakdown-item">
            <span class="breakdown-label">强度</span>
            <span class="breakdown-value">{{ healthData.breakdown.strength_score }}</span>
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label">{{ $t('zh_006636') }}</span>
            <span class="breakdown-value">{{ healthData.breakdown.age_score }}</span>
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label">{{ $t('zh_006763') }}</span>
            <span class="breakdown-value">{{ healthData.breakdown.concepts_score }}</span>
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label">{{ $t('zh_0066c6') }}</span>
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
      :title="$t('zh_c0c40a')"
      :message="`${$t('zh_794546')}？${$t('zh_974456')}。`"
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

// P38 r16: strength ring helpers — 与 MemoryCard r15 完全一致
const strengthPercent = computed(() => {
  const raw = (memory.value?.strength || 0) * 10
  if (Number.isNaN(raw)) return 0
  return Math.max(0, Math.min(100, Math.round(raw)))
})

const strengthTier = computed(() => {
  if (strengthPercent.value >= 70) return 'high'
  if (strengthPercent.value >= 40) return 'mid'
  return 'low'
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
  box-shadow: var(--shadow-press);
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
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.6875rem;            /* 11px — small caps vibe, 对齐 MemoryCard */
  font-weight: 600;
  padding: 4px 10px 4px 8px;
  border-radius: 6px;              /* P38 r16: 12px → 6px，对齐 MemoryCard */
  letter-spacing: 0.06em;
  white-space: nowrap;
  text-transform: uppercase;       /* P38 r16: capitalize → uppercase，对齐 MemoryCard */
  border: 1px solid transparent;
}

/* P38 r16: ::before dot prefix — 与 MemoryCard .card-type 完全一致。
   之前 MemoryDetailView 的 type chip 没有"色块前的小圆点"，
   用户在 list 卡片看到 dot+chip，在 detail 页面只看 chip，视觉跳变。
   复用同样的 dot prefix 让"type"在两处是同一个表达。 */
.memory-type::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.85;
  flex-shrink: 0;
}

/* P38 r16: type-chip 补 1px border + color-mix（同 MemoryCard 配方）。
   之前只有 bg+color，无 border → 在 tag-bg 卡片上边界感"糊"，
   加 1px 与 chip 文字同色 18% 透明度的 border 提锐度。 */
.type-pattern     { background: var(--type-pattern-bg);     color: var(--type-pattern-text);     border-color: color-mix(in srgb, var(--type-pattern-text) 18%, transparent); }
.type-fact        { background: var(--type-fact-bg);        color: var(--type-fact-text);        border-color: color-mix(in srgb, var(--type-fact-text) 18%, transparent); }
.type-preference  { background: var(--type-preference-bg);  color: var(--type-preference-text);  border-color: color-mix(in srgb, var(--type-preference-text) 18%, transparent); }
.type-bug         { background: var(--type-bug-bg);         color: var(--type-bug-text);         border-color: color-mix(in srgb, var(--type-bug-text) 18%, transparent); }
.type-workflow    { background: var(--type-workflow-bg);    color: var(--type-workflow-text);    border-color: color-mix(in srgb, var(--type-workflow-text) 18%, transparent); }
.type-architecture{ background: var(--type-architecture-bg);color: var(--type-architecture-text);border-color: color-mix(in srgb, var(--type-architecture-text) 18%, transparent); }

.archived-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.6875rem;            /* P38 r16: 0.7rem → 0.6875rem，对齐 type chip 节奏 */
  font-weight: 600;
  padding: 4px 8px;
  background: var(--tag-bg);
  border-radius: 6px;              /* P38 r16: 4px → 6px，对齐全站 badge 圆角 */
  color: var(--text-secondary);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

/* P38 r16: archived-badge ::before 复用"小圆点"设计语言（与 type chip 一致） */
.archived-badge::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.7;
  flex-shrink: 0;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* P38 r16: strength ring — 与 MemoryCard r15 同一规格（44px, 0.78rem/700, stroke 3.5）
   之前 .strength-bar + .strength-fill 是 6px 高线性进度条 + 文字，与 MemoryCard 的 44px ring
   视觉权重差距巨大（list 强 / detail 弱）。统一为 ring 让"强度"在 list→detail 是同一锚点。 */
.strength-ring {
  position: relative;
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.strength-ring__svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.strength-ring__track {
  fill: none;
  stroke: var(--tag-bg);
  stroke-width: 3.5;
}

.strength-ring__fill {
  fill: none;
  stroke-width: 3.5;
  stroke-linecap: round;
  transition: stroke-dasharray 0.5s cubic-bezier(0.25, 0.1, 0.25, 1), stroke 0.3s ease;
}

.strength-ring--high .strength-ring__fill { stroke: var(--strength-high-fill); }
.strength-ring--mid  .strength-ring__fill { stroke: var(--strength-mid-fill); }
.strength-ring--low  .strength-ring__fill { stroke: var(--strength-low-fill); }

/* P38 r24: 与 MemoryCard 同源 — high tier 微光晕 + 100% 满级里程碑环。
   同步 list/detail 两个视图的"强度"视觉语言，避免 P38 r16 刚统一完又被本轮遗漏。 */
.strength-ring--high {
  filter: drop-shadow(0 0 4px color-mix(in srgb, var(--strength-high-fill) 40%, transparent));
}

.strength-ring--perfect {
  box-shadow: inset 0 0 0 2px color-mix(in srgb, var(--strength-high-fill) 50%, transparent),
              0 0 0 1px color-mix(in srgb, var(--strength-high-fill) 30%, transparent);
  border-radius: 50%;
}

.strength-ring__num {
  position: absolute;
  font-size: 0.78rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
  color: var(--primary);
  line-height: 1;
}

.strength-ring--high .strength-ring__num { color: var(--strength-high-ink); }
.strength-ring--mid  .strength-ring__num { color: var(--strength-mid-ink); }
.strength-ring--low  .strength-ring__num { color: var(--strength-low-ink); }

.memory-body {
  margin-bottom: 20px;
}

.memory-body.expanded .card-content {
  max-height: none;
}

/* P38 r24: 阅读列宽 + 排版打磨 — 旧 .card-content 是 0.95rem / line-height 1.6，
   在 900px 宽的 .memory-detail-view 里行可达 ~150 字符，远超可读舒适区（中文 ≤45 字符/行，
   英文 ≤75 字符/行）。Geist 风格长文阅读最佳行宽 60-75 字符。
   改：font-size 0.95rem → 1rem（接近 Apple 阅读器 17px），line-height 1.6 → 1.7（Vercel/Geist 偏好），
   color 用 --primary 而非 --text-primary（token 治理，之前是错引），并加 max-width: 70ch
   限制单行最大字符数。中文 1ch ≈ 1 字符，70ch ≈ 70 字符 → 体感舒适。 */
.card-content {
  font-size: 1rem;
  line-height: 1.7;
  color: var(--primary);
  max-width: 70ch;
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