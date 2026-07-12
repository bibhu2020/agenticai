<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { getAllNews } from '../services/api.js'
import { tabMeta, sourceMeta } from '../categories.js'
import { usePlayer } from '../player.js'
import { useLang } from '../lang.js'
import NewsCard from '../components/NewsCard.vue'

const props = defineProps({ groupKey: { type: String, required: true } })
const player = usePlayer()
const lang = useLang()

const loading = ref(true)
const error = ref(null)
const articles = ref([]) // flat: [...weather, ...news, ...events], each tagged with origin
const sectionCounts = ref({ local_weather: 0, local: 0, local_events: 0 })
const cardRefs = ref({})

function setCardRef(idx, el) {
  if (el) cardRefs.value[idx] = el
}

async function scrollToCurrentIfHere() {
  const t = player.currentTrack.value
  if (!t || t.category !== props.groupKey) return
  await nextTick()
  const el = cardRefs.value[t.index]
  const domEl = el?.$el || el
  if (domEl) domEl.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

watch(player.currentTrack, scrollToCurrentIfHere)
watch(articles, scrollToCurrentIfHere)

const queueItems = computed(() => articles.value.map((a, i) => ({
  category: props.groupKey,
  origin: a.origin,
  index: i,
  title: lang.articleTitle(a),
  audioUrl: lang.articleAudio(a),
})))

const hasAnyAudio = computed(() => articles.value.some(a => lang.articleAudio(a)))

function isCurrent(idx) {
  const t = player.currentTrack.value
  return !!t && t.category === props.groupKey && t.index === idx
}

function isTabQueuePlaying() {
  const t = player.currentTrack.value
  return !!t && t.category === props.groupKey && player.state.isPlaying
}

function playAllInTab() {
  if (isTabQueuePlaying()) { player.togglePlay(); return }
  player.playQueue(queueItems.value, 0)
}

function playArticle(idx) {
  if (isCurrent(idx)) { player.togglePlay(); return }
  player.playQueue(queueItems.value, idx)
}

// Each section carries its items' absolute index into `articles` (for playback/isCurrent).
const SECTION_DEFS = [
  { key: 'local_weather', title: 'Weather', empty: 'No weather update yet — check back after the next daily update.' },
  { key: 'local', title: 'Top Local News', empty: 'No local stories yet — check back after the next daily update.' },
  { key: 'local_events', title: "This Week's Events", empty: 'No local events found for the next 7 days.' },
]

const sections = computed(() => {
  const out = []
  let offset = 0
  for (const def of SECTION_DEFS) {
    const count = sectionCounts.value[def.key] || 0
    out.push({
      ...def,
      icon: sourceMeta(def.key).icon,
      items: articles.value.slice(offset, offset + count).map((a, i) => ({ article: a, idx: offset + i })),
    })
    offset += count
  }
  return out
})

async function load() {
  loading.value = true
  error.value = null
  cardRefs.value = {}
  try {
    const data = await getAllNews()
    const weather = data.categories?.local_weather || []
    const news = data.categories?.local || []
    const events = data.categories?.local_events || []
    sectionCounts.value = { local_weather: weather.length, local: news.length, local_events: events.length }
    articles.value = [
      ...weather.map(a => ({ ...a, origin: 'local_weather' })),
      ...news.map(a => ({ ...a, origin: 'local' })),
      ...events.map(a => ({ ...a, origin: 'local_events' })),
    ]
  } catch (e) {
    error.value = 'Failed to load local updates — the daily digest may not have run yet.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => props.groupKey, load)
</script>

<template>
  <div class="local-view">
    <div class="view-header">
      <h1 class="view-title">{{ tabMeta(groupKey).icon }} {{ tabMeta(groupKey).label }}</h1>
      <div class="view-header-actions">
        <button v-if="hasAnyAudio" class="btn btn-outline play-all-btn" @click="playAllInTab">
          {{ isTabQueuePlaying() ? '⏸ Pause' : '▶ Play all in this tab' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
      <span>Loading local updates…</span>
    </div>

    <div v-else-if="error" class="empty-state">
      <div class="empty-icon">⚠️</div>
      <p>{{ error }}</p>
    </div>

    <div v-else class="local-sections">
      <section v-for="section in sections" :key="section.key" class="local-section">
        <h2 class="section-title">{{ section.icon }} {{ section.title }}</h2>
        <div v-if="section.items.length === 0" class="empty-state section-empty">
          <p>{{ section.empty }}</p>
        </div>
        <div v-else class="news-grid">
          <NewsCard
            v-for="entry in section.items"
            :key="entry.idx"
            :ref="el => setCardRef(entry.idx, el)"
            :article="entry.article"
            :icon="section.icon"
            :isCurrent="isCurrent(entry.idx)"
            :isPlaying="player.state.isPlaying"
            @listen="playArticle(entry.idx)"
          />
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.local-view { display: flex; flex-direction: column; gap: 20px; }

.view-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.view-title { font-size: 22px; font-weight: 700; }
.view-header-actions { display: flex; align-items: center; gap: 12px; }
.play-all-btn { white-space: nowrap; }

.local-sections { display: flex; flex-direction: column; gap: 28px; }
.local-section { display: flex; flex-direction: column; gap: 14px; }
.section-title { font-size: 16px; font-weight: 700; color: var(--text-secondary); }
.section-empty { padding: 16px 0; }

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

@media (max-width: 640px) {
  .news-grid { grid-template-columns: 1fr; }
}
</style>
