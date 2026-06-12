<template>
  <div class="done-step">
    <div class="done-icon">🎉</div>
    <h2>{{ $t('i18n.all_set') }}！</h2>
    <p class="done-desc">{{ $t('i18n.got_a9807e') }} Memory Viewer {{ $t('i18n.core_functionality') }}</p>
    <div class="quick-links">
      <div class="link-card" @click="$router.push('/agentmemory')">📝 {{ $t('i18n.browse_memories') }}</div>
      <div class="link-card" @click="$router.push('/dashboard')">📊 {{ $t('i18n.view_dashboard') }}</div>
      <div class="link-card" @click="$router.push('/conflicts')">⚠️ {{ $t('i18n.detect_conflicts') }}</div>
      <div class="link-card" @click="$router.push('/workflows')">⚙️ {{ $t('i18n.set_automation') }}</div>
    </div>
    <p class="hint">{{ $t('i18n.restart_tour') }}</p>
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
