<template>
  <div class="profiles-view">
    <h2>Profiles</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="profiles.length === 0">
      <EmptyState icon="👤" message="暂无 Profile" />
    </div>
    <div v-else class="profile-list">
      <div v-for="name in profiles" :key="name" class="profile-card">
        <div class="profile-icon">👤</div>
        <div class="profile-info">
          <h3>{{ name }}</h3>
          <p class="profile-desc">Profile: {{ name }}</p>
        </div>
        <router-link :to="{ path: '/hermes', query: { profile: name } }" class="profile-link">查看 →</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchProfiles } from '@/api/profiles'
import EmptyState from '@/components/Layout/EmptyState.vue'

const profiles = ref<string[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    profiles.value = await fetchProfiles()
  } catch (e) {
    console.error('Failed to fetch profiles:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.profiles-view {
  padding-bottom: 40px;
}

h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 24px;
}

.profile-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: box-shadow 0.2s;
}

.profile-card:hover {
  box-shadow: var(--shadow);
}

.profile-icon {
  font-size: 2rem;
}

.profile-info {
  flex: 1;
}

.profile-info h3 {
  font-size: 1rem;
  font-weight: 600;
}

.profile-desc {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 2px;
}

.profile-link {
  color: var(--accent);
  font-size: 0.875rem;
  font-weight: 500;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

/* Responsive */
@media (max-width: 767px) {
  h2 {
    font-size: 1.2rem;
  }

  .profile-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .profile-link {
    align-self: flex-end;
  }
}
</style>
