<template>
  <!-- P38 r14: a11y — role/aria-modal/aria-labelledby + Esc to close
       P38 r29: 包裹 .modal-fade transition — 共享 main.css 全局 modal-pop-in. -->
  <transition name="modal-fade">
  <div class="share-modal-overlay" @click.self="$emit('close')" @keydown.esc="$emit('close')">
    <div
      class="share-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="share-modal-title"
    >
      <div class="modal-header">
        <h3 id="share-modal-title">🔗 {{ $t('zh_aab872') }}</h3>
        <button class="close-btn" @click="$emit('close')" aria-label="$t('zh_77e130')">✕</button>
      </div>

      <div class="modal-body">
        <!-- Create share link section -->
        <div class="share-section">
          <div class="section-label">{{ $t('zh_cb8ce6') }}</div>
          <div class="access-options">
            <button
              v-for="opt in accessOptions"
              :key="opt.value"
              class="access-btn"
              :class="{ active: accessLevel === opt.value }"
              @click="accessLevel = opt.value"
            >
              <span class="access-icon">{{ opt.icon }}</span>
              <span class="access-name">{{ opt.label }}</span>
              <span class="access-desc">{{ opt.desc }}</span>
            </button>
          </div>
        </div>

        <div class="share-section">
          <div class="section-label">{{ $t('zh_ccf8c3') }}</div>
          <div class="expires-options">
            <button
              v-for="opt in expiresOptions"
              :key="opt.value"
              class="expires-btn"
              :class="{ active: expiresIn === opt.value }"
              @click="expiresIn = opt.value"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <div class="share-section">
          <div class="section-label">
            <label class="password-toggle">
              <input type="checkbox" v-model="usePassword" />
              <span>{{ $t('zh_b0b947') }}</span>
            </label>
          </div>
          <input
            v-if="usePassword"
            v-model="password"
            type="password"
            placeholder="$t('zh_513c9b')"
            class="password-input"
          />
        </div>

        <button
          class="create-share-btn"
          :disabled="creating"
          @click="createShare"
        >
          {{ creating ? '生成中...' : '🔗 生成分享链接' }}
        </button>

        <!-- Result -->
        <div v-if="shareResult" class="share-result">
          <div class="result-label">{{ $t('zh_aab9a9') }}</div>
          <div class="result-url-row">
            <input
              ref="urlInput"
              :value="shareResult.share_url"
              readonly
              class="result-url"
            />
            <button class="copy-btn" @click="copyUrl">
              {{ copied ? '✅ 已复制' : '📋 复制' }}
            </button>
          </div>
          <div class="result-meta">
            <span class="meta-item">
              {{ shareResult.access_level === 'view' ? '👁 仅查看' : shareResult.access_level === 'comment' ? '💬 可评论' : '✏️ 可编辑' }}
            </span>
            <span v-if="shareResult.expires_at" class="meta-item">
              ⏰ {{ formatDate(shareResult.expires_at) }} {{ $t('zh_006c5a') }}
            </span>
            <span v-if="shareResult.pii_masked" class="meta-item">🔒 PII {{ $t('zh_0d2761') }}</span>
          </div>

          <!-- QR Code area -->
          <div class="qr-section">
            <button class="qr-toggle" @click="showQR = !showQR">
              {{ showQR ? '隐藏二维码' : '📱 显示二维码' }}
            </button>
            <div v-if="showQR" class="qr-placeholder">
              <div class="qr-box">
                <p class="qr-text">QR Code</p>
                <p class="qr-url">{{ shareResult.share_url }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Existing shares management -->
      <div class="modal-footer">
        <div class="shares-header" @click="showExisting = !showExisting">
          <span>📂 {{ $t('zh_a2fd47') }} ({{ existingShares.length }})</span>
          <span>{{ showExisting ? '▲' : '▼' }}</span>
        </div>
        <transition name="expand">
          <div v-if="showExisting" class="existing-shares">
            <div v-if="loadingShares" class="shares-loading">加载中...</div>
            <div v-else-if="existingShares.length === 0" class="shares-empty">{{ $t('zh_872abc') }}</div>
            <div v-else class="shares-list">
              <div v-for="share in existingShares" :key="share.share_id" class="share-item">
                <div class="share-item-info">
                  <span class="share-item-level" :class="'level-' + share.access_level">
                    {{ share.access_level }}
                  </span>
                  <span class="share-item-id">{{ share.share_id.slice(0, 8) }}...</span>
                  <span v-if="share.expires_at" class="share-item-expires">
                    {{ formatDate(share.expires_at) }}
                  </span>
                </div>
                <button
                  class="revoke-btn"
                  :disabled="revoking === share.share_id"
                  @click="revokeShare(share.share_id)"
                >
                  {{ revoking === share.share_id ? '...' : '撤销' }}
                </button>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { request } from '@/api/index'
import { useToast } from '@/composables/useToast'

interface ShareResult {
  share_id: string
  share_url: string
  access_level: string
  expires_at: string | null
  password_protected: boolean
  pii_masked: boolean
}

interface ShareInfo {
  share_id: string
  memory_id: string
  memory_title: string
  access_level: string
  expires_at: string | null
  created_at: string
}

const props = defineProps<{
  memoryId: string
}>()

defineEmits<{
  (e: 'close'): void
}>()

const toast = useToast()

const accessLevel = ref<'view' | 'comment' | 'edit'>('view')
const expiresIn = ref('7d')
const usePassword = ref(false)
const password = ref('')
const creating = ref(false)
const shareResult = ref<ShareResult | null>(null)
const copied = ref(false)
const showQR = ref(false)
const showExisting = ref(false)
const existingShares = ref<ShareInfo[]>([])
const loadingShares = ref(false)
const revoking = ref<string | null>(null)
const urlInput = ref<HTMLInputElement | null>(null)

const accessOptions = [
  { value: 'view' as const, icon: '👁', label: '仅查看', desc: '只能阅读' },
  { value: 'comment' as const, icon: '💬', label: '可评论', desc: '可添加评论' },
  { value: 'edit' as const, icon: '✏️', label: '可编辑', desc: '可修改内容' },
]

const expiresOptions = [
  { value: '1h', label: '1 小时' },
  { value: '1d', label: '1 天' },
  { value: '7d', label: '7 天' },
  { value: '30d', label: '30 天' },
  { value: 'never', label: '永不' },
]

async function createShare() {
  creating.value = true
  try {
    const body: any = {
      access_level: accessLevel.value,
      expires_in: expiresIn.value,
    }
    if (usePassword.value && password.value) {
      body.password = password.value
    }
    shareResult.value = await request<ShareResult>(`/memories/${props.memoryId}/share`, {
      method: 'POST',
      body: JSON.stringify(body),
    })
    toast.success('分享链接已生成')
    loadExistingShares()
  } catch (e: any) {
    toast.error(e.message || '生成分享链接失败')
  } finally {
    creating.value = false
  }
}

async function copyUrl() {
  if (!shareResult.value) return
  try {
    await navigator.clipboard.writeText(shareResult.value.share_url)
    copied.value = true
    toast.success('已复制到剪贴板')
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // fallback: select input
    urlInput.value?.select()
    document.execCommand('copy')
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  }
}

async function loadExistingShares() {
  loadingShares.value = true
  try {
    const res = await request<{ shares: ShareInfo[] }>('/shares')
    existingShares.value = res.shares
  } catch {
    // silent
  } finally {
    loadingShares.value = false
  }
}

async function revokeShare(shareId: string) {
  revoking.value = shareId
  try {
    await request(`/shares/${shareId}`, { method: 'DELETE' })
    existingShares.value = existingShares.value.filter(s => s.share_id !== shareId)
    toast.success('分享链接已撤销')
  } catch (e: any) {
    toast.error(e.message || '撤销失败')
  } finally {
    revoking.value = null
  }
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleString('zh-CN')
  } catch {
    return dateStr
  }
}

