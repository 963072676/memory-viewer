<template>
  <div class="compare-view">
    <div class="view-header">
      <h2 class="section-title">🔍 多 Agent 记忆对比</h2>
      <button class="action-btn primary" @click="compare" :disabled="!leftProfile || !rightProfile || loading">
        {{ loading ? '对比中...' : '开始对比' }}
      </button>
    </div>

    <div class="profile-select">
      <div class="select-group">
        <label>Left Profile</label>
        <select v-model="leftProfile" class="select-input">
          <option value="">选择 Profile</option>
          <option v-for="p in profiles" :key="p" :value="p">{{ p }}</option>
        </select>
      </div>
      <div class="select-group">
        <label>Right Profile</label>
        <select v-model="rightProfile" class="select-input">
          <option value="">选择 Profile</option>
          <option v-for="p in profiles" :key="p" :value="p">{{ p }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="result" class="compare-content">
      <!-- Similarity Score -->
      <div class="similarity-bar">
        <span class="similarity-label">相似度</span>
        <div class="similarity-track">
          <div class="similarity-fill" :style="{ width: (result.similarity_score * 100) + '%' }"></div>
        </div>
        <span class="similarity-value">{{ (result.similarity_score * 100).toFixed(1) }}%</span>
      </div>

      <!-- Three column layout -->
      <div class="three-column">
        <div class="column left-only">
          <h3>🅰️ 仅在左侧 ({{ result.left_only.length }})</h3>
          <div v-if="result.left_only.length === 0" class="empty-col">无独有记忆</div>
          <div v-for="item in result.left_only" :key="item.id" class="item-card">
            <div class="item-header">
              <span class="item-type">{{ item.type }}</span>
              <span v-if="item.strength" class="item-strength">{{ item.strength.toFixed(0) }}</span>
            </div>
            <strong class="item-title">{{ item.title }}</strong>
            <p class="item-content">{{ item.content }}</p>
            <div v-if="item.concepts.length" class="item-concepts">
              <span v-for="c in item.concepts.slice(0, 5)" :key="c" class="concept-tag">{{ c }}</span>
            </div>
          </div>
        </div>

        <div class="column common">
          <h3>🔗 共有 ({{ result.common.length }})</h3>
          <div v-if="result.common.length === 0" class="empty-col">无共有记忆</div>
          <div v-for="item in result.common" :key="item.id" class="item-card">
            <div class="item-header">
              <span class="item-type">{{ item.type }}</span>
              <span v-if="item.strength" class="item-strength">{{ item.strength.toFixed(0) }}</span>
            </div>
            <strong class="item-title">{{ item.title }}</strong>
            <p class="item-content">{{ item.content }}</p>
            <div v-if="item.concepts.length" class="item-concepts">
              <span v-for="c in item.concepts.slice(0, 5)" :key="c" class="concept-tag">{{ c }}</span>
            </div>
          </div>
        </div>

        <div class="column right-only">
          <h3>🅱️ 仅在右侧 ({{ result.right_only.length }})</h3>
          <div v-if="result.right_only.length === 0" class="empty-col">无独有记忆</div>
          <div v-for="item in result.right_only" :key="item.id" class="item-card">
            <div class="item-header">
              <span class="item-type">{{ item.type }}</span>
              <span v-if="item.strength" class="item-strength">{{ item.strength.toFixed(0) }}</span>
            </div>
            <strong class="item-title">{{ item.title }}</strong>
            <p class="item-content">{{ item.content }}</p>
            <div v-if="item.concepts.length" class="item-concepts">
              <span v-for="c in item.concepts.slice(0, 5)" :key="c" class="concept-tag">{{ c }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { compareProfiles, fetchProfiles } from '@/api/compare'
import type { CompareResult } from '@/api/compare'

const profiles = ref<string[]>([])
const leftProfile = ref('')
const rightProfile = ref('')
const loading = ref(false)
const result = ref<CompareResult | null>(null)

async function loadProfiles() {
  try {
    profiles.value = await fetchProfiles()
  } catch (e) {
    console.error('Failed to fetch profiles:', e)
  }
}

async function compare() {
  if (!leftProfile.value || !rightProfile.value) return
  loading.value = true
  try {
    result.value = await compareProfiles(leftProfile.value, rightProfile.value)
  } catch (e) {
    console.error('Compare failed:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => loadProfiles())
</script>

<style scoped>
.compare-view { padding-bottom: 40px; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
h2 { font-size: 1.5rem; font-weight: 600; color: var(--primary); }
/* P38 r20: section-title 左侧 3px accent bar — 与全站其他 view 同源 (r15 模式). */
h2.section-title { position: relative; padding-left: 12px; }
h2.section-title::before { content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%); width: 3px; height: 60%; background: var(--accent); border-radius: 0 2px 2px 0; }
h3 { font-size: 1rem; font-weight: 600; margin-bottom: 12px; color: var(--primary); }
.action-btn { padding: 8px 16px; border: 1px solid var(--border); border-radius: 8px; background: var(--card); color: var(--primary); cursor: pointer; font-size: 0.85rem; }
.action-btn:hover { background: var(--tag-bg); }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.action-btn.primary { background: var(--primary); color: var(--card); border-color: var(--primary); }
.profile-select { display: flex; gap: 16px; margin-bottom: 24px; }
.select-group { flex: 1; }
.select-group label { display: block; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 6px; font-weight: 500; }
.select-input { width: 100%; padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px; background: var(--card); color: var(--primary); font-size: 0.875rem; font-family: var(--font); }
.loading { text-align: center; padding: 40px; color: var(--text-secondary); }

/* Similarity bar */
.similarity-bar { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding: 12px 16px; background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); }
.similarity-label { font-size: 0.85rem; font-weight: 600; color: var(--text-secondary); }
.similarity-track { flex: 1; height: 8px; background: var(--tag-bg); border-radius: 4px; overflow: hidden; }
.similarity-fill { height: 100%; background: linear-gradient(90deg, var(--success-color, #4caf50), var(--accent)); border-radius: 4px; transition: width 0.3s ease; }
.similarity-value { font-size: 0.9rem; font-weight: 700; color: var(--primary); min-width: 50px; }

/* Three column layout */
.three-column { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.column { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; }
.column.left-only { border-left: 3px solid var(--diff-left-border); }
.column.common { border-left: 3px solid var(--diff-common-border); }
.column.right-only { border-left: 3px solid var(--diff-right-border); }
.empty-col { color: var(--text-secondary); font-size: 0.85rem; padding: 20px 0; text-align: center; }

/* Item cards */
.item-card { background: var(--bg); border-radius: var(--radius); padding: 12px; margin-bottom: 8px; }
.item-card:last-child { margin-bottom: 0; }
.item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.item-type { font-size: 0.7rem; padding: 2px 6px; border-radius: 8px; background: var(--tag-bg); color: var(--text-secondary); text-transform: uppercase; }
.item-strength { font-size: 0.7rem; font-weight: 600; color: var(--accent); }
.item-title { font-size: 0.85rem; color: var(--primary); display: block; margin-bottom: 4px; }
.item-content { font-size: 0.8rem; color: var(--text-secondary); margin: 0 0 8px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.item-concepts { display: flex; flex-wrap: wrap; gap: 4px; }
/* P38 r11: concept-tag 风格升级 — 旧实现 `background: accent + color: white + opacity: 0.8`
   有两个问题：(1) 硬编码 white 违反 token 契约 (P44 漏网)；
   (2) opacity: 0.8 让 tag 与父元素背景发生 alpha 混合，嵌套在 card 上时色相偏灰。
   新实现用 --accent-soft bg + accent 文字 + 1px 1级 border，Geist 风格"轻量 tag"语言。
   与 MemoryCard .card-type (P39 type chip 体系) 视觉语言一致。 */
.concept-tag {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 6px;
  background: var(--accent-soft);
  color: var(--accent);
  border: 1px solid color-mix(in srgb, var(--accent) 18%, transparent);
}

/* P38 (round 3): 三栏 diff 关系用 --diff-*-bg token 统一
   旧实现：3px 左边框 Material hex（#2196f3/#4caf50/#f44336） + dark mode 单独写一套 rgba
   新实现：token 自动跟随 light/dark 调色板，省 1 个 dark-mode media query。
   - left-only 冷静蓝（呼应 --accent）
   - common 稳定绿（呼应 --success）
   - right-only 暖橙（与 --type-fact 同源，差异=提示）*/
.column.left-only {
  border-left: 3px solid var(--diff-left-border);
  background: var(--diff-left-bg);
}
.column.common {
  border-left: 3px solid var(--diff-common-border);
  background: var(--diff-common-bg);
}
.column.right-only {
  border-left: 3px solid var(--diff-right-border);
  background: var(--diff-right-bg);
}

/* Responsive */
@media (max-width: 767px) {
  h2 { font-size: 1.2rem; }
  .profile-select { flex-direction: column; }
  .three-column { grid-template-columns: 1fr; }
  .similarity-bar { flex-wrap: wrap; }
}
</style>