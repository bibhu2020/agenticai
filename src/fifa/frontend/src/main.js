import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import ScoresView from './views/ScoresView.vue'
import ScheduleView from './views/ScheduleView.vue'
import NewsView from './views/NewsView.vue'
import StandingsView from './views/StandingsView.vue'
import HighlightsView from './views/HighlightsView.vue'
import './style.css'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/scores' },
    { path: '/scores',     component: ScoresView,     meta: { title: 'Today\'s Scores' } },
    { path: '/schedule',   component: ScheduleView,   meta: { title: 'Upcoming Schedule' } },
    { path: '/standings',  component: StandingsView,  meta: { title: 'Standings' } },
    { path: '/highlights', component: HighlightsView, meta: { title: 'Highlights' } },
    { path: '/news',       component: NewsView,       meta: { title: 'News' } },
  ]
})

router.afterEach((to) => {
  document.title = `${to.meta.title || 'FIFA'} | World Cup 2026`
})

// Register PWA service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {})
  })
}

createApp(App).use(router).mount('#app')
