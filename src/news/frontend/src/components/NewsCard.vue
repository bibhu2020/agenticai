<script setup>
import { useLang } from '../lang.js'

defineProps({
  article: { type: Object, required: true },
  icon: { type: String, default: '📰' },
  originLabel: { type: String, default: '' },
  isCurrent: { type: Boolean, default: false },
  isPlaying: { type: Boolean, default: false },
})
defineEmits(['listen'])

const lang = useLang()

function formatDate(dateStr) {
  if (!dateStr) return ''
  // Event dates can be free-text ("Every Saturday", "Wednesdays at 7:00 PM") rather than
  // ISO — Date parses those to Invalid Date without throwing, so check explicitly.
  const parsed = new Date(dateStr)
  if (isNaN(parsed.getTime())) return dateStr
  return parsed.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>

<template>
  <article class="news-card card" :class="{ 'now-playing-card': isCurrent }">
    <div class="thumbnail-wrap">
      <img
        v-if="article.image"
        :src="article.image"
        :alt="article.title"
        class="thumbnail"
        loading="lazy"
        @error="$event.target.style.display='none'"
      />
      <div v-else class="thumbnail-placeholder">{{ icon }}</div>
      <span class="source-badge" v-if="article.source">{{ article.source }}</span>
      <span class="now-playing-badge" v-if="isCurrent">
        {{ isPlaying ? '🔊 Playing' : '⏸ Paused' }}
      </span>
    </div>

    <div class="news-content">
      <div class="news-meta-row">
        <span class="origin-badge" v-if="originLabel">{{ icon }} {{ originLabel }}</span>
        <span class="news-date" v-if="article.published_at">{{ formatDate(article.published_at) }}</span>
      </div>
      <h3 class="news-title">{{ lang.articleTitle(article) }}</h3>
      <p class="news-summary">{{ lang.articleSummary(article) }}</p>
      <div class="news-actions">
        <button
          v-if="lang.articleAudio(article)"
          class="btn btn-outline listen-btn"
          @click="$emit('listen')"
          :class="{ playing: isCurrent && isPlaying }"
        >
          {{ isCurrent && isPlaying ? '⏸ Pause' : '🔊 Listen' }}
        </button>
        <a v-if="article.url" :href="article.url" target="_blank" rel="noopener" class="btn btn-outline read-more">
          Read source →
        </a>
      </div>
    </div>
  </article>
</template>

<style scoped>
.news-card { display: flex; flex-direction: column; overflow: hidden; transition: box-shadow 0.2s, border-color 0.2s; }
.now-playing-card {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 1px var(--accent-primary), 0 8px 30px rgba(245,158,11,0.25);
}

.now-playing-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background: var(--accent-primary);
  color: #1a1200;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 700;
}

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
.news-meta-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.news-date { font-size: 12px; color: var(--text-muted); }
.origin-badge {
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-primary);
  background: rgba(245,158,11,0.1);
  border: 1px solid rgba(245,158,11,0.25);
  padding: 1px 8px;
  border-radius: 10px;
  white-space: nowrap;
}

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

.news-actions { margin-top: auto; display: flex; gap: 8px; flex-wrap: wrap; }
.read-more { font-size: 13px; padding: 7px 14px; }
.listen-btn { font-size: 13px; padding: 7px 14px; }
.listen-btn.playing { border-color: var(--accent-primary); color: var(--accent-primary); }
</style>
