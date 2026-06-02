<template>
  <div class="template-card">
    <div class="card-header">
      <span class="card-icon">{{ template.icon }}</span>
      <div class="card-info">
        <h3>{{ template.name }}</h3>
        <p>{{ template.description }}</p>
      </div>
      <span v-if="template.builtin" class="builtin-badge">Built-in</span>
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
      <button class="btn-use" @click="$emit('use', template)">Use Template</button>
      <button v-if="!template.builtin" class="btn-edit" @click="$emit('edit', template)">Edit</button>
      <button v-if="!template.builtin" class="btn-delete" @click="$emit('delete', template)">Delete</button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ template: any }>()
defineEmits<{ use: [t: any]; edit: [t: any]; delete: [t: any] }>()
</script>

<style scoped>
.template-card {
  background: var(--card, #fff); border: 1px solid var(--border, #e5e5ea);
  border-radius: 12px; padding: 16px; transition: box-shadow 0.2s;
}
.template-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.card-header { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 12px; }
.card-icon { font-size: 2rem; }
.card-info { flex: 1; }
.card-info h3 { margin: 0; font-size: 1rem; font-weight: 600; color: var(--text, #1d1d1f); }
.card-info p { margin: 4px 0 0; font-size: 0.8rem; color: var(--text-secondary, #86868b); }
.builtin-badge {
  font-size: 0.65rem; background: rgba(0,113,227,0.1); color: var(--accent, #007aff);
  padding: 2px 6px; border-radius: 4px; font-weight: 600;
}
.card-fields { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.field-chip {
  font-size: 0.75rem; background: var(--tag-bg, #f5f5f7); padding: 2px 8px;
  border-radius: 4px; display: flex; align-items: center; gap: 4px;
}
.field-type { font-size: 0.65rem; color: var(--text-secondary, #86868b); }
.card-tags { display: flex; gap: 4px; margin-bottom: 12px; }
.tag {
  font-size: 0.7rem; background: rgba(0,113,227,0.1); color: var(--accent, #007aff);
  padding: 1px 6px; border-radius: 3px;
}
.card-actions { display: flex; gap: 8px; }
.btn-use {
  flex: 1; padding: 6px 12px; border: none; border-radius: 6px;
  background: var(--accent, #007aff); color: #fff; font-size: 0.8rem;
  cursor: pointer; font-family: var(--font);
}
.btn-edit, .btn-delete {
  padding: 6px 12px; border: 1px solid var(--border, #e5e5ea);
  border-radius: 6px; background: var(--card, #fff); font-size: 0.8rem;
  cursor: pointer; font-family: var(--font); color: var(--text, #1d1d1f);
}
.btn-delete { color: var(--error, #ff3b30); border-color: var(--error, #ff3b30); }
</style>
