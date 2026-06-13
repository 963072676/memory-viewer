<template>
  <div class="welcome-step">
    <div class="welcome-icon">🧠</div>
    <h2>{{ $t('i18n.welcome') }} Memory Viewer v2</h2>
    <p class="welcome-desc">{{ $t('i18n.intelligent_memory') }} — {{ $t('i18n.help_understand') }}、{{ $t('i18n.organize_optimize') }} Agent {{ $t('i18n.onboarding.memory_system') }}</p>
    <div class="feature-grid">
      <div class="feature-item"><span>🔍</span> {{ $t('i18n.smart') }} & {{ $t('i18n.natural_language') }}</div>
      <div class="feature-item"><span>🕸️</span> {{ $t('i18n.memory_graph') }} & {{ $t('i18n.clustering') }}</div>
      <div class="feature-item"><span>⚠️</span> {{ $t('i18n.conflict_detection') }} & {{ $t('i18n.anomaly_alert') }}</div>
      <div class="feature-item"><span>⚙️</span> {{ $t('i18n.automated_workflow') }}</div>
    </div>
    <p class="welcome-hint">{{ $t('i18n.next_few') }}</p>
  </div>
</template>

<style scoped>
.welcome-step { text-align: center; }
.welcome-icon { font-size: 64px; margin-bottom: 16px; }
.welcome-desc { color: #666; font-size: 16px; margin-bottom: 24px; }
.feature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px; }
.feature-item { padding: 12px; background: var(--bg-recessed); border-radius: 10px; font-size: 14px; text-align: left; }
.feature-item span { margin-right: 8px; }
.welcome-hint { color: #999; font-size: 13px; }
</style>
