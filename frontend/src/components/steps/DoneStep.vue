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
.done-desc { color: #666; font-size: 16px; margin-bottom: 24px; }
.quick-links { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
.link-card { padding: 16px; background: var(--card-bg, #f8f9fa); border-radius: 12px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.2s; border: 2px solid transparent; }
.link-card:hover { border-color: #007aff; background: #f0f7ff; }
.hint { color: #999; font-size: 13px; }
</style>
