<script setup>
import { ref, watch, onMounted } from 'vue'
import { getCategoryNews } from '../services/api.js'
import { tabMeta } from '../categories.js'

const props = defineProps({ categoryKey: { type: String, required: true } })

const loading = ref(true)
const error = ref(null)
const articles = ref([])
const generatedAt = ref(null)

function formatDate(dateStr) {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  } catch { return dateStr }
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const data = await getCategoryNews(props.categoryKey)
    articles.value = data.articles || []
    generatedAt.value = data.generated_at
  } catch (e) {
    error.value = 'Failed to load this category — the daily digest may not have run yet.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => props.categoryKey, load)
</script>

<template>
  <div class="category-view">
    <div class="view-header">
      <h1 class="view-title">{{ tabMeta(categoryKey).icon }} {{ tabMeta(categoryKey).label }}</h1>
      <span class="article-count" v-if="articles.length">{{ articles.length }} stories</span>
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
      <div class="empty-icon">{{ tabMeta(categoryKey).icon }}</div>
      <p>No stories yet for this category — check back after the next daily update.</p>
    </div>

    <div v-else class="news-grid">
      <article v-for="(article, idx) in articles" :key="idx" class="news-card card">
        <div class="thumbnail-wrap">
          <img
            v-if="article.image"
            :src="article.image"
            :alt="article.title"
            class="thumbnail"
            loading="lazy"
            @error="$event.target.style.display='none'"
          />
          <div v-else class="thumbnail-placeholder">{{ tabMeta(categoryKey).icon }}</div>
          <span class="source-badge" v-if="article.source">{{ article.source }}</span>
        </div>

        <div class="news-content">
          <span class="news-date" v-if="article.published_at">{{ formatDate(article.published_at) }}</span>
          <h3 class="news-title">{{ article.title }}</h3>
          <p class="news-summary">{{ article.summary }}</p>
          <div class="news-actions">
            <a v-if="article.url" :href="article.url" target="_blank" rel="noopener" class="btn btn-outline read-more">
              Read source →
            </a>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.category-view { display: flex; flex-direction: column; gap: 20px; }

.view-header { display: flex; align-items: center; justify-content: space-between; }
.view-title { font-size: 22px; font-weight: 700; }
.article-count { font-size: 13px; color: var(--text-muted); }

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.news-card { display: flex; flex-direction: column; overflow: hidden; }

.thumbnail-wrap { position: relative; height: 190px; overflow: hidden; background: var(--bg-secondary); flex-shrink: 0; }
.thumbnail { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
.news-card:hover .thumbnail { transform: scale(1.03); }
.thumbnail-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 52px; background: var(--bg-secondary); }

.source-badge {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(0,0,0,0.75);
  color: var(--accent-primary);
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.news-content { display: flex; flex-direction: column; gap: 8px; padding: 16px; flex: 1; }
.news-date { font-size: 12px; color: var(--text-muted); }

.news-title {
  font-size: 16px;
  font-weight: 700;
  line-height: 1.4;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-summary { font-size: 14px; color: var(--text-secondary); line-height: 1.6; flex: 1; }

.news-actions { margin-top: auto; }
.read-more { font-size: 13px; padding: 7px 14px; }

@media (max-width: 640px) {
  .news-grid { grid-template-columns: 1fr; }
}
</style>
