<script setup>
import { ref, onMounted } from 'vue'
import { getNews } from '../services/api.js'

const loading = ref(true)
const error = ref(null)
const articles = ref([])
const expanded = ref(new Set())

function toggleExpand(id) {
  if (expanded.value.has(id)) expanded.value.delete(id)
  else expanded.value.add(id)
  expanded.value = new Set(expanded.value)
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  try {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  } catch { return dateStr }
}

function truncate(text, n = 160) {
  if (!text) return ''
  return text.length > n ? text.slice(0, n) + '…' : text
}

onMounted(async () => {
  try {
    const data = await getNews()
    articles.value = Array.isArray(data) ? data : []
  } catch (e) {
    error.value = 'Failed to load news.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="news-view">
    <div class="view-header">
      <h1 class="view-title">📰 FIFA World Cup 2026 News</h1>
      <span class="article-count" v-if="articles.length">{{ articles.length }} articles</span>
    </div>

    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
      <span>Loading news…</span>
    </div>

    <div v-else-if="error" class="empty-state">
      <div class="empty-icon">⚠️</div>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="articles.length === 0" class="empty-state">
      <div class="empty-icon">📰</div>
      <p>No news articles found.</p>
    </div>

    <div v-else class="news-grid">
      <article
        v-for="(article, idx) in articles"
        :key="idx"
        class="news-card card"
        :class="{ expanded: expanded.has(idx) }"
      >
        <!-- Thumbnail -->
        <div class="thumbnail-wrap">
          <img
            v-if="article.thumbnail_url"
            :src="article.thumbnail_url"
            :alt="article.title"
            class="thumbnail"
            loading="lazy"
            @error="$event.target.style.display='none'"
          />
          <div v-else class="thumbnail-placeholder">⚽</div>
          <span class="source-badge">{{ article.source }}</span>
        </div>

        <!-- Content -->
        <div class="news-content">
          <div class="news-meta">
            <span class="news-date">{{ formatDate(article.published_date) }}</span>
          </div>

          <h3 class="news-title">{{ article.title }}</h3>

          <p class="news-summary">
            <span v-if="expanded.has(idx)">{{ article.summary }}</span>
            <span v-else>{{ truncate(article.summary) }}</span>
          </p>

          <div v-if="article.summary && article.summary.length > 160" class="expand-toggle">
            <button class="btn-text" @click="toggleExpand(idx)">
              {{ expanded.has(idx) ? 'Show less ↑' : 'Read more ↓' }}
            </button>
          </div>

          <div class="news-actions">
            <a
              v-if="article.article_url"
              :href="article.article_url"
              target="_blank"
              rel="noopener"
              class="btn btn-outline read-more"
            >
              Full Article →
            </a>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.news-view { display: flex; flex-direction: column; gap: 20px; }

.view-header { display: flex; align-items: center; justify-content: space-between; }
.view-title { font-size: 22px; font-weight: 700; }
.article-count { font-size: 13px; color: var(--text-muted); }

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.news-card { display: flex; flex-direction: column; overflow: hidden; }

.thumbnail-wrap { position: relative; height: 200px; overflow: hidden; background: var(--bg-secondary); flex-shrink: 0; }
.thumbnail { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
.news-card:hover .thumbnail { transform: scale(1.03); }
.thumbnail-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 52px; background: var(--bg-secondary); }

.source-badge {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(0,0,0,0.75);
  color: var(--accent-gold);
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.news-content { display: flex; flex-direction: column; gap: 10px; padding: 16px; flex: 1; }

.news-meta { display: flex; align-items: center; gap: 10px; }
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

.expand-toggle { margin-top: -4px; }
.btn-text { background: none; border: none; color: var(--accent-blue); font-size: 13px; cursor: pointer; padding: 0; }
.btn-text:hover { text-decoration: underline; }

.news-actions { margin-top: auto; }
.read-more { font-size: 13px; padding: 7px 14px; }

@media (max-width: 640px) {
  .news-grid { grid-template-columns: 1fr; }
}
</style>
