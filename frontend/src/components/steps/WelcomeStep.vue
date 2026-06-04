<template>
  <div class="welcome-step">
    <div class="welcome-icon">🧠</div>
    <h2>{{ $t('zh_b98aaf') }} Memory Viewer v2</h2>
    <p class="welcome-desc">{{ $t('zh_620a0c') }} — {{ $t('zh_def3a9') }}、{{ $t('zh_44e04b') }} Agent {{ $t('zh_ca9e41') }}</p>
    <div class="feature-grid">
      <div class="feature-item"><span>🔍</span> {{ $t('zh_b6c0b4') }} & {{ $t('zh_62e500') }}</div>
      <div class="feature-item"><span>🕸️</span> {{ $t('zh_ca9969') }} & {{ $t('zh_c4db6b') }}</div>
      <div class="feature-item"><span>⚠️</span> {{ $t('zh_ab4068') }} & {{ $t('zh_b2125c') }}</div>
      <div class="feature-item"><span>⚙️</span> {{ $t('zh_1a1246') }}</div>
    </div>
    <p class="welcome-hint">{{ $t('zh_22a624') }}</p>
  </div>
</template>

<style scoped>
.welcome-step { text-align: center; }
.welcome-icon { font-size: 64px; margin-bottom: 16px; }
.welcome-desc { color: #666; font-size: 16px; margin-bottom: 24px; }
.feature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px; }
.feature-item { padding: 12px; background: var(--card-bg, #f8f9fa); border-radius: 10px; font-size: 14px; text-align: left; }
.feature-item span { margin-right: 8px; }
.welcome-hint { color: #999; font-size: 13px; }
</style>
