<template>
  <div class="memory-card" :class="{ expanded: isExpanded, archived: memory.archived }">
    <label class="select-checkbox" @click.stop>
      <input type="checkbox" :checked="isSelected" @change="store.toggleSelect(memory.id)" />
      <span class="checkmark"></span>
    </label>
    <div class="card-header" @click="toggle">
      <div class="card-title-row">
        <h3 class="card-title">
          <router-link :to="`/memory/${memory.id}`" class="memory-title-link" @click.stop>
            {{ memory.title }}
          </router-link>
          <span v-if="memory.archived" class="archived-badge">{{ $t('i18n.archived') }}</span>
        </h3>
        <div class="card-right">
          <span v-if="healthDisplay" class="health-dot" :class="'dot-' + healthDisplay.color" :title="'健康度: ' + healthDisplay.health_score"></span>
          <HealthBadge v-if="healthDisplay" :score="healthDisplay.health_score" :color="healthDisplay.color" />
          <span class="card-type" :class="'type-' + memory.type">{{ memory.type }}</span>
        </div>
      </div>
      <p class="card-summary" v-if="!isExpanded">{{ truncatedContent }}</p>
      <div class="card-tags" v-if="!isExpanded && memory.tags && memory.tags.length">
        <span
          v-for="tag in memory.tags"
          :key="tag"
          class="tag-capsule"
          @click.stop="$emit('tag-click', tag)"
        >{{ tag }}</span>
      </div>
      <div class="card-meta" v-if="!isExpanded">
        <!-- P38 r15: Strength 视觉锚点升级 — 直径 38px → 44px，字号 0.7rem → 0.78rem。
             之前 ring 在缩略视图里"看起来像绿点"，数字小到看不清是 70 还是 76。
             增大环 + 加大数字（保持 tabular-nums 等宽）让 strength 真正成为每张卡片的视觉锚点。
             删除右侧冗余 .meta-text (数字 + 百分号 与 ring 内数字 + 标题 aria-label 重复)。
             仅保留 ring 单一表达，更克制（v.s. P38 r13 之前 ring + bar + text 三种）。 -->
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
              cx="18"
              cy="18"
              r="15.5"
              :stroke-dasharray="`${strengthPercent}, 100`"
            />
          </svg>
          <span class="strength-ring__num">{{ strengthPercent }}</span>
        </div>
      </div>
    </div>
    <transition name="expand">
      <div class="card-body" v-if="isExpanded">
        <div class="card-content" v-html="sanitizedContent"></div>
        <div class="card-details">
          <div class="detail-row" v-if="memory.concepts.length">
            <span class="detail-label">{{ $t('en_concepts') }}</span>
            <div class="tags">
              <span class="tag" v-for="c in memory.concepts" :key="c">{{ c }}</span>
            </div>
          </div>
          <div class="detail-row" v-if="memory.files.length">
            <span class="detail-label">{{ $t('en_files') }}</span>
            <div class="tags">
              <span class="tag file-tag" v-for="f in memory.files" :key="f">{{ f }}</span>
            </div>
          </div>
          <!-- F46: Tags section in expanded body -->
          <div class="detail-row">
            <span class="detail-label">{{ $t('i18n.label') }}</span>
            <TagManager
              :tags="memory.tags || []"
              :all-tags="allTagNames"
              @update:tags="onTagsUpdate"
            />
          </div>
          <div class="detail-row">
            <span class="detail-label">{{ $t('en_strength') }}</span>
            <span>{{ memory.strength * 10 }}%</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">{{ $t('en_updated') }}</span>
            <span>{{ formatDate(memory.updatedAt) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">{{ $t('en_created') }}</span>
            <span>{{ formatDate(memory.createdAt) }}</span>
          </div>
          <!-- Health breakdown (F-20) -->
          <div class="detail-row" v-if="healthDisplay">
            <span class="detail-label">{{ $t('i18n.health') }}</span>
            <span class="health-detail">
              {{ healthDisplay.health_score }}/100
              <span v-if="healthData" class="health-dim" :class="'health-' + healthDisplay.color">
                力{{ healthData.breakdown.strength_score }} ·
                龄{{ healthData.breakdown.age_score }} ·
                概{{ healthData.breakdown.concepts_score }} ·
                推{{ healthData.breakdown.recommendation_score }}
              </span>
              <span v-else class="health-dim" :class="'health-' + healthDisplay.color">
                ({{ $t('i18n.list_estimate') }})
              </span>
            </span>
          </div>
        </div>

        <!-- Decay chart (F-22) -->
        <DecayChart v-if="decayData" :data="decayData" />

        <!-- Related memories (F-19) -->
        <RelatedMemories :memory-id="memory.id" />

        <!-- F-34: AI Auto-Tagging & Summarization -->
        <div class="ai-section">
          <div class="ai-actions">
            <button
              class="action-btn ai-btn"
              :disabled="suggestTagsLoading"
              @click.stop="handleSuggestTags"
            >
              {{ suggestTagsLoading ? '⏳ 分析中...' : '✨ Suggest Tags' }}
            </button>
            <button
              class="action-btn ai-btn"
              :disabled="summarizeLoading"
              @click.stop="handleSummarize"
            >
              {{ summarizeLoading ? '⏳ 生成中...' : '📝 Summarize' }}
            </button>
          </div>

          <!-- Suggested tags as clickable chips -->
          <div v-if="suggestedTags.length > 0" class="ai-suggested-tags">
            <span class="ai-label">{{ $t('i18n.suggested') }}：</span>
            <span
              v-for="tag in suggestedTags"
              :key="tag"
              class="suggested-tag-chip"
              @click.stop="applySuggestedTag(tag)"
            >
              {{ tag }} +
            </span>
          </div>
          <div v-if="suggestTagsError" class="ai-error">{{ suggestTagsError }}</div>

          <!-- Summary display -->
          <div v-if="summary" class="ai-summary">
            <span class="ai-label">{{ $t('i18n.summarization') }}：</span>
            <p class="ai-summary-text">{{ summary }}</p>
          </div>
          <div v-if="summarizeError" class="ai-error">{{ summarizeError }}</div>
        </div>

        <div class="card-actions">
          <button
            class="action-btn archive-btn"
            :disabled="archiving"
            @click.stop="toggleArchive"
          >
            {{ archiving ? '处理中...' : (memory.archived ? '📂 取消归档' : '📦 归档') }}
          </button>
          <button
            class="action-btn"
            @click.stop="goToVersions"
          >
            📋 {{ $t('i18n.version_history') }}
          </button>
          <button
            class="action-btn compare-btn"
            @click.stop="$emit('compare', memory)"
          >
            🔍 {{ $t('i18n.compare') }}
          </button>
        </div>
      </div>
    </transition>
    <button
      type="button"
      class="expand-indicator"
      :aria-expanded="isExpanded"
      :aria-label="isExpanded ? $t('i18n.collapse') : $t('i18n.expand')"
      @click="toggle"
    >
      <span class="expand-indicator__text">
        {{ isExpanded ? $t('i18n.collapse') : $t('i18n.expand') }}
      </span>
      <span class="expand-indicator__icon" aria-hidden="true">{{ isExpanded ? '▲' : '▼' }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { AgentMemory, DecayResponse, HealthResponse } from '@/types'
import { formatDate, truncateText } from '@/utils/format'
import { archiveMemory, unarchiveMemory, getDecay, getHealth } from '@/api/agentmemory'
import { suggestTags, summarizeMemory } from '@/api/p8'
import { setMemoryTags } from '@/api/agentmemory'
import { useAgentMemoryStore } from '@/stores/agentmemory'
import { useToast } from '@/composables/useToast'
import HealthBadge from './HealthBadge.vue'
import DecayChart from './DecayChart.vue'
import RelatedMemories from './RelatedMemories.vue'
import TagManager from './TagManager.vue'

const props = defineProps<{
  memory: AgentMemory
  forceExpanded?: boolean | null
}>()

defineEmits<{
  (e: 'tag-click', tag: string): void
  (e: 'compare', memory: AgentMemory): void
}>()

const agentMemoryStore = useAgentMemoryStore()
const store = agentMemoryStore
const router = useRouter()
const toast = useToast()

const allTagNames = computed(() => agentMemoryStore.allTags.map(t => t.tag))
const isExpanded = ref(false)
const archiving = ref(false)
const decayData = ref<DecayResponse | null>(null)
const healthData = ref<HealthResponse | null>(null)
// F-34: AI auto-tagging & summarization state
const suggestedTags = ref<string[]>([])
const suggestTagsLoading = ref(false)
const suggestTagsError = ref('')
const summary = ref('')
const summarizeLoading = ref(false)
const summarizeError = ref('')

const isSelected = computed(() => store.selectedIds.has(props.memory.id))

const truncatedContent = computed(() => truncateText(props.memory.content, 100))

// P38: Strength visual anchor — clamp to [0,100], pick color tier
const strengthPercent = computed(() => {
  const raw = (props.memory.strength || 0) * 10
  if (Number.isNaN(raw)) return 0
  return Math.max(0, Math.min(100, Math.round(raw)))
})

const strengthTier = computed(() => {
  if (strengthPercent.value >= 70) return 'high'
  if (strengthPercent.value >= 40) return 'mid'
  return 'low'
})

// F43: Use pre-loaded health_score from list API, fallback to detailed data
const healthDisplay = computed(() => {
  if (healthData.value) {
    return { health_score: healthData.value.health_score, color: healthData.value.color }
  }
  if (props.memory.health_score != null && props.memory.health_color) {
    return { health_score: props.memory.health_score, color: props.memory.health_color }
  }
  return null
})

const sanitizedContent = computed(() => {
  return props.memory.content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
})

function toggle() {
  isExpanded.value = !isExpanded.value
}

// Load P3 data when expanded
watch(isExpanded, async (expanded) => {
  if (expanded && !decayData.value) {
    try {
      const [decay, health] = await Promise.all([
        getDecay(props.memory.id),
        getHealth(props.memory.id),
      ])
      decayData.value = decay
      healthData.value = health
    } catch (e) {
      console.error('Failed to load P3 data:', e)
    }
  }
})

// F-34: Suggest tags via AI
async function handleSuggestTags() {
  suggestTagsLoading.value = true
  suggestTagsError.value = ''
  suggestedTags.value = []
  try {
    const resp = await suggestTags(props.memory.id)
    suggestedTags.value = resp.suggested_tags.filter(
      t => !(props.memory.tags || []).includes(t)
    )
    if (suggestedTags.value.length === 0) {
      toast.info('没有新的标签建议')
    }
  } catch (e: any) {
    suggestTagsError.value = e.message || '获取标签建议失败'
    toast.error('获取标签建议失败: ' + (e.message || ''))
  } finally {
    suggestTagsLoading.value = false
  }
}

// F-34: Apply a single suggested tag
async function applySuggestedTag(tag: string) {
  const currentTags = [...(props.memory.tags || [])]
  if (currentTags.includes(tag)) return
  currentTags.push(tag)
  await onTagsUpdate(currentTags)
  suggestedTags.value = suggestedTags.value.filter(t => t !== tag)
}

// F-34: Summarize via AI
async function handleSummarize() {
  summarizeLoading.value = true
  summarizeError.value = ''
  summary.value = ''
  try {
    const resp = await summarizeMemory(props.memory.id)
    summary.value = resp.summary
  } catch (e: any) {
    summarizeError.value = e.message || '生成摘要失败'
    toast.error('生成摘要失败: ' + (e.message || ''))
  } finally {
    summarizeLoading.value = false
  }
}

async function toggleArchive() {
  archiving.value = true
  try {
    if (props.memory.archived) {
      await unarchiveMemory(props.memory.id)
      toast.success('已取消归档')
    } else {
      await archiveMemory(props.memory.id)
      toast.success('已归档')
    }
    await agentMemoryStore.refresh()
  } catch (e) {
    console.error('Archive toggle failed:', e)
    toast.error('归档操作失败')
  } finally {
    archiving.value = false
  }
}

function goToVersions() {
  router.push(`/memory/${props.memory.id}/versions`)
}

// F46: Save tags on change
async function onTagsUpdate(newTags: string[]) {
  try {
    await setMemoryTags(props.memory.id, newTags)
    // Update local memory object
    props.memory.tags = newTags
    toast.success('标签已更新')
    agentMemoryStore.loadAllTags()
  } catch (e) {
    console.error('Failed to update tags:', e)
    toast.error('标签更新失败')
  }
}

// React to forceExpanded prop (BUG-6: use watch instead of computed with side effects)
watch(() => props.forceExpanded, (newVal) => {
  if (newVal === true) isExpanded.value = true
  if (newVal === false) isExpanded.value = false
})
</script>

<style scoped>
.memory-card {
  position: relative;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  transition: box-shadow 0.3s ease, transform 0.3s ease;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.memory-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-3px);
}

.card-header {
  padding: 20px 20px 16px;
}

.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
  /* 给左侧 .select-checkbox (18px + 12px left offset) 让出空间,
     否则 checkbox 浮在标题文字之上,造成"遮挡"视觉 */
  padding-left: 30px;
}

.card-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--primary);
  line-height: 1.4;
  letter-spacing: -0.01em;
}

