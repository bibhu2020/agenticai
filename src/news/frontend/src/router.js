import { createRouter, createWebHistory } from 'vue-router'
import CategoryView from './views/CategoryView.vue'
import LocalView from './views/LocalView.vue'
import AdminView from './views/AdminView.vue'
import { TABS } from './categories.js'

const categoryRoutes = TABS.map(tab => ({
  path: `/${tab.key}`,
  component: tab.key === 'local' ? LocalView : CategoryView,
  props: { groupKey: tab.key },
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
