<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { HEADER_TABS, FOOTER_TABS } from './categories.js'
import { getAllNews } from './services/api.js'

const route = useRoute()
const generatedAt = ref(null)
const installPrompt = ref(null)
const showInstall = ref(false)

function formatUpdated(iso) {
  if (!iso) return null
  const d = new Date(iso)
  return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  try {
    const data = await getAllNews()
    generatedAt.value = data.generated_at
  } catch { /* first load before any agent run yet */ }

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
        <div class="header-top">
          <div class="brand">
            <span class="brand-icon">📰</span>
            <div class="brand-text">
              <span class="brand-title">Daily News Digest</span>
              <span class="brand-sub" v-if="generatedAt">Updated {{ formatUpdated(generatedAt) }}</span>
              <span class="brand-sub" v-else>Top stories, summarized daily</span>
            </div>
          </div>

          <div class="header-actions">
            <button v-if="showInstall" class="btn btn-primary" @click="installPWA">📲 Install</button>
            <router-link to="/admin" class="admin-link" title="Admin">⚙️</router-link>
          </div>
        </div>

        <nav class="header-tabs">
          <router-link
            v-for="tab in HEADER_TABS"
            :key="tab.key"
            :to="`/${tab.key}`"
            class="header-tab"
            :class="{ active: route.path === `/${tab.key}` }"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            <span class="tab-label">{{ tab.label }}</span>
          </router-link>
        </nav>
      </div>
    </header>

    <!-- Main Content -->
    <main class="content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Footer / bottom tab bar -->
    <nav class="footer-tabs">
      <router-link
        v-for="tab in FOOTER_TABS"
        :key="tab.key"
        :to="`/${tab.key}`"
        class="footer-tab"
        :class="{ active: route.path === `/${tab.key}` }"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span class="tab-label">{{ tab.label }}</span>
      </router-link>
    </nav>
  </div>
</template>

<style scoped>
.layout { display: flex; flex-direction: column; min-height: 100vh; }

/* ── Header (top, always visible) ── */
.header {
  background: linear-gradient(135deg, #0B1220 0%, #131B2E 100%);
  border-bottom: 1px solid var(--border);
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow);
}
.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 10px 0 6px;
}

.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
  padding-bottom: 8px;
}

.brand { display: flex; align-items: center; gap: 10px; }
.brand-icon { font-size: 26px; }
.brand-title { display: block; font-size: 17px; font-weight: 700; color: var(--accent-primary); line-height: 1.3; }
.brand-sub { display: block; font-size: 11px; color: var(--text-muted); }

.header-tabs {
  display: flex;
  gap: 4px;
  overflow-x: auto;
  scrollbar-width: none;
}
.header-tabs::-webkit-scrollbar { display: none; }

.header-tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  padding: 8px 4px 10px;
  min-width: 64px;
  border-radius: 8px;
  border-bottom: 2px solid transparent;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.2px;
  white-space: nowrap;
  transition: all 0.2s;
}
.header-tab:hover { color: var(--text-secondary); background: rgba(255,255,255,0.04); }
.header-tab.active { color: var(--accent-primary); border-bottom-color: var(--accent-primary); background: rgba(245,158,11,0.1); }
.header-tab .tab-icon { font-size: 19px; line-height: 1; }
.header-tab .tab-label { line-height: 1; }

.header-actions { display: flex; align-items: center; gap: 10px; }
.admin-link {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: 8px;
  color: var(--text-muted); text-decoration: none; font-size: 15px;
  transition: all 0.2s;
}
.admin-link:hover { color: var(--accent-primary); background: rgba(255,255,255,0.04); }

.content { flex: 1; max-width: 1400px; width: 100%; margin: 0 auto; padding: 24px 24px 96px; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ── Footer / bottom tab bar (fixed, thumb-reachable on mobile) ── */
.footer-tabs {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  background: rgba(19, 27, 46, 0.97);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-top: 1px solid var(--border);
  box-shadow: 0 -4px 20px rgba(0,0,0,0.4);
  padding: 0 8px;
  padding-bottom: env(safe-area-inset-bottom, 0px);
  z-index: 200;
}

.footer-tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  padding: 8px 4px 10px;
  min-width: 0;
  border-top: 2px solid transparent;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.2px;
  transition: all 0.2s;
}
.footer-tab:hover { color: var(--text-secondary); }
.footer-tab.active { color: var(--accent-primary); border-top-color: var(--accent-primary); background: rgba(245,158,11,0.06); }
.footer-tab .tab-icon { font-size: 19px; line-height: 1; }
.footer-tab .tab-label { line-height: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }

@media (max-width: 640px) {
  .brand-sub { display: none; }
  .content { padding: 12px 12px 96px; }
}
</style>