.card-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

/* BUG-5: compact health dot visible in collapsed state */
.health-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot-green { background: var(--health-good); }
.dot-yellow { background: var(--health-warn); }
.dot-red { background: var(--health-bad); }

.card-type {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.6875rem;            /* 11px — small caps vibe */
  font-weight: 600;
  padding: 4px 10px 4px 8px;
  border-radius: 6px;
  letter-spacing: 0.06em;
  white-space: nowrap;
  text-transform: uppercase;
  border: 1px solid transparent;   /* placeholder, filled by .type-* below */
}

/* P39: colored dot prefix — works as a visual anchor at a-glance scanning.
   The dot reuses the same hue as the text so the badge reads as one chip. */
.card-type::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.85;
  flex-shrink: 0;
}

.type-pattern     { background: var(--type-pattern-bg);     color: var(--type-pattern-text);     border-color: color-mix(in srgb, var(--type-pattern-text) 18%, transparent); }
.type-workflow    { background: var(--type-workflow-bg);    color: var(--type-workflow-text);    border-color: color-mix(in srgb, var(--type-workflow-text) 18%, transparent); }
.type-fact        { background: var(--type-fact-bg);        color: var(--type-fact-text);        border-color: color-mix(in srgb, var(--type-fact-text) 18%, transparent); }
.type-preference  { background: var(--type-preference-bg);  color: var(--type-preference-text);  border-color: color-mix(in srgb, var(--type-preference-text) 18%, transparent); }
.type-bug         { background: var(--type-bug-bg);         color: var(--type-bug-text);         border-color: color-mix(in srgb, var(--type-bug-text) 18%, transparent); }
.type-architecture{ background: var(--type-architecture-bg);color: var(--type-architecture-text);border-color: color-mix(in srgb, var(--type-architecture-text) 18%, transparent); }

