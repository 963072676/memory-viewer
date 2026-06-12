<template>
  <div class="profiles-view">
    <h2 class="section-title">{{ $t('en_profiles') }}</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="profiles.length === 0">
      <!-- P38 r30: EmptyState message prop 改 v-bind -->
      <EmptyState icon="👤" :message="`${$t('i18n.no')} Profile`" />
    </div>
    <div v-else class="profile-list">
      <div v-for="name in profiles" :key="name" class="profile-card">
        <div class="profile-icon">👤</div>
        <div class="profile-info">
          <h3>{{ name }}</h3>
          <p class="profile-desc">Profile: {{ name }}</p>
        </div>
        <router-link :to="{ path: '/hermes', query: { profile: name } }" class="profile-link">{{ $t('i18n.view') }} →</router-link>
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

/* P38 r20: section-title 左侧 3px accent bar — 与全站其他 view 同源 (r15 模式). */
h2.section-title { position: relative; padding-left: 12px; }
h2.section-title::before { content: ''; position: absolute; left: 0; top: 50%; transform: translateY(-50%); width: 3px; height: 60%; background: var(--accent); border-radius: 0 2px 2px 0; }

.profile-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* P46 r1: .profile-card 视觉对齐 P38 r35 的 5 套 Card 家族 (MemoryCard / CollectionCard /
   DashboardWidget / TemplateCard / hermes-card / search-result-card) — 之前仅有静态 box-shadow
   无 transition / 无 hover lift / 无 border-color 过渡, 视觉上比 hermes-card 弱 1 档 (她有
   translateY -2px + shadow-hover + border-strong, ProfilesView 完全没有).
   补齐: cubic-bezier(0.25, 0.1, 0.25, 1) 0.25s 节奏 (与 5 套 Card 同手感),
   hover translateY -2px + shadow-hover + border-strong 联动, 跨 view 切换无视觉跳变. */
.profile-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  transition: box-shadow 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              transform 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
              border-color 0.2s ease;
}

.profile-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
  border-color: var(--border-strong);
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
