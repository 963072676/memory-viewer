<template>
  <div class="rag-citation">
    <span class="citation-index">[{{ index }}]</span>
    <div class="citation-content">
      <div class="citation-title">{{ source.title }}</div>
      <div class="citation-snippet">{{ source.snippet }}</div>
      <div class="citation-meta">
        <span class="citation-type">{{ source.type }}</span>
        <span v-for="tag in (source.tags || []).slice(0, 3)" :key="tag" class="citation-tag">{{ tag }}</span>
        <span class="citation-similarity">{{ source.similarity }}% match</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ source: any; index: number }>()
</script>

<style scoped>
.rag-citation {
  display: flex; gap: 10px; padding: 8px 10px; margin-bottom: 6px;
  background: var(--tag-bg, #f5f5f7); border-radius: 8px; align-items: flex-start;
}
.citation-index {
  font-size: 0.75rem; font-weight: 700; color: var(--accent, #007aff);
  background: rgba(0,113,227,0.1); width: 24px; height: 24px;
  display: flex; align-items: center; justify-content: center; border-radius: 4px;
  flex-shrink: 0;
}
.citation-content { flex: 1; min-width: 0; }
.citation-title { font-size: 0.85rem; font-weight: 600; color: var(--text, #1d1d1f); }
.citation-snippet {
  font-size: 0.8rem; color: var(--text-secondary, #86868b);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.citation-meta { display: flex; gap: 6px; align-items: center; margin-top: 4px; flex-wrap: wrap; }
.citation-type {
  font-size: 0.65rem; background: var(--border, #e5e5ea); padding: 1px 5px;
  border-radius: 3px;
}
.citation-tag {
  font-size: 0.65rem; background: rgba(0,113,227,0.1); color: var(--accent, #007aff);
  padding: 1px 5px; border-radius: 3px;
}
.citation-similarity {
  font-size: 0.65rem; color: var(--text-secondary, #86868b); margin-left: auto;
}
</style>
