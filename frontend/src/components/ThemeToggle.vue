<template>
  <!-- P38 r14: a11y — aria-label 替代 title（title 不被屏幕阅读器可靠读取） -->
  <button class="theme-toggle" @click="toggleTheme" :title="modeLabel()" :aria-label="modeLabel()">
    <span aria-hidden="true">{{ modeIcon() }}</span>
  </button>
</template>

<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'

const { toggleTheme, modeLabel, modeIcon } = useTheme()
</script>

<style scoped>
.theme-toggle {
  background: var(--tag-bg);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.theme-toggle:hover {
  transform: scale(1.1);
}
</style>