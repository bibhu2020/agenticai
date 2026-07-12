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
const showOriginBadge = computed(() => tabMeta(props.groupKey).sources.length > 1)

const loading = ref(true)
const error = ref(null)
const articles = ref([])
const generatedAt = ref(null)
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

async function load() {
  loading.value = true
  error.value = null
  cardRefs.value = {}
  try {
    const data = await getAllNews()
    const sources = tabMeta(props.groupKey).sources
    articles.value = sources.flatMap(src =>
      (data.categories?.[src] || []).map(a => ({ ...a, origin: src }))
    )
    generatedAt.value = data.generated_at
  } catch (e) {
    error.value = 'Failed to load this category — the daily digest may not have run yet.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => props.groupKey, load)
</script>

<template>
  <div class="category-view">
    <div class="view-header">
      <h1 class="view-title">{{ tabMeta(groupKey).icon }} {{ tabMeta(groupKey).label }}</h1>
      <div class="view-header-actions">
        <button v-if="hasAnyAudio" class="btn btn-outline play-all-btn" @click="playAllInTab">
          {{ isTabQueuePlaying() ? '⏸ Pause' : '▶ Play all in this tab' }}
        </button>
        <span class="article-count" v-if="articles.length">{{ articles.length }} stories</span>
      </div>
    </div>

    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
      <span>Loading top stories…</span>
    </div>

    <div v-else-if="error" class="empty-state">
      <div class="empty-icon">⚠️</div>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="articles.length === 0" class="empty-state">
      <div class="empty-icon">{{ tabMeta(groupKey).icon }}</div>
      <p>No stories yet for this category — check back after the next daily update.</p>
    </div>

    <div v-else class="news-grid">
      <NewsCard
        v-for="(article, idx) in articles"
        :key="idx"
        :ref="el => setCardRef(idx, el)"
        :article="article"
        :icon="sourceMeta(article.origin).icon"
        :originLabel="showOriginBadge ? sourceMeta(article.origin).label : ''"
        :isCurrent="isCurrent(idx)"
        :isPlaying="player.state.isPlaying"
        @listen="playArticle(idx)"
      />
    </div>
  </div>
</template>

<style scoped>
.category-view { display: flex; flex-direction: column; gap: 20px; }

.view-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.view-title { font-size: 22px; font-weight: 700; }
.view-header-actions { display: flex; align-items: center; gap: 12px; }
.article-count { font-size: 13px; color: var(--text-muted); white-space: nowrap; }
.play-all-btn { white-space: nowrap; }

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

@media (max-width: 640px) {
  .news-grid { grid-template-columns: 1fr; }
}
</style>
