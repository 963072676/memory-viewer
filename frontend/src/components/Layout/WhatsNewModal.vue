<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div v-if="showModal" class="modal-overlay" @click.self="onClose">
        <div class="modal-container">
          <div class="modal-header">
            <h2>🎉 What's New</h2>
            <button class="close-btn" @click="onClose">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="changelog.length === 0" class="empty-changelog">
              暂无更新记录
            </div>
            <div v-else class="version-list">
              <div
                v-for="entry in changelog"
                :key="entry.version"
                class="version-entry"
              >
                <div class="version-header">
                  <span class="version-tag">v{{ entry.version }}</span>
                  <span class="version-date">{{ entry.date }}</span>
                </div>
                <h3 class="version-title">{{ entry.title }}</h3>
                <ul class="changes-list">
                  <li
                    v-for="(change, idx) in entry.changes"
                    :key="idx"
                    class="change-item"
                  >
                    <span
                      class="change-type"
                      :class="'type-' + change.type"
                    >
                      {{ typeLabel(change.type) }}
                    </span>
                    <div class="change-content">
                      <strong>{{ change.title }}</strong>
                      <p>{{ change.description }}</p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-primary" @click="onClose">知道了</button>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useChangelog } from '@/composables/useChangelog'

const { changelog, showModal, markAsRead } = useChangelog()

function onClose() {
  markAsRead()
}

function typeLabel(type: string): string {
  const map: Record<string, string> = {
    feature: '新功能',
    fix: '修复',
    improvement: '改进',
  }
  return map[type] || type
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--modal-backdrop);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 24px;
}

.modal-container {
  background: var(--card);
  border-radius: 16px;
  max-width: 640px;
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
}

.modal-header h2 {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--primary);
  margin: 0;
}

/* P38 (round 4): close-btn 全站统一 — Geist ghost 32×32 圆角方块
   （与 DedupModal / MemoryDiffModal / ShareModal 完全同款）。
   之前的 1.5rem font + 无边框版本 hit-area 不可控，移动端无视觉边界。 */
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
  overflow-y: auto;
  padding: 24px;
  flex: 1;
}

.empty-changelog {
  text-align: center;
  color: var(--text-secondary);
  padding: 40px 0;
}

.version-entry {
  margin-bottom: 32px;
}

.version-entry:last-child {
  margin-bottom: 0;
}

.version-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.version-tag {
  font-size: 0.85rem;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 20px;
  background: var(--accent);
  color: white;
}

.version-date {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.version-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 12px;
}

.changes-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.change-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  background: var(--bg);
}

.change-type {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  white-space: nowrap;
  flex-shrink: 0;
  margin-top: 2px;
}

.type-feature {
  background: #e8f5e9;
  color: #2e7d32;
}

.type-fix {
  background: #fff3e0;
  color: #e65100;
}

.type-improvement {
  background: #e3f2fd;
  color: #1565c0;
}

[data-theme='dark'] .type-feature {
  background: #1b3a1b;
  color: #66bb6a;
}

[data-theme='dark'] .type-fix {
  background: #3e2a0a;
  color: #ffcc80;
}

[data-theme='dark'] .type-improvement {
  background: #0d2744;
  color: #64b5f6;
}

.change-content strong {
  font-size: 0.85rem;
  color: var(--primary);
}

.change-content p {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 2px;
  line-height: 1.5;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border);
  text-align: right;
}

.btn-primary {
  padding: 10px 24px;
  border: none;
  border-radius: 10px;
  background: var(--accent);
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: var(--accent-hover);
}

/* Transition */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .modal-container {
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