.card-summary {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 6px;
}

/* P38 r15: Strength 视觉锚点 — 圆形 SVG ring + 中心数字 + 渐变颜色。
   r15 升级：直径 38px → 44px，字号 0.7rem → 0.78rem，stroke-width 3 → 3.5。
   让 ring 真正成为每张卡片的视觉锚点（之前在缩略视图里"看起来像绿点"）。 */
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
  transform: rotate(-90deg); /* dasharray 从 12 点钟方向开始 */
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

/* Tier 颜色（亮色 + Dark 模式自动通过变量切换） */
.strength-ring--high .strength-ring__fill { stroke: var(--strength-high-fill); }
.strength-ring--mid  .strength-ring__fill { stroke: var(--strength-mid-fill); }
.strength-ring--low  .strength-ring__fill { stroke: var(--strength-low-fill); }

/* P38 r24: high tier 微光晕 — 用 stroke 自带的 filter drop-shadow 给"≥70% 强健"
   记忆一个柔和的外发光，让它在缩略列表里"跳出来"（用户扫到时不会漏过）。
   mid/low 故意不加 — 视觉上"安静的弱化"才符合"弱化状态"语义。 */
.strength-ring--high {
  filter: drop-shadow(0 0 4px color-mix(in srgb, var(--strength-high-fill) 40%, transparent));
}

