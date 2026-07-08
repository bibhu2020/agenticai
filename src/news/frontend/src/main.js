import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import CategoryView from './views/CategoryView.vue'
import AdminView from './views/AdminView.vue'
import { ALL_TABS } from './categories.js'
import './style.css'

const categoryRoutes = ALL_TABS.map(tab => ({
  path: `/${tab.key}`,
  component: CategoryView,
  props: { categoryKey: tab.key },
  meta: { title: tab.label },
}))

const router = createRouter({
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

// Register PWA service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {})
  })
}

createApp(App).use(router).mount('#app')
