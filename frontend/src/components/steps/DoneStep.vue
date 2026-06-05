<template>
  <div class="done-step">
    <div class="done-icon">🎉</div>
    <h2>{{ $t('zh_a88bee') }}！</h2>
    <p class="done-desc">{{ $t('zh_a9807e') }} Memory Viewer {{ $t('zh_a367b9') }}</p>
    <div class="quick-links">
      <div class="link-card" @click="$router.push('/agentmemory')">📝 {{ $t('zh_baaa2b') }}</div>
      <div class="link-card" @click="$router.push('/dashboard')">📊 {{ $t('zh_a2b3af') }}</div>
      <div class="link-card" @click="$router.push('/conflicts')">⚠️ {{ $t('zh_b7a9ae') }}</div>
      <div class="link-card" @click="$router.push('/workflows')">⚙️ {{ $t('zh_30cf4a') }}</div>
    </div>
    <p class="hint">{{ $t('zh_512cb0') }}</p>
  </div>
</template>

<style scoped>
.done-step { text-align: center; }
.done-icon { font-size: 64px; margin-bottom: 16px; }
.done-desc { color: var(--text-secondary); font-size: 16px; margin-bottom: 24px; }
.quick-links { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
/* P47 r2: DoneStep 硬编码 #f8f9fa / #999 / #007aff / #f0f7ff → 全站 token.
   link-card 静态 bg = --bg-recessed (与 SearchBar 输入同源), hover = --accent border + --accent-subtle bg
   (与 MemoryCard hover lift / SearchBar focus 同手感). hint = --text-tertiary (与全站"最弱文字"语义统一). */
.link-card { padding: 16px; background: var(--bg-recessed); border-radius: 12px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.2s; border: 2px solid transparent; }
.link-card:hover { border-color: var(--accent); background: var(--accent-subtle); }
.hint { color: var(--text-tertiary); font-size: 13px; }
</style>