/* P38 r24: 100% 满级里程碑 — 在 ring 容器外圈加一道 2px 细金线
   （用 inset box-shadow 实现），表达"完美记忆"。仅 strengthPercent === 100 触发。 */
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
/* P38 (round 6): 数字颜色 token 化 — light 用 -ink（深色，4.5:1 对比度），
   dark 模式由 variables.css [data-theme='dark'] 块接管 -ink 切换到亮一档。 */
.strength-ring--high .strength-ring__num { color: var(--strength-high-ink); }
.strength-ring--mid  .strength-ring__num { color: var(--strength-mid-ink); }
.strength-ring--low  .strength-ring__num { color: var(--strength-low-ink); }

.card-body {
  padding: 0 20px 20px;
  border-top: 1px solid var(--border);
}

.card-content {
  font-size: 0.875rem;
  line-height: 1.7;
  color: var(--primary);
  margin: 16px 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.card-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 0.8rem;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-label {
  color: var(--text-secondary);
  min-width: 80px;
  font-weight: 500;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  font-size: 0.7rem;
  padding: 3px 8px;
  border-radius: 12px;
  background: var(--tag-bg);
  color: var(--text-secondary);
}

/* P40: file-tag 字体用 --font-mono token（Geist 一致性） */
.file-tag {
  font-family: var(--font-mono);
}

/* F46: Tag capsule in collapsed header */
.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}

