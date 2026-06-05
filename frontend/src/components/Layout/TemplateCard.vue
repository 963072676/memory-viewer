<template>
  <div class="template-card">
    <div class="card-header">
      <span class="card-icon">{{ template.icon }}</span>
      <div class="card-info">
        <h3>{{ template.name }}</h3>
        <p>{{ template.description }}</p>
      </div>
      <span v-if="template.builtin" class="builtin-badge">{{ $t('en_builtin') }}</span>
    </div>
    <div class="card-fields">
      <span v-for="field in (template.fields || []).slice(0, 4)" :key="field.name" class="field-chip">
        {{ field.label }} <span class="field-type">{{ field.type }}</span>
      </span>
    </div>
    <div class="card-tags">
      <span v-for="tag in (template.default_tags || []).slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
    </div>
    <div class="card-actions">
      <button class="btn-use" @click="$emit('use', template)">{{ $t('en_use_template') }}</button>
      <button v-if="!template.builtin" class="btn-edit" @click="$emit('edit', template)">{{ $t('en_edit') }}</button>
      <button v-if="!template.builtin" class="btn-delete" @click="$emit('delete', template)">{{ $t('en_delete') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ template: any }>()
defineEmits<{ use: [t: any]; edit: [t: any]; delete: [t: any] }>()
</script>

<style scoped>
.template-card {
  /* P38 r12: fallback 硬编码 #fff / #e5e5ea / #1d1d1f / #86868b / #007aff / #ff3b30 / #f5f5f7 全部删除
     8 个 var() 全部回到无 fallback 形态（与 variables.css 契约一致）
     同时 hover 视觉统一：与 MemoryCard / CollectionCard / DashboardWidget 同源
     (var(--shadow-hover) + translateY(-2px) + 0.25s 过渡) */
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  transition: box-shadow 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              transform 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              border-color 0.2s ease;
}
.template-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
  border-color: var(--border-strong);
}
.card-header { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 12px; }
.card-icon { font-size: 2rem; }
.card-info { flex: 1; }
.card-info h3 { margin: 0; font-size: 1rem; font-weight: 600; color: var(--primary); }
.card-info p { margin: 4px 0 0; font-size: 0.8rem; color: var(--text-secondary); }

.builtin-badge {
  /* P38 r12: rgba(0,113,227,0.1) Apple 系统色硬编码 → var(--accent-soft) token
     (与 P38 r7 sweep 的 .card-icon 修正同源: 5% accent 软底) */
  font-size: 0.65rem;
  background: var(--accent-soft);
  color: var(--accent);
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.card-fields { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.field-chip {
  font-size: 0.75rem; background: var(--tag-bg); padding: 2px 8px;
  border-radius: 4px; display: flex; align-items: center; gap: 4px;
}
.field-type { font-size: 0.65rem; color: var(--text-secondary); }
.card-tags { display: flex; gap: 4px; margin-bottom: 12px; }
.tag {
  /* P38 r12: 同 builtin-badge, rgba(0,113,227,0.1) → var(--accent-soft) */
  font-size: 0.7rem;
  background: var(--accent-soft);
  color: var(--accent);
  padding: 1px 6px;
  border-radius: 3px;
}
.card-actions { display: flex; gap: 8px; }
.btn-use {
  flex: 1; padding: 6px 12px; border: none; border-radius: 6px;
  background: var(--accent); color: var(--card); font-size: 0.8rem;
  cursor: pointer; font-family: var(--font);
  transition: background 0.15s ease;
}
.btn-use:hover { background: var(--primary); }
.btn-edit, .btn-delete {
  padding: 6px 12px; border: 1px solid var(--border);
  border-radius: 6px; background: var(--card); font-size: 0.8rem;
  cursor: pointer; font-family: var(--font); color: var(--primary);
  transition: background 0.15s ease, border-color 0.15s ease;
}
.btn-edit:hover, .btn-delete:hover { background: var(--tag-bg); }
.btn-delete { color: var(--error); border-color: var(--error); }
.btn-delete:hover { background: var(--error-bg); }
</style>
