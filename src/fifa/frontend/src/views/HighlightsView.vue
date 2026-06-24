<script setup>
import { ref, onMounted } from 'vue'
import { getHighlights } from '../services/api.js'

const loading = ref(true)
const error = ref(null)
const clips = ref([])
const playing = ref(null)

async function load() {
  try {
    const data = await getHighlights()
    clips.value = Array.isArray(data) ? data : []
  } catch {
    error.value = 'Failed to load highlights.'
  } finally {
    loading.value = false
  }
}

function scoreLabel(clip) {
  const hs = clip.home_score, as = clip.away_score
  if (hs === '' || hs == null) return 'vs'
  return `${hs} – ${as}`
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d + 'T12:00:00').toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

onMounted(load)
</script>

<template>
  <div class="highlights-view">
    <div class="view-header">
      <h1 class="view-title">🎬 Match Highlights</h1>
      <span class="subtitle">Last {{ clips.length }} completed matches · YouTube</span>
    </div>

    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
      <span>Finding highlight videos…</span>
    </div>

    <div v-else-if="error" class="empty-state">
      <div class="empty-icon">⚠️</div>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="clips.length === 0" class="empty-state">
      <div class="empty-icon">🎬</div>
      <p>No completed matches yet — check back after games finish.</p>
    </div>

    <div v-else class="tiles-grid">
      <div
        v-for="clip in clips"
        :key="clip.home_team + clip.away_team"
        class="tile card"
        :class="{ expanded: playing === clip.home_team }"
      >
        <!-- YouTube iframe (when playing) -->
        <div v-if="playing === clip.home_team && clip.youtube_id" class="player-wrap">
          <iframe
            class="yt-player"
            :src="`https://www.youtube-nocookie.com/embed/${clip.youtube_id}?autoplay=1&rel=0`"
            frameborder="0"
            allow="autoplay; encrypted-media; fullscreen"
            allowfullscreen
          ></iframe>
          <button class="close-btn" @click="playing = null">✕ Close</button>
        </div>

        <!-- Thumbnail (when not playing) -->
        <div v-else class="thumb-wrap" @click="clip.youtube_id && (playing = clip.home_team)">
          <!-- YouTube-generated thumbnail -->
          <img
            v-if="clip.thumbnail"
            :src="clip.thumbnail"
            :alt="`${clip.home_team} vs ${clip.away_team}`"
            class="thumb"
            @error="$event.target.src = `https://img.youtube.com/vi/${clip.youtube_id}/hqdefault.jpg`"
          />
          <div v-else class="thumb-placeholder">⚽</div>

          <div class="play-overlay" :class="{ 'no-video': !clip.youtube_id }">
            <div class="play-btn" v-if="clip.youtube_id">▶</div>
            <div class="no-video-msg" v-else>Video not available</div>
          </div>
        </div>

        <!-- Match info bar -->
        <div class="match-bar">
          <div class="team-row">
            <div class="team-info">
              <img v-if="clip.home_logo" :src="clip.home_logo" :alt="clip.home_team" class="team-logo" />
              <span class="team-name">{{ clip.home_team }}</span>
            </div>
            <span class="score-pill">{{ scoreLabel(clip) }}</span>
            <div class="team-info team-info-right">
              <span class="team-name">{{ clip.away_team }}</span>
              <img v-if="clip.away_logo" :src="clip.away_logo" :alt="clip.away_team" class="team-logo" />
            </div>
          </div>
          <div class="match-meta">
            <span class="match-round">{{ clip.round }}</span>
            <span class="match-date">{{ formatDate(clip.date) }}</span>
          </div>
          <div class="actions">
            <button
              v-if="clip.youtube_id"
              class="btn-watch"
              @click="playing = clip.home_team"
            >▶ Watch Highlights</button>
            <a
              v-if="clip.youtube_url"
              :href="clip.youtube_url"
              target="_blank"
              rel="noopener"
              class="btn-yt"
            >YouTube ↗</a>
            <span v-if="!clip.youtube_id" class="no-vid-label">No highlight found</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.highlights-view { display: flex; flex-direction: column; gap: 20px; }