.tag-capsule {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 12px;
  background: var(--tag-bg);
  color: var(--accent);
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.tag-capsule:hover {
  background: var(--border);
}

.health-detail {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.health-dim {
  font-size: 0.65rem;
  font-weight: 400;
  color: var(--text-secondary);
}

.health-green { color: var(--health-good); }
.health-yellow { color: var(--health-warn); }
.health-red { color: var(--health-bad); }

/* P38 r34: expand-indicator 升级 — div → <button> + 文字 label + 顶部 hairline.
   旧实现只是一个 4px 高的 ▼, 用户看不到"可点击", hover 也只有背景变色 (太弱).
   新实现: 整条变成一个 ghost 按钮, 文字+icon 同行, 顶部 1px border 与 card-body 视觉分隔,
   hover 时 icon 跳动 1px (微动效), 让"点击展开"语义一眼可读. */
.expand-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 8px 12px;
  font-size: 0.72rem;
  font-family: var(--font);
  font-weight: 500;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-top: 1px solid var(--border);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  -webkit-tap-highlight-color: transparent;
}

.expand-indicator:hover {
  background: var(--tag-bg);
  color: var(--primary);
}

.expand-indicator:hover .expand-indicator__icon {
  /* hover 时 icon 微微下移 1px, 强化"可点击"反馈 */
  transform: translateY(1px);
}

.expand-indicator__text {
  /* 占位用 — 文字 "展开" / "折叠" */
  letter-spacing: 0.02em;
}

.expand-indicator__icon {
  font-size: 0.7rem;
  line-height: 1;
  display: inline-block;
  transition: transform 0.15s ease;
}

/* P38 r34: expanded 状态下 icon 朝上 — 保持 transition 平滑, 不抖动 */
.memory-card.expanded .expand-indicator__icon {
  transform: translateY(-1px);
}

.select-checkbox {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 5;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.select-checkbox input {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--accent);
}

/* Archive styles (F-15) */
.memory-card.archived {
  opacity: 0.7;
}

.archived-badge {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 8px;
  background: var(--tag-bg);
  color: var(--text-secondary);
  margin-left: 8px;
  vertical-align: middle;
}

.card-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.action-btn {
  padding: 6px 14px 6px 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  color: var(--primary);
  font-size: 0.75rem;
  font-family: var(--font);
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.action-btn:hover {
  background: var(--tag-bg);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Expand animation */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 500px;
}

/* F-34: AI Section styles */
.compare-btn {
  border-color: var(--accent);
  color: var(--accent);
}

.compare-btn:hover:not(:disabled) {
  background: var(--accent);
  /* P38 r12: color: white 硬编码 → var(--card), 与 r11 sweep 同源 */
  color: var(--card);
}

.ai-section {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.ai-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.ai-btn {
  border-color: var(--accent);
  color: var(--accent);
}

.ai-btn:hover:not(:disabled) {
  background: var(--accent);
  /* P38 r12: color: white 硬编码 → var(--card), 与 r11 sweep 同源 */
  color: var(--card);
}

.ai-suggested-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  padding: 8px 10px;
  background: var(--tag-bg);
  border-radius: 8px;
}

.ai-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-right: 4px;
}

.suggested-tag-chip {
  font-size: 0.7rem;
  padding: 3px 10px;
  border-radius: 12px;
  background: var(--accent);
  /* P38 r12: color: white 硬编码 → var(--card), 与 r11 sweep 同源 */
  color: var(--card);
  cursor: pointer;
  transition: background 0.2s, transform 0.15s;
  white-space: nowrap;
  user-select: none;
}

.suggested-tag-chip:hover {
  background: var(--primary);
  transform: scale(1.05);
}

.ai-summary {
  margin-bottom: 12px;
  padding: 10px 12px;
  background: var(--tag-bg);
  border-radius: 8px;
  border-left: 3px solid var(--accent);
}

.ai-summary-text {
  font-size: 0.8rem;
  line-height: 1.6;
  color: var(--primary);
  margin: 4px 0 0;
}

.ai-error {
  font-size: 0.75rem;
  /* P38 r17: 改 hardcoded #ef4444 + rgba(239, 68, 68, 0.08) → --error-text / --error-bg.
     此前 dark 模式 --error-bg = #3e1a1a, 但 hardcoded 0.08 alpha 不会跟随, 
     dark 模式下错误提示几乎看不见. 改 token 后两套主题都走 --error-bg. */
  color: var(--error-text);
  padding: 6px 10px;
  background: var(--error-bg);
  border-radius: 6px;
  margin-bottom: 8px;
}

.memory-title-link {
  color: inherit;
  text-decoration: none;
}

.memory-title-link:hover {
  text-decoration: underline;
  color: var(--accent);
}

/* Responsive */
@media (max-width: 767px) {
  .memory-card {
    padding: 12px;
  }

  .card-title-row {
    flex-wrap: wrap;
    gap: 8px;
  }

  .card-title {
    font-size: 0.9rem;
  }

  .card-summary {
    font-size: 0.8rem;
    -webkit-line-clamp: 2;
  }

  .card-tags {
    gap: 4px;
  }

  .tag-capsule {
    font-size: 0.65rem;
    padding: 2px 8px;
  }

  .action-btn {
    padding: 8px 12px;
    font-size: 0.7rem;
    min-height: 36px;
    min-width: 36px;
  }

  /* P38: 小屏隐藏 ring，节省横向空间 */
  .strength-ring {
    width: 30px;
    height: 30px;
  }
  .strength-ring__num {
    font-size: 0.6rem;
  }
}
</style>
