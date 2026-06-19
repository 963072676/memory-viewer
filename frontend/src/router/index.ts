import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // Core routes
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/agentmemory',
      name: 'agentmemory',
      component: () => import('@/views/AgentMemoryView.vue'),
    },
    {
      path: '/hermes',
      name: 'hermes',
      component: () => import('@/views/HermesMemoryView.vue'),
    },
    {
      path: '/profiles',
      name: 'profiles',
      component: () => import('@/views/ProfilesView.vue'),
    },
    // Feature routes
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
    },
    {
      path: '/collections',
      name: 'collections',
      component: () => import('@/views/CollectionsView.vue'),
    },
    {
      path: '/compare',
      name: 'compare',
      component: () => import('@/views/CompareView.vue'),
    },
    {
      path: '/graph',
      name: 'graph',
      component: () => import('@/views/GraphView.vue'),
    },
    {
      path: '/sources',
      name: 'sources',
      component: () => import('@/views/SourcesView.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/SettingsView.vue'),
    },
    // Dynamic routes (MUST be last)
    {
      path: '/memory/:id',
      name: 'memory-detail',
      component: () => import('@/views/MemoryDetailView.vue'),
    },
  ],
})

export default router
