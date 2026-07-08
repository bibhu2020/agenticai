<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { HEADER_TABS, FOOTER_TABS, tabMeta } from './categories.js'
import { getAllNews } from './services/api.js'
import { usePlayer } from './player.js'

const route = useRoute()
const generatedAt = ref(null)
const newsData = ref(null)
const installPrompt = ref(null)
const showInstall = ref(false)

const { state: playerState, currentTrack, playQueue, playAllTabs, togglePlay, next, prev, seek, stop } = usePlayer()

const progressPct = computed(() => playerState.duration ? (playerState.progress / playerState.duration) * 100 : 0)

function onSeek(e) {
  if (!playerState.duration) return
  const rect = e.currentTarget.getBoundingClientRect()
  const ratio = Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width))
  seek(ratio * playerState.duration)
}

function formatUpdated(iso) {
  if (!iso) return null
  const d = new Date(iso)
  return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function categoryArticles(key) {
  return newsData.value?.categories?.[key] || []
}

function tabHasAudio(key) {
  return categoryArticles(key).some(a => a.audio)
}

function isTabPlaying(key) {
  return currentTrack.value?.category === key && playerState.isPlaying
}

function quickPlayTab(key) {
  if (isTabPlaying(key)) { togglePlay(); return }
  const items = categoryArticles(key).map((a, i) => ({ category: key, index: i, title: a.title, audioUrl: a.audio }))
  playQueue(items, 0)
}

onMounted(async () => {
  try {
    const data = await getAllNews()
    newsData.value = data
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
      <div class="header-top-wrap">
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
            <button class="btn btn-outline" @click="playAllTabs" title="Play every story from every tab, in order">
              🎧 Play all tabs
            </button>
            <button v-if="showInstall" class="btn btn-primary" @click="installPWA">📲 Install</button>
            <router-link to="/admin" class="admin-link" title="Admin">⚙️</router-link>
          </div>
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
          <button
            v-if="tabHasAudio(tab.key)"
            class="tab-play-btn"
            :class="{ playing: isTabPlaying(tab.key) }"
            @click.stop.prevent="quickPlayTab(tab.key)"
            :title="`Play ${tab.label}`"
          >
            {{ isTabPlaying(tab.key) ? '⏸' : '▶' }}
          </button>
        </router-link>
      </nav>
    </header>

    <!-- Main Content -->
    <main class="content" :class="{ 'player-active': currentTrack }">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Player error toast -->
    <transition name="fade">
      <div v-if="playerState.error" class="player-toast" :class="{ 'above-dock': currentTrack }">
        {{ playerState.error }}
      </div>
    </transition>

    <!-- Fixed bottom dock: now-playing mini-player + footer tab bar -->
    <div class="bottom-dock">
      <div class="now-playing" v-if="currentTrack">
        <div class="now-playing-progress" @click="onSeek">
          <div class="now-playing-progress-fill" :style="{ width: progressPct + '%' }"></div>
        </div>
        <div class="now-playing-row">
          <div class="now-playing-info">
            <span class="now-playing-icon">{{ tabMeta(currentTrack.category).icon }}</span>
            <div class="now-playing-text">
              <span class="now-playing-title">{{ currentTrack.title }}</span>
              <span class="now-playing-cat">{{ tabMeta(currentTrack.category).label }}</span>
            </div>
          </div>
          <div class="now-playing-controls">
            <button class="np-btn" @click="prev" title="Previous">⏮</button>
            <button class="np-btn np-play" @click="togglePlay" :title="playerState.isPlaying ? 'Pause' : 'Play'">
              {{ playerState.isPlaying ? '⏸' : '▶' }}
            </button>
            <button class="np-btn" @click="next" title="Next">⏭</button>
            <button class="np-btn np-close" @click="stop" title="Stop">✕</button>
          </div>
        </div>
      </div>

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
          <button
            v-if="tabHasAudio(tab.key)"
            class="tab-play-btn"
            :class="{ playing: isTabPlaying(tab.key) }"
            @click.stop.prevent="quickPlayTab(tab.key)"
            :title="`Play ${tab.label}`"
          >
            {{ isTabPlaying(tab.key) ? '⏸' : '▶' }}
          </button>
        </router-link>
      </nav>
    </div>
  </div>
</template>

<style scoped>
.layout { display: flex; flex-direction: column; min-height: 100vh; }

/* ── Header (top, always visible) ── */
.header {
  background: linear-gradient(135deg, #0B1220 0%, #131B2E 100%);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow);
}
.header-top-wrap {
  max-width: 1400px;
  margin: 0 auto;
  padding: 10px 20px 8px;
}

.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.brand { display: flex; align-items: center; gap: 10px; }
.brand-icon { font-size: 26px; }
.brand-title { display: block; font-size: 17px; font-weight: 700; color: var(--accent-primary); line-height: 1.3; }
.brand-sub { display: block; font-size: 11px; color: var(--text-muted); }

/* ── Header tab bar: same full-bleed banded treatment as the footer bar ── */
.header-tabs {
  display: flex;
  background: rgba(19, 27, 46, 0.97);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  padding: 0 8px;
}

.header-tab {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  padding: 8px 4px 10px;
  min-width: 0;
  border-bottom: 2px solid transparent;
  color: var(--text-muted);
  text-decoration: none;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.2px;
  transition: all 0.2s;
}
.header-tab:hover { color: var(--text-secondary); }
.header-tab.active { color: var(--accent-primary); border-bottom-color: var(--accent-primary); background: rgba(245,158,11,0.06); }
.header-tab .tab-icon { font-size: 19px; line-height: 1; }
.header-tab .tab-label { line-height: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }

.header-actions { display: flex; align-items: center; gap: 10px; }
.admin-link {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: 8px;
  color: var(--text-muted); text-decoration: none; font-size: 15px;
  transition: all 0.2s;
}
.admin-link:hover { color: var(--accent-primary); background: rgba(255,255,255,0.04); }

.content { flex: 1; max-width: 1400px; width: 100%; margin: 0 auto; padding: 24px 24px 96px; }
.content.player-active { padding-bottom: 156px; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ── Fixed bottom dock: now-playing bar + footer tab bar (thumb-reachable on mobile) ── */
.bottom-dock {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(19, 27, 46, 0.97);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-top: 1px solid var(--border);
  box-shadow: 0 -4px 20px rgba(0,0,0,0.4);
  padding-bottom: env(safe-area-inset-bottom, 0px);
  z-index: 200;
}

/* ── Now-playing mini-player ── */
.now-playing { border-bottom: 1px solid var(--border); padding: 8px 12px 6px; }
.now-playing-progress {
  height: 3px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  cursor: pointer;
  margin-bottom: 8px;
}
.now-playing-progress-fill { height: 100%; background: var(--accent-primary); border-radius: 2px; }
.now-playing-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.now-playing-info { display: flex; align-items: center; gap: 8px; min-width: 0; flex: 1; }
.now-playing-icon { font-size: 18px; flex-shrink: 0; }
.now-playing-text { display: flex; flex-direction: column; min-width: 0; }
.now-playing-title {
  font-size: 12px; font-weight: 600; color: var(--text-primary);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%;
}
.now-playing-cat { font-size: 10px; color: var(--text-muted); }
.now-playing-controls { display: flex; align-items: center; gap: 4px; flex-shrink: 0; }
.np-btn {
  background: none; border: none; color: var(--text-secondary);
  font-size: 15px; cursor: pointer; padding: 4px 7px; border-radius: 6px;
  transition: all 0.2s;
}
.np-btn:hover { color: var(--accent-primary); background: rgba(255,255,255,0.06); }
.np-play { font-size: 18px; color: var(--accent-primary); }
.np-close { font-size: 12px; }

.player-toast {
  position: fixed;
  bottom: 96px;
  left: 50%;
  transform: translateX(-50%);
  max-width: calc(100% - 32px);
  background: rgba(19, 27, 46, 0.97);
  border: 1px solid var(--accent-primary);
  color: var(--text-primary);
  font-size: 13px;
  padding: 10px 16px;
  border-radius: 10px;
  box-shadow: var(--shadow);
  z-index: 300;
  text-align: center;
}
.player-toast.above-dock { bottom: 156px; }

.footer-tabs {
  display: flex;
  padding: 0 8px;
}

.footer-tab {
  position: relative;
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

/* ── Quick-play badge on nav tabs: play this category's audio without navigating ── */
.tab-play-btn {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.55);
  color: var(--accent-primary);
  font-size: 7px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s;
}
.tab-play-btn:hover { background: var(--accent-primary); color: #1a1200; }
.tab-play-btn.playing { background: var(--accent-primary); color: #1a1200; }

@media (max-width: 640px) {
  .brand-sub { display: none; }
  .content { padding: 12px 12px 96px; }
  .content.player-active { padding-bottom: 156px; }
  .header-actions { gap: 6px; }
  .header-actions .btn { font-size: 12px; padding: 6px 10px; }
}
</style>