.view-header { display: flex; flex-direction: column; gap: 4px; }
.view-title { font-size: 22px; font-weight: 700; }
.subtitle { font-size: 13px; color: var(--text-muted); }

.tiles-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 18px;
}

.tile {
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.tile.expanded { grid-column: 1 / -1; }

/* Thumbnail */
.thumb-wrap {
  position: relative;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: #000;
  cursor: pointer;
}
.thumb {
  width: 100%; height: 100%;
  object-fit: cover;
  transition: transform 0.3s, opacity 0.3s;
}
.thumb-wrap:hover .thumb { transform: scale(1.03); opacity: 0.85; }
.thumb-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  font-size: 48px; background: var(--bg-secondary);
}

.play-overlay {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,0.2);
  transition: background 0.2s;
}
.thumb-wrap:hover .play-overlay { background: rgba(0,0,0,0.4); }
.play-overlay.no-video { cursor: default; }

.play-btn {
  width: 60px; height: 60px;
  border-radius: 50%;
  background: rgba(255,0,0,0.88);   /* YouTube red */
  color: #fff;
  font-size: 22px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 24px rgba(0,0,0,0.6);
  transition: transform 0.2s, background 0.2s;
  padding-left: 4px;
}
.thumb-wrap:hover .play-btn { transform: scale(1.12); background: rgba(255,0,0,1); }
.no-video-msg {
  background: rgba(0,0,0,0.6); color: var(--text-muted);
  padding: 6px 14px; border-radius: 6px; font-size: 13px;
}

/* YouTube player */
.player-wrap { position: relative; background: #000; }
.yt-player {
  width: 100%; aspect-ratio: 16 / 9; display: block; border: none;
}
.close-btn {
  position: absolute; top: 10px; right: 10px;
  background: rgba(0,0,0,0.7); color: #fff;
  border: none; border-radius: 6px;
  padding: 5px 12px; font-size: 13px; cursor: pointer;
}
.close-btn:hover { background: rgba(200,0,0,0.8); }

/* Match info bar */
.match-bar {
  padding: 12px 14px 14px;
  display: flex; flex-direction: column; gap: 8px;
}

.team-row {
  display: flex; align-items: center; gap: 8px;
}
.team-info {
  display: flex; align-items: center; gap: 6px; flex: 1;
}
.team-info-right { justify-content: flex-end; }
.team-logo { width: 24px; height: 24px; object-fit: contain; flex-shrink: 0; }
.team-name { font-size: 13px; font-weight: 600; }
.score-pill {
  flex-shrink: 0;
  padding: 3px 12px;
  border-radius: 20px;
  background: rgba(255,215,0,0.12);
  border: 1px solid rgba(255,215,0,0.3);
  font-size: 15px; font-weight: 800;
  color: var(--accent-gold);
  letter-spacing: 1px;
}

.match-meta {
  display: flex; justify-content: space-between;
  font-size: 11px; color: var(--text-muted);
}
.match-round { font-style: italic; }

.actions { display: flex; gap: 8px; flex-wrap: wrap; }
.btn-watch {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 6px 14px; border-radius: 6px;
  background: rgba(255,0,0,0.15); border: 1px solid rgba(255,0,0,0.5);
  color: #ff4444; font-size: 13px; font-weight: 600;
  cursor: pointer; transition: background 0.2s;
}
.btn-watch:hover { background: rgba(255,0,0,0.28); }
.btn-yt {
  display: inline-flex; align-items: center;
  padding: 6px 12px; border-radius: 6px;
  background: transparent; border: 1px solid var(--border);
  color: var(--text-muted); font-size: 12px; text-decoration: none;
  transition: border-color 0.2s, color 0.2s;
}
.btn-yt:hover { border-color: #ff4444; color: #ff4444; }
.no-vid-label { font-size: 12px; color: var(--text-muted); align-self: center; }

@media (max-width: 640px) {
  .tiles-grid { grid-template-columns: 1fr; }
  .tile.expanded { grid-column: 1; }
}
</style>
