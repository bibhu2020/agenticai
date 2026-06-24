<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getSummary, refreshCache } from './services/api.js'

const route = useRoute()
const summary = ref(null)
const refreshing = ref(false)
const installPrompt = ref(null)
const showInstall = ref(false)

const tabs = [
  { path: '/scores',     label: "Today's Scores", icon: '⚽' },
  { path: '/schedule',   label: 'Schedule',        icon: '📅' },
  { path: '/standings',  label: 'Standings',       icon: '🏅' },
  { path: '/highlights', label: 'Highlights',      icon: '🎬' },
  { path: '/news',       label: 'News',            icon: '📰' },
]

async function loadSummary() {
  try { summary.value = await getSummary() } catch {}
}

async function doRefresh() {
  refreshing.value = true
  try {
    await refreshCache()
    await loadSummary()
  } catch {}
  refreshing.value = false
}

function formatLastUpdated(iso) {
  if (!iso) return 'Never'
  const d = new Date(iso)
  return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadSummary()
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault()
    installPrompt.value = e
    showInstall.value = true
  })
})

async function installPWA() {
  if (!installPrompt.value) return
  installPrompt.value.prompt()
  const { outcome } = await installPrompt.value.userChoice
  if (outcome === 'accepted') showInstall.value = false
}
</script>

<template>
  <div class="layout">
    <!-- Header -->
    <header class="header">
      <div class="header-inner">
        <div class="brand">
          <span class="brand-icon">🏆</span>
          <div class="brand-text">
            <span class="brand-title">FIFA World Cup 2026</span>
            <span class="brand-sub">Live Dashboard</span>
          </div>
        </div>

        <div class="header-stats" v-if="summary">
          <div class="stat-pill live" v-if="summary.live > 0">
            <span class="dot"></span>{{ summary.live }} Live
          </div>
          <div class="stat-pill">⚽ {{ summary.matches_today }} Today</div>
          <div class="stat-pill">📅 {{ summary.upcoming_7days }} Upcoming</div>
        </div>

        <div class="header-actions">
          <span class="last-updated" v-if="summary?.last_updated">
            Updated {{ formatLastUpdated(summary.last_updated) }}
          </span>
          <button class="btn btn-outline" @click="doRefresh" :disabled="refreshing">
            <span :class="{ spin: refreshing }">↻</span>
            Refresh
          </button>
          <button v-if="showInstall" class="btn btn-gold" @click="installPWA">
            📲 Install App
          </button>
        </div>
      </div>
    </header>

    <!-- Tab Navigation -->
    <nav class="tabs">
      <router-link
        v-for="tab in tabs"
        :key="tab.path"
        :to="tab.path"
        class="tab"
        :class="{ active: route.path === tab.path }"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span class="tab-label">{{ tab.label }}</span>
      </router-link>
    </nav>

    <!-- Main Content -->
    <main class="content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style scoped>
.layout { display: flex; flex-direction: column; min-height: 100vh; }

.header {
  background: linear-gradient(135deg, #0A1628 0%, #112240 100%);
  border-bottom: 1px solid rgba(255,215,0,0.2);
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 20px rgba(0,0,0,0.5);
}
.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  height: 70px;
  display: flex;
  align-items: center;
  gap: 24px;
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-icon { font-size: 28px; }
.brand-title { display: block; font-size: 18px; font-weight: 700; color: #FFD700; line-height: 1; }
.brand-sub { display: block; font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }

.header-stats { display: flex; gap: 8px; flex: 1; }
.stat-pill {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px 12px;
  border-radius: 20px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  font-size: 13px;
  color: var(--text-secondary);
}
.stat-pill.live { border-color: rgba(255,68,68,0.4); color: #FF6B6B; background: rgba(255,68,68,0.1); }
.dot { width: 7px; height: 7px; border-radius: 50%; background: #FF4444; animation: pulse 1.2s infinite; }

.header-actions { display: flex; align-items: center; gap: 10px; }
.last-updated { font-size: 12px; color: var(--text-muted); white-space: nowrap; }

.spin { display: inline-block; animation: spin 0.8s linear infinite; }

.tabs {
  display: flex;
  background: #0D1F3C;
  border-bottom: 1px solid var(--border);
  padding: 0 24px;
  position: sticky;
  top: 70px;
  z-index: 99;
}
.tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 20px;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}
.tab:hover { color: var(--text-secondary); }
.tab.active { color: var(--accent-gold); border-bottom-color: var(--accent-gold); }
.tab-icon { font-size: 16px; }

.content { flex: 1; max-width: 1400px; width: 100%; margin: 0 auto; padding: 24px; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 768px) {
  .header-stats { display: none; }
  .last-updated { display: none; }
  .header-inner { gap: 12px; }
  .content { padding: 16px; }
  .tabs { padding: 0 8px; }
  .tab { padding: 12px 12px; font-size: 13px; }
}
</style>
