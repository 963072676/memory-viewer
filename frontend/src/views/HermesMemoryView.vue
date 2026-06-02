<template>
  <div class="hermes-view">
    <h2>Hermes Memory</h2>
    <div v-if="store.loading" class="card-grid">
      <div v-for="i in 4" :key="i" class="skeleton-card"></div>
    </div>
    <div v-else-if="store.totalEntries === 0" class="empty-state">
      <p>暂无 Hermes Memory 数据</p>
    </div>
    <template v-else>
      <!-- Global -->
      <div class="profile-section">
        <h3 class="profile-heading">🌐 Global</h3>
        <div class="card-grid">
          <div v-for="(entry, i) in store.globalData.memory" :key="'gm-' + i" class="hermes-card">
            <div class="hermes-label">MEMORY.md</div>
            <p>{{ entry }}</p>
          </div>
          <div v-for="(entry, i) in store.globalData.user" :key="'gu-' + i" class="hermes-card">
            <div class="hermes-label">USER.md</div>
            <p>{{ entry }}</p>
          </div>
        </div>
      </div>
      <!-- Profiles -->
      <div v-for="(data, name) in store.profiles" :key="name" class="profile-section">
        <h3 class="profile-heading">👤 {{ name }}</h3>
        <div class="card-grid">
          <div v-for="(entry, i) in data.memory" :key="'pm-' + i" class="hermes-card">
            <div class="hermes-label">MEMORY.md</div>
            <p>{{ entry }}</p>
          </div>
          <div v-for="(entry, i) in data.user" :key="'pu-' + i" class="hermes-card">
            <div class="hermes-label">USER.md</div>
            <p>{{ entry }}</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useHermesMemoryStore } from '@/stores/hermes-memory'
const store = useHermesMemoryStore()
</script>

<style scoped>
.hermes-view {
  padding-bottom: 40px;
}

h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 24px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.profile-section {
  margin-bottom: 32px;
}

.profile-heading {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 16px;
}

.hermes-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
}

.hermes-label {
  font-size: 0.7rem;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.hermes-card p {
  font-size: 0.875rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.skeleton-card {
  height: 80px;
  background: linear-gradient(90deg, var(--tag-bg) 25%, var(--border) 50%, var(--tag-bg) 75%);
  background-size: 200% 100%;
  border-radius: var(--radius);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

/* Responsive */
@media (max-width: 767px) {
  h2 {
    font-size: 1.2rem;
  }

  .card-grid {
    grid-template-columns: 1fr;
  }

  .hermes-card p {
    font-size: 0.825rem;
  }

  .skeleton-card {
    height: 60px;
  }
}
</style>
