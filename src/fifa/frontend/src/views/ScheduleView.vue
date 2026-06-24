<script setup>
import { ref, computed, onMounted } from 'vue'
import { getSchedule } from '../services/api.js'

const loading = ref(true)
const error = ref(null)
const matches = ref([])
const selectedDate = ref('all')

const groupedByDate = computed(() => {
  const groups = {}
  for (const m of matches.value) {
    const d = m.date || 'TBD'
    if (!groups[d]) groups[d] = []
    groups[d].push(m)
  }
  return Object.entries(groups).sort(([a], [b]) => a.localeCompare(b))
})

const uniqueDates = computed(() => ['all', ...Object.keys(groupedByDate.value.reduce((a, [d]) => ({ ...a, [d]: true }), {}))])

const filtered = computed(() => {
  if (selectedDate.value === 'all') return groupedByDate.value
  return groupedByDate.value.filter(([d]) => d === selectedDate.value)
})

function formatDate(dateStr) {
  if (!dateStr || dateStr === 'TBD') return 'TBD'
  try {
    return new Date(dateStr + 'T12:00:00').toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
  } catch { return dateStr }
}

onMounted(async () => {
  try {
    const data = await getSchedule()
    matches.value = Array.isArray(data) ? data : []
  } catch (e) {
    error.value = 'Failed to load schedule.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="schedule-view">
    <div class="view-header">
      <h1 class="view-title">📅 Upcoming Schedule <span class="subtitle">(CDT)</span></h1>
      <div class="date-filter" v-if="uniqueDates.length > 2">
        <select v-model="selectedDate" class="date-select">
          <option value="all">All Dates</option>
          <option v-for="d in uniqueDates.slice(1)" :key="d" :value="d">{{ formatDate(d) }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
      <span>Loading schedule…</span>
    </div>

    <div v-else-if="error" class="empty-state">
      <div class="empty-icon">⚠️</div>
      <p>{{ error }}</p>
    </div>

    <div v-else-if="matches.length === 0" class="empty-state">
      <div class="empty-icon">📅</div>
      <p>No upcoming matches found.</p>
    </div>

    <div v-else class="schedule-groups">
      <div v-for="[date, dayMatches] in filtered" :key="date" class="day-group">
        <div class="day-header">
          <span class="day-label">{{ formatDate(date) }}</span>
          <span class="day-count">{{ dayMatches.length }} match{{ dayMatches.length !== 1 ? 'es' : '' }}</span>
        </div>

        <div class="day-matches">
          <div v-for="match in dayMatches" :key="match.match_id || match.home_team" class="schedule-row card">
            <div class="sched-time">
              <span class="time-main">{{ match.time_cdt ? match.time_cdt.split(' ').slice(1, 3).join(' ') : 'TBD' }}</span>
              <span class="time-tz">CDT</span>
            </div>

            <div class="sched-teams">
              <div class="sched-team">
                <img v-if="match.home_logo" :src="match.home_logo" :alt="match.home_team" class="sched-logo" />
                <span>{{ match.home_team }}</span>
              </div>
              <span class="vs-label">vs</span>
              <div class="sched-team">
                <img v-if="match.away_logo" :src="match.away_logo" :alt="match.away_team" class="sched-logo" />
                <span>{{ match.away_team }}</span>
              </div>
            </div>

            <div class="sched-venue">
              <div class="venue-name">🏟️ {{ match.venue || 'TBD' }}</div>
              <div class="venue-city" v-if="match.city">📍 {{ match.city }}</div>
              <div class="sched-round" v-if="match.round">{{ match.round }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.schedule-view { display: flex; flex-direction: column; gap: 24px; }

.view-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.view-title { font-size: 22px; font-weight: 700; }
.subtitle { font-size: 14px; font-weight: 400; color: var(--text-muted); }

.date-select {
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}
.date-select:focus { outline: none; border-color: var(--accent-gold); }

.schedule-groups { display: flex; flex-direction: column; gap: 20px; }

.day-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255,215,0,0.2);
}
.day-label { font-size: 16px; font-weight: 700; color: var(--accent-gold); }
.day-count { font-size: 12px; color: var(--text-muted); }

.day-matches { display: flex; flex-direction: column; gap: 10px; }

.schedule-row {
  display: grid;
  grid-template-columns: 90px 1fr auto;
  align-items: center;
  gap: 20px;
  padding: 16px 20px;
}

.sched-time {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  text-align: center;
}
.time-main { font-size: 18px; font-weight: 700; color: var(--accent-blue); }
.time-tz { font-size: 10px; color: var(--text-muted); text-transform: uppercase; }

.sched-teams {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.sched-team {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
}
.sched-logo { width: 28px; height: 28px; object-fit: contain; }
.vs-label { font-size: 12px; color: var(--text-muted); font-weight: 500; }

.sched-venue { text-align: right; min-width: 160px; }
.venue-name { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.venue-city { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.sched-round { font-size: 11px; color: var(--accent-gold); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }

@media (max-width: 768px) {
  .schedule-row { grid-template-columns: 70px 1fr; grid-template-rows: auto auto; }
  .sched-venue { grid-column: 1 / -1; text-align: left; }
  .sched-teams { flex-direction: column; align-items: flex-start; }
}
</style>