onMounted(() => {
  loadExistingShares()
})
</script>

<style scoped>
.share-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.share-modal {
  background: var(--card);
  border-radius: 16px;
  width: 480px;
  max-width: 95vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-modal);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  /* P38 r9: var(--text) 不存在（设计系统用 --primary 作为文字主色） */
  color: var(--primary);
}

/* P38 (round 4): close-btn 全站统一 — Geist ghost 32×32 圆角方块
   （与 DedupModal / MemoryDiffModal / WhatsNewModal 完全同款）。
   之前的 4px 8px padding + 无边框版本 hit-area 仅 ~24px，移动端难按。 */
.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.close-btn:hover {
  background: var(--tag-bg);
  border-color: var(--border-strong);
  color: var(--primary);
}

.modal-body {
  padding: 16px 20px;
}

.share-section {
  margin-bottom: 16px;
}

.section-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.access-options {
  display: flex;
  gap: 8px;
}

.access-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 8px;
  border: 1px solid var(--border);
  border-radius: 10px;
  /* P38 r9: var(--bg) 是页面底色 (#fafafa light / #0a0a0a dark)，不是 card 表面。
     卡片表面应用 --card (#fff light / #171717 dark)，否则 light 模式下 access-btn
     灰底与 modal 白底（也是 --card）有 ~5% 灰度差。 */
  background: var(--card);
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: var(--font);
}

