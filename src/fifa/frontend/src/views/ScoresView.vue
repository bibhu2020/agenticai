<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getScores } from '../services/api.js'
import { toLocalDateTime, localTZAbbr } from '../utils/time.js'

const loading = ref(true)
const error = ref(null)
const matches = ref([])
const filter = ref('all')
const refreshing = ref(false)
const lastRefreshed = ref(null)
const tz = localTZAbbr()
let pollTimer = null

const POLL_MS = 5 * 60 * 1000  // 5 minutes

const filtered = computed(() => {
  if (filter.value === 'all') return matches.value
  if (filter.value === 'live') return matches.value.filter(m => isLive(m))
  if (filter.value === 'final') return matches.value.filter(m => isFinal(m))
  if (filter.value === 'upcoming') return matches.value.filter(m => isUpcoming(m))
  return matches.value
})

const counts = computed(() => ({
  all: matches.value.length,
  live: matches.value.filter(isLive).length,
  final: matches.value.filter(isFinal).length,
  upcoming: matches.value.filter(isUpcoming).length,
}))

function isLive(m) { return /live|progress|half/i.test(m.status || '') }
function isFinal(m) { return /final|ft|ended/i.test(m.status || '') }
function isUpcoming(m) { return /sched|upcoming|tbd/i.test(m.status || '') }

function badgeClass(m) {
  if (isLive(m)) return 'badge-live'
  if (isFinal(m)) return 'badge-final'
  if (isUpcoming(m)) return 'badge-upcoming'
  return 'badge-tbd'
}

function statusLabel(m) {
  if (isLive(m)) return 'LIVE'
  return m.status || 'TBD'
}

function scoreDisplay(m) {
  const hs = m.home_score
  const as = m.away_score
  if (hs === '' || hs === null || hs === undefined) return 'vs'
  return `${hs} – ${as}`
}

async function fetchData() {
  refreshing.value = true
  try {
    const data = await getScores()
    matches.value = Array.isArray(data) ? data : []
    lastRefreshed.value = new Date()
  } catch {}
  refreshing.value = false
}

function lastRefreshedLabel() {
  if (!lastRefreshed.value) return ''
  return lastRefreshed.value.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  try {
    const data = await getScores()
    matches.value = Array.isArray(data) ? data : []
    lastRefreshed.value = new Date()
  } catch (e) {
    error.value = 'Failed to load scores. The daily agent may not have run yet.'
  } finally {
    loading.value = false
  }
  pollTimer = setInterval(fetchData, POLL_MS)
})

onUnmounted(() => clearInterval(pollTimer))
</script>

<template>
  <div class="scores-view">
    <div class="view-header">
      <div class="title-row">
        <h1 class="view-title">⚽ Today's Matches</h1>
        <div class="refresh-status">
          <span v-if="refreshing" class="refreshing-dot"></span>
          <span class="refresh-label">
            {{ refreshing ? 'Updating…' : lastRefreshed ? `Updated ${lastRefreshedLabel()}` : '' }}
          </span>
          <span class="refresh-cadence">· auto every 5 min</span>
        </div>
      </div>
      <div class="filter-pills">

        <button
          v-for="f in ['all','live','final','upcoming']"
          :key="f"
          class="filter-pill"
          :class="{ active: filter === f }"
          @click="filter = f"
        >
          {{ f.charAt(0).toUpperCase() + f.slice(1) }}
          <span class="pill-count">{{ counts[f] }}</span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
      <span>Loading today's matches…</span>
    </div>

    <div v-else-if="error" class="empty-state">
      <div class="empty-icon">⚠️</div>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="filtered.length === 0" class="empty-state">
      <div class="empty-icon">⚽</div>
      <p>No matches found for today.</p>
    </div>

    <div v-else class="matches-grid">
      <div v-for="match in filtered" :key="match.match_id || match.home_team" class="match-card card">
        <!-- Status bar -->
        <div class="match-status-bar">
          <span class="badge" :class="badgeClass(match)">{{ statusLabel(match) }}</span>
          <span class="match-time">{{ toLocalDateTime(match.time_cdt) }} {{ tz }}</span>
          <span class="match-round">{{ match.round }}</span>
        </div>

        <!-- Teams & Score -->
        <div class="teams">
          <div class="team home">
            <img v-if="match.home_logo" :src="match.home_logo" :alt="match.home_team" class="team-logo" />
            <div v-else class="team-logo-placeholder">🏳️</div>
            <span class="team-name">{{ match.home_team }}</span>
          </div>

          <div class="score-box">
            <span class="score" :class="{ 'score-live': isLive(match) }">
              {{ scoreDisplay(match) }}
            </span>
          </div>

          <div class="team away">
            <img v-if="match.away_logo" :src="match.away_logo" :alt="match.away_team" class="team-logo" />
            <div v-else class="team-logo-placeholder">🏳️</div>
            <span class="team-name">{{ match.away_team }}</span>
          </div>
        </div>

        <!-- Venue -->
        <div class="match-venue" v-if="match.venue">
          📍 {{ match.venue }}<span v-if="match.city">, {{ match.city }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scores-view { display: flex; flex-direction: column; gap: 20px; }

.view-header { display: flex; flex-direction: column; gap: 10px; }
.title-row { display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap; }
.view-title { font-size: 22px; font-weight: 700; }

.refresh-status { display: flex; align-items: center; gap: 5px; }
.refresh-label { font-size: 12px; color: var(--text-muted); }
.refresh-cadence { font-size: 11px; color: var(--text-muted); opacity: 0.6; }
.refreshing-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--accent-green);
  animation: pulse 0.8s infinite;
  flex-shrink: 0;
}

.filter-pills { display: flex; gap: 8px; flex-wrap: wrap; }
.filter-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}
.filter-pill:hover { border-color: var(--accent-gold); color: var(--accent-gold); }
.filter-pill.active { background: rgba(255,215,0,0.15); border-color: var(--accent-gold); color: var(--accent-gold); }
.pill-count { background: rgba(255,255,255,0.1); padding: 1px 7px; border-radius: 10px; font-size: 11px; }

.matches-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.match-card { padding: 0; overflow: hidden; }

.match-status-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  background: rgba(0,0,0,0.3);
  border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
}
.match-time { font-size: 12px; color: var(--text-muted); }
.match-round { font-size: 11px; color: var(--text-muted); margin-left: auto; }

.teams {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 16px;
  gap: 12px;
}
.team {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
}
.team-logo { width: 52px; height: 52px; object-fit: contain; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4)); }
.team-logo-placeholder { width: 52px; height: 52px; display: flex; align-items: center; justify-content: center; font-size: 28px; }
.team-name { font-size: 14px; font-weight: 600; text-align: center; line-height: 1.3; }

.score-box { display: flex; flex-direction: column; align-items: center; flex-shrink: 0; }
.score {
  font-size: 26px;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: 2px;
  min-width: 80px;
  text-align: center;
}
.score-live { color: var(--accent-red); }

.match-venue {
  padding: 8px 16px 12px;
  font-size: 12px;
  color: var(--text-muted);
  border-top: 1px solid var(--border);
}

@media (max-width: 640px) {
  .matches-grid { grid-template-columns: 1fr; }
  .view-header { flex-direction: column; align-items: flex-start; }
}
</style>
