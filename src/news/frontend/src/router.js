import { createRouter, createWebHistory } from 'vue-router'
import CategoryView from './views/CategoryView.vue'
import AdminView from './views/AdminView.vue'
import { ALL_TABS } from './categories.js'

const categoryRoutes = ALL_TABS.map(tab => ({
  path: `/${tab.key}`,
  component: CategoryView,
  props: { categoryKey: tab.key },
  meta: { title: tab.label },
}))

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/world' },
    ...categoryRoutes,
    { path: '/admin', component: AdminView, meta: { title: 'Admin' } },
  ],
})

router.afterEach((to) => {
  document.title = `${to.meta.title || 'News'} | Daily News Digest`
})