/* P38 (round 7): 5% accent 浅蓝背景 + 0.5px 蓝边 — 之前硬编码 Apple rgba(0,122,255,0.05) +
   var(--primary, #007aff) fallback（语义错配：--primary 是文字主色而非品牌色）。
   现在 --accent-soft 自动跟随 light/dark 主题。 */
.access-btn.active {
  border-color: var(--accent);
  background: var(--accent-soft);
}

.access-icon {
  font-size: 1.2rem;
}

.access-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--primary);
}

.access-desc {
  font-size: 0.65rem;
  color: var(--text-secondary);
}

.expires-options {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.expires-btn {
  padding: 6px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  font-size: 0.8rem;
  cursor: pointer;
  font-family: var(--font);
  color: var(--primary);
  transition: all 0.15s ease;
}

/* P38 (round 7): 见 .access-btn.active — 同源 token 化 */
.expires-btn.active {
  border-color: var(--accent);
  background: var(--accent-soft);
  color: var(--accent);
}

.password-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.password-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 0.85rem;
  font-family: var(--font);
  margin-top: 8px;
  box-sizing: border-box;
}

.password-input:focus {
  outline: none;
  /* P38 r9: --primary 是文字主色（#171717 ink），不是品牌色。
     焦点描边应该是 accent（蓝），与全站 input focus 一致。 */
  border-color: var(--accent);
}

.create-share-btn {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 10px;
  /* P38 r9: 同上 — 这里是关键 CTA 按钮（生成分享链接），主色背景应该是
     品牌蓝 accent 而不是文字墨色。修复后 light/dark 都跟随主题。 */
  background: var(--accent);
  color: var(--card);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--font);
  transition: opacity 0.15s ease;
}

.create-share-btn:hover {
  opacity: 0.9;
}

.create-share-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.share-result {
  margin-top: 16px;
  padding: 14px;
  /* P38 r9: 浅灰底 fill，--tag-bg 是设计系统的"subtle fill surface" 语义 token */
  background: var(--tag-bg);
  border-radius: 10px;
}

.result-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.result-url-row {
  display: flex;
  gap: 8px;
}

.result-url {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 0.8rem;
  font-family: var(--font-mono);
  background: var(--card);
  color: var(--primary);
}

.copy-btn {
  padding: 8px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
  font-size: 0.8rem;
  cursor: pointer;
  white-space: nowrap;
  font-family: var(--font);
  color: var(--primary);
}

.copy-btn:hover {
  background: var(--tag-bg);
}

.result-meta {
  display: flex;
  gap: 12px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.meta-item {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.qr-section {
  margin-top: 12px;
}

.qr-toggle {
  border: none;
  background: none;
  /* P38 r9: 链接色用 --accent，--primary 是文字墨色 */
  color: var(--accent);
  font-size: 0.8rem;
  cursor: pointer;
  font-family: var(--font);
  padding: 0;
}

.qr-toggle:hover {
  text-decoration: underline;
}

.qr-placeholder {
  margin-top: 10px;
}

.qr-box {
  width: 160px;
  height: 160px;
  border: 2px dashed var(--border);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.qr-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin: 0;
}

.qr-url {
  font-size: 0.55rem;
  color: var(--text-secondary);
  margin: 0;
  text-align: center;
  padding: 0 8px;
  word-break: break-all;
}

.modal-footer {
  border-top: 1px solid var(--border);
}

.shares-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.shares-header:hover {
  background: var(--tag-bg);
}

.existing-shares {
  max-height: 200px;
  overflow-y: auto;
}

.shares-loading,
.shares-empty {
  padding: 16px 20px;
  text-align: center;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.shares-list {
  padding: 0 20px 12px;
}

.share-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
}

.share-item:last-child {
  border-bottom: none;
}

.share-item-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.share-item-level {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.level-view {
  background: #e8f5e9;
  color: #2e7d32;
}

.level-comment {
  background: #e3f2fd;
  color: #1565c0;
}

.level-edit {
  background: #fff3e0;
  color: #e65100;
}

.share-item-id {
  font-size: 0.75rem;
  font-family: var(--font-mono);
  color: var(--text-secondary);
}

.share-item-expires {
  font-size: 0.7rem;
  color: var(--text-secondary);
}

.revoke-btn {
  padding: 4px 10px;
  border: 1px solid var(--error);
  border-radius: 6px;
  background: transparent;
  color: var(--error);
  font-size: 0.7rem;
  cursor: pointer;
  font-family: var(--font);
}

.revoke-btn:hover {
  /* P38 r9: --error-bg 已是设计系统的 error 软底色，dark 模式自动变 #3e1a1a */
  background: var(--error-bg);
}

.revoke-btn:disabled {
  opacity: 0.5;
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 200px;
}
</style>
