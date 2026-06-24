<script setup>
import { ref, onMounted } from 'vue'
import { getHighlights } from '../services/api.js'

const loading = ref(true)
const error = ref(null)
const clips = ref([])
const playing = ref(null)   // id of the currently-expanded video

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

function fmtDuration(secs) {
  if (!secs) return ''
  const m = Math.floor(secs / 60)
  const s = String(secs % 60).padStart(2, '0')
  return `${m}:${s}`
}

function toggle(clip) {
  if (playing.value === clip.id) {
    playing.value = null
  } else {
    playing.value = clip.id
  }
}

onMounted(load)
</script>

<template>
  <div class="highlights-view">
    <div class="view-header">
      <h1 class="view-title">🎬 Match Highlights</h1>
      <span class="subtitle">Latest FIFA World Cup 2026 videos · via ESPN</span>
    </div>

    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
      <span>Loading highlights…</span>
    </div>

    <div v-else-if="error" class="empty-state">
      <div class="empty-icon">⚠️</div>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="clips.length === 0" class="empty-state">
      <div class="empty-icon">🎬</div>
      <p>No highlight videos available right now.</p>
    </div>

    <div v-else class="tiles-grid">
      <div
        v-for="clip in clips"
        :key="clip.id"
        class="tile card"
        :class="{ expanded: playing === clip.id }"
      >
        <!-- Video player (shown when expanded) -->
        <div v-if="playing === clip.id" class="player-wrap">
          <video
            class="player"
            :src="clip.video_url"
            controls
            autoplay
            preload="metadata"
            @error="playing = null"
          ></video>
          <button class="close-btn" @click="playing = null">✕ Close</button>
        </div>

        <!-- Thumbnail (shown when not playing) -->
        <div v-else class="thumb-wrap" @click="toggle(clip)">
          <img
            v-if="clip.thumbnail"
            :src="clip.thumbnail"
            :alt="clip.headline"
            class="thumb"
          />
          <div v-else class="thumb-placeholder">🎬</div>

          <div class="play-overlay">
            <div class="play-btn">▶</div>
          </div>

          <div class="duration-badge" v-if="clip.duration">
            {{ fmtDuration(clip.duration) }}
          </div>
        </div>

        <!-- Caption -->
        <div class="caption">
          <p class="caption-title">{{ clip.headline }}</p>
          <p class="caption-desc" v-if="clip.description && clip.description !== clip.headline">
            {{ clip.description }}
          </p>
          <div class="caption-actions">
            <button v-if="playing !== clip.id && clip.video_url" class="btn-watch" @click="toggle(clip)">
              ▶ Watch
            </button>
            <a v-if="clip.espn_url" :href="clip.espn_url" target="_blank" rel="noopener" class="btn-espn">
              ESPN ↗
            </a>
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

/* 2×2 grid */
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
  transition: transform 0.2s, box-shadow 0.2s;
}
.tile.expanded {
  grid-column: 1 / -1;  /* full-width when playing */
}

/* Thumbnail */
.thumb-wrap {
  position: relative;
  cursor: pointer;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: #000;
}
.thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s, opacity 0.3s;
}
.thumb-wrap:hover .thumb { transform: scale(1.03); opacity: 0.85; }
.thumb-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  font-size: 48px;
  background: var(--bg-secondary);
}

.play-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.25);
  transition: background 0.2s;
}
.thumb-wrap:hover .play-overlay { background: rgba(0,0,0,0.45); }

.play-btn {
  width: 56px; height: 56px;
  border-radius: 50%;
  background: rgba(255, 215, 0, 0.9);
  color: #000;
  font-size: 20px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  transition: transform 0.2s;
  padding-left: 4px; /* optical center for ▶ */
}
.thumb-wrap:hover .play-btn { transform: scale(1.1); }

.duration-badge {
  position: absolute;
  bottom: 8px; right: 8px;
  background: rgba(0,0,0,0.75);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 4px;
}

/* Player */
.player-wrap { position: relative; background: #000; }
.player {
  width: 100%;
  aspect-ratio: 16 / 9;
  display: block;
}
.close-btn {
  position: absolute;
  top: 10px; right: 10px;
  background: rgba(0,0,0,0.7);
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 5px 12px;
  font-size: 13px;
  cursor: pointer;
}
.close-btn:hover { background: rgba(255,0,0,0.7); }

/* Caption */
.caption {
  padding: 12px 14px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}
.caption-title {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--text-primary);
}
.caption-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.caption-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}
.btn-watch {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 5px 14px;
  border-radius: 6px;
  background: rgba(255,215,0,0.15);
  border: 1px solid var(--accent-gold);
  color: var(--accent-gold);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-watch:hover { background: rgba(255,215,0,0.28); }

.btn-espn {
  display: inline-flex; align-items: center;
  padding: 5px 12px;
  border-radius: 6px;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-muted);
  font-size: 12px;
  text-decoration: none;
  transition: border-color 0.2s, color 0.2s;
}
.btn-espn:hover { border-color: var(--accent-gold); color: var(--accent-gold); }

@media (max-width: 640px) {
  .tiles-grid { grid-template-columns: 1fr; }
  .tile.expanded { grid-column: 1; }
}
</style>
