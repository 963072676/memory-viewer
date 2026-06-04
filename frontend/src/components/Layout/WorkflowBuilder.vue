<template>
  <div class="workflow-builder">
    <div class="builder-section">
      <h4>基本信息</h4>
      <div class="field-group">
        <label>规则名称</label>
        <input v-model="form.name" type="text" placeholder="例如: 清理过期记忆" class="input-field" />
      </div>
      <div class="field-group">
        <label>描述</label>
        <input v-model="form.description" type="text" placeholder="规则描述" class="input-field" />
      </div>
    </div>

    <div class="builder-section">
      <h4>触发器</h4>
      <select v-model="form.trigger.type" class="input-field">
        <option value="manual">手动触发</option>
        <option value="schedule">定时触发</option>
        <option value="on_memory_create">记忆创建时</option>
        <option value="on_memory_update">记忆更新时</option>
        <option value="on_strength_change">强度变化时</option>
      </select>
      <div v-if="form.trigger.type === 'schedule'" class="field-group">
        <label>Cron 表达式</label>
        <input v-model="form.trigger.config.cron" type="text" placeholder="0 2 * * *" class="input-field" />
        <span class="field-hint">例: "0 2 * * *" = 每天凌晨2点</span>
      </div>
    </div>

    <div class="builder-section">
      <h4>
        条件 (全部满足)
        <button class="btn-add" @click="addCondition">+ 添加</button>
      </h4>
      <div v-for="(cond, i) in form.conditions" :key="i" class="condition-row">
        <select v-model="cond.field" class="input-field short">
          <option value="age_days">天数</option>
          <option value="strength">强度</option>
          <option value="type">类型</option>
          <option value="content">内容</option>
          <option value="has_concept">包含概念</option>
        </select>
        <select v-model="cond.op" class="input-field short">
          <option value=">">></option>
          <option value="<"><</option>
          <option value=">=">>=</option>
          <option value="<="><=</option>
          <option value="==">==</option>
          <option value="!=">!=</option>
          <option value="contains">包含</option>
        </select>
        <input v-model="cond.value" type="text" class="input-field short" placeholder="值" />
        <button class="btn-remove" @click="form.conditions.splice(i, 1)">✕</button>
      </div>
    </div>

    <div class="builder-section">
      <h4>
        动作
        <button class="btn-add" @click="addAction">+ 添加</button>
      </h4>
      <div v-for="(action, i) in form.actions" :key="i" class="action-row">
        <select v-model="action.type" class="input-field short">
          <option value="archive">归档</option>
          <option value="delete">删除</option>
          <option value="add_tag">添加标签</option>
          <option value="adjust_strength">调整强度</option>
          <option value="send_notification">发送通知</option>
        </select>
        <input
          v-if="action.type === 'add_tag'"
          v-model="action.config.tag"
          type="text"
          class="input-field"
          placeholder="标签名"
        />
        <input
          v-if="action.type === 'adjust_strength'"
          v-model.number="action.config.delta"
          type="number"
          step="0.1"
          class="input-field short"
          placeholder="delta"
        />
        <button class="btn-remove" @click="form.actions.splice(i, 1)">✕</button>
      </div>
    </div>

    <div class="builder-actions">
      <button class="action-btn action-btn--accent" @click="$emit('save', form)" :disabled="!isValid">保存规则</button>
      <button class="action-btn" @click="$emit('cancel')">取消</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed } from 'vue'

const emit = defineEmits<{
  save: [form: any]
  cancel: []
}>()

const form = reactive({
  name: '',
  description: '',
  trigger: { type: 'manual', config: {} as any },
  conditions: [] as any[],
  actions: [] as any[],
})

const isValid = computed(() => form.name.trim() !== '' && form.actions.length > 0)

function addCondition() {
  form.conditions.push({ field: 'age_days', op: '>', value: '' })
}

function addAction() {
  form.actions.push({ type: 'archive', config: {} })
}

defineExpose({ form })
</script>

<style scoped>
.workflow-builder {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.builder-section {
  background: var(--bg, #f2f2f7);
  border-radius: 10px;
  padding: 14px;
}

.builder-section h4 {
  margin: 0 0 10px;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text, #1d1d1f);
  display: flex;
  align-items: center;
  gap: 8px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 8px;
}

.field-group label,
.builder-section label {
  font-size: 0.75rem;
  color: var(--text-secondary, #86868b);
  font-weight: 500;
}

.input-field {
  padding: 6px 10px;
  border: 1px solid var(--border, #e5e5ea);
  border-radius: 6px;
  background: var(--card, #fff);
  font-size: 0.85rem;
  font-family: var(--font);
  color: var(--text, #1d1d1f);
  width: 100%;
  box-sizing: border-box;
}

.input-field.short {
  width: auto;
  min-width: 80px;
}

.field-hint {
  font-size: 0.7rem;
  color: var(--text-secondary, #86868b);
}

.condition-row,
.action-row {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.btn-add {
  padding: 2px 8px;
  border: 1px dashed var(--primary, #007aff);
  border-radius: 4px;
  background: transparent;
  color: var(--primary, #007aff);
  font-size: 0.75rem;
  cursor: pointer;
  font-family: var(--font);
}

.btn-remove {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--error, #ff3b30);
  cursor: pointer;
  font-size: 0.85rem;
}

.builder-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* P38 r23: btn-save / btn-cancel → .action-btn (r21 global system). */
</style>
