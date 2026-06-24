<script setup>
import { ref, computed, onMounted } from 'vue'
import { getStandings } from '../services/api.js'
import { toLocalDateTime, localTZAbbr } from '../utils/time.js'

const tz = localTZAbbr()

const loading = ref(true)
const error = ref(null)
const groups = ref([])
const knockout = ref({})
const activeGroup = ref(null)
const activeSection = ref('groups') // 'groups' | 'knockout'

const knockoutLabels = {
  r32:   { label: 'Round of 32', icon: '32' },
  r16:   { label: 'Round of 16', icon: '16' },
  qf:    { label: 'Quarterfinals', icon: 'QF' },
  sf:    { label: 'Semifinals', icon: 'SF' },
  third: { label: 'Third Place', icon: '3rd' },
  final: { label: 'Final', icon: '🏆' },
}

const knockoutOrder = ['r32', 'r16', 'qf', 'sf', 'third', 'final']

const hasKnockout = computed(() =>
  knockoutOrder.some(k => (knockout.value[k] || []).length > 0)
)

function noteStyle(row) {
  if (!row.note_color) return {}
  const hex = row.note_color.replace('#', '')
  const r = parseInt(hex.slice(0,2),16), g = parseInt(hex.slice(2,4),16), b = parseInt(hex.slice(4,6),16)
  return { borderLeft: `3px solid ${row.note_color}`, background: `rgba(${r},${g},${b},0.08)` }
}

function scoreDisplay(m) {
  const hs = m.home_score, as = m.away_score
  if (hs === '' || hs == null) return 'vs'
  return `${hs} – ${as}`
}
function isLive(m) { return /live|progress|half/i.test(m.status || '') }
function isFinal(m) { return /final|ft|ended/i.test(m.status || '') }
function badgeClass(m) {
  if (isLive(m)) return 'badge-live'
  if (isFinal(m)) return 'badge-final'
  return 'badge-upcoming'
}
function statusLabel(m) { return isLive(m) ? 'LIVE' : (m.status || 'TBD') }

onMounted(async () => {
  try {
    const data = await getStandings()
    groups.value = data.groups || []
    knockout.value = data.knockout || {}
    if (groups.value.length) activeGroup.value = groups.value[0].group
  } catch {
    error.value = 'Failed to load standings.'
  } finally {
    loading.value = false
  }
})

const activeGroupData = computed(() =>
  groups.value.find(g => g.group === activeGroup.value) || null
)
</script>

<template>
  <div class="standings-view">
    <div class="view-header">
      <h1 class="view-title">🏅 Standings &amp; Bracket</h1>
      <div class="section-toggle">
        <button class="toggle-btn" :class="{ active: activeSection === 'groups' }" @click="activeSection = 'groups'">
          📊 Group Stage
        </button>
        <button class="toggle-btn" :class="{ active: activeSection === 'knockout' }" @click="activeSection = 'knockout'">
          🥊 Knockout
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-spinner">
      <div class="spinner"></div>
      <span>Loading standings…</span>
    </div>

    <div v-else-if="error" class="empty-state">
      <div class="empty-icon">⚠️</div>
      <p>{{ error }}</p>
    </div>

    <template v-else>
      <!-- ── GROUP STAGE ── -->
      <template v-if="activeSection === 'groups'">
        <!-- Group selector -->
        <div class="group-tabs">
          <button
            v-for="g in groups"
            :key="g.group"
            class="group-tab"
            :class="{ active: activeGroup === g.group }"
            @click="activeGroup = g.group"
          >{{ g.group }}</button>
        </div>

        <!-- Group table -->
        <div v-if="activeGroupData" class="group-card card">
          <div class="group-title">{{ activeGroupData.group }}</div>
          <div class="table-wrap">
            <table class="standings-table">
              <thead>
                <tr>
                  <th class="col-pos">#</th>
                  <th class="col-team">Team</th>
                  <th title="Games Played">GP</th>
                  <th title="Wins">W</th>
                  <th title="Draws">D</th>
                  <th title="Losses">L</th>
                  <th title="Goals For">GF</th>
                  <th title="Goals Against">GA</th>
                  <th title="Goal Difference">GD</th>
                  <th class="col-pts" title="Points">Pts</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="row in activeGroupData.rows"
                  :key="row.team"
                  class="team-row"
                  :style="noteStyle(row)"
                >
                  <td class="col-pos">{{ row.pos }}</td>
                  <td class="col-team">
                    <img v-if="row.logo" :src="row.logo" :alt="row.team" class="tbl-logo" />
                    <span class="tbl-name">{{ row.team }}</span>
                  </td>
                  <td>{{ row.gp }}</td>
                  <td>{{ row.w }}</td>
                  <td>{{ row.d }}</td>
                  <td>{{ row.l }}</td>
                  <td>{{ row.gf }}</td>
                  <td>{{ row.ga }}</td>
                  <td :class="{ 'gd-pos': Number(row.gd) > 0, 'gd-neg': Number(row.gd) < 0 }">{{ row.gd }}</td>
                  <td class="col-pts">{{ row.pts }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Legend -->
          <div class="legend" v-if="activeGroupData.rows.some(r => r.note)">
            <div
              v-for="row in activeGroupData.rows.filter(r => r.note)"
              :key="row.note"
              class="legend-item"
            >
              <span class="legend-dot" :style="{ background: row.note_color }"></span>
              <span>{{ row.note }}</span>
            </div>
          </div>
        </div>

        <!-- All groups mini-view (scroll) -->
        <div class="all-groups">
          <div v-for="g in groups" :key="g.group" class="mini-group card" @click="activeGroup = g.group; window?.scrollTo(0,0)">
            <div class="mini-group-title">{{ g.group }}</div>
            <div class="mini-rows">
              <div v-for="row in g.rows" :key="row.team" class="mini-row" :style="noteStyle(row)">
                <span class="mini-pos">{{ row.pos }}</span>
                <img v-if="row.logo" :src="row.logo" :alt="row.team" class="mini-logo" />
                <span class="mini-name">{{ row.team }}</span>
                <span class="mini-pts">{{ row.pts }}pts</span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- ── KNOCKOUT ── -->
      <template v-if="activeSection === 'knockout'">
        <div v-if="!hasKnockout" class="empty-state">
          <div class="empty-icon">🔜</div>
          <p>Knockout stage hasn't started yet.</p>
        </div>

        <div v-else class="knockout-sections">
          <div
            v-for="key in knockoutOrder"
            :key="key"
            v-show="(knockout[key] || []).length > 0"
            class="knockout-round"
          >
            <div class="round-header">
              <span class="round-badge">{{ knockoutLabels[key].icon }}</span>
              <span class="round-name">{{ knockoutLabels[key].label }}</span>
              <span class="round-count">{{ (knockout[key] || []).length }} match{{ (knockout[key] || []).length !== 1 ? 'es' : '' }}</span>
            </div>

            <div class="ko-grid">
              <div v-for="match in knockout[key]" :key="match.match_id || match.home_team" class="ko-card card">
                <div class="ko-status-bar">
                  <span class="badge" :class="badgeClass(match)">{{ statusLabel(match) }}</span>
                  <span class="ko-time">{{ toLocalDateTime(match.time_cdt) }} {{ tz }}</span>
                </div>
                <div class="ko-teams">
                  <div class="ko-team">
                    <img v-if="match.home_logo" :src="match.home_logo" :alt="match.home_team" class="ko-logo" />
                    <span class="ko-name">{{ match.home_team }}</span>
                    <span class="ko-score" :class="{ 'score-live': isLive(match) }">
                      {{ match.home_score !== '' && match.home_score != null ? match.home_score : '-' }}
                    </span>
                  </div>
                  <div class="ko-sep">vs</div>
                  <div class="ko-team ko-team-away">
                    <span class="ko-score ko-score-right" :class="{ 'score-live': isLive(match) }">
                      {{ match.away_score !== '' && match.away_score != null ? match.away_score : '-' }}
                    </span>
                    <span class="ko-name ko-name-right">{{ match.away_team }}</span>
                    <img v-if="match.away_logo" :src="match.away_logo" :alt="match.away_team" class="ko-logo" />
                  </div>
                </div>
                <div class="ko-venue" v-if="match.venue">📍 {{ match.venue }}<span v-if="match.city">, {{ match.city }}</span></div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>

<style scoped>
.standings-view { display: flex; flex-direction: column; gap: 20px; }

.view-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.view-title { font-size: 22px; font-weight: 700; }

.section-toggle { display: flex; gap: 0; border-radius: 10px; overflow: hidden; border: 1px solid var(--border); }
.toggle-btn {
  padding: 8px 18px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}
.toggle-btn.active { background: rgba(255,215,0,0.15); color: var(--accent-gold); }

/* Group tabs */
.group-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.group-tab {
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s;
}
.group-tab:hover { border-color: var(--accent-gold); color: var(--accent-gold); }
.group-tab.active { background: rgba(255,215,0,0.15); border-color: var(--accent-gold); color: var(--accent-gold); }

/* Group card */
.group-card { overflow: hidden; }
.group-title {
  padding: 12px 16px;
  font-size: 16px;
  font-weight: 700;
  color: var(--accent-gold);
  border-bottom: 1px solid var(--border);
  background: rgba(0,0,0,0.2);
}

.table-wrap { overflow-x: auto; }
.standings-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.standings-table th {
  padding: 8px 10px;
  text-align: center;
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  border-bottom: 1px solid var(--border);
  background: rgba(0,0,0,0.15);
  letter-spacing: 0.5px;
}
.standings-table th.col-team { text-align: left; }
.standings-table td {
  padding: 10px 10px;
  text-align: center;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}
.team-row:last-child td { border-bottom: none; }
.team-row:hover { background: rgba(255,255,255,0.03); }

.col-pos { width: 36px; font-weight: 700; color: var(--text-secondary); }
.col-team { text-align: left; }
.col-pts { font-weight: 800; color: var(--accent-gold); font-size: 15px; }

.tbl-logo { width: 22px; height: 22px; object-fit: contain; vertical-align: middle; margin-right: 8px; }
.tbl-name { vertical-align: middle; font-weight: 500; }

.gd-pos { color: var(--accent-green); font-weight: 600; }
.gd-neg { color: var(--accent-red); font-weight: 600; }

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 10px 16px;
  border-top: 1px solid var(--border);
}
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--text-muted); }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

/* All groups mini grid */
.all-groups {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}
.mini-group { padding: 0; overflow: hidden; cursor: pointer; }
.mini-group:hover { transform: translateY(-2px); }
.mini-group-title {
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 700;
  color: var(--accent-gold);
  background: rgba(0,0,0,0.2);
  border-bottom: 1px solid var(--border);
}
.mini-rows { display: flex; flex-direction: column; }
.mini-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  font-size: 13px;
}
.mini-row:last-child { border-bottom: none; }
.mini-pos { width: 16px; color: var(--text-muted); font-weight: 700; font-size: 12px; flex-shrink: 0; }
.mini-logo { width: 18px; height: 18px; object-fit: contain; flex-shrink: 0; }
.mini-name { flex: 1; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.mini-pts { font-weight: 700; color: var(--accent-gold); font-size: 12px; flex-shrink: 0; }

/* Knockout */
.knockout-sections { display: flex; flex-direction: column; gap: 28px; }
.knockout-round { display: flex; flex-direction: column; gap: 12px; }

.round-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}
.round-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 26px;
  padding: 0 8px;
  border-radius: 6px;
  background: rgba(255,215,0,0.15);
  border: 1px solid var(--accent-gold);
  color: var(--accent-gold);
  font-size: 12px;
  font-weight: 800;
}
.round-name { font-size: 17px; font-weight: 700; }
.round-count { font-size: 12px; color: var(--text-muted); margin-left: auto; }

.ko-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
}
.ko-card { overflow: hidden; padding: 0; }
.ko-status-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(0,0,0,0.3);
  border-bottom: 1px solid var(--border);
}
.ko-time { font-size: 11px; color: var(--text-muted); margin-left: auto; }

.ko-teams {
  display: flex;
  align-items: center;
  padding: 14px;
  gap: 8px;
}
.ko-team {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}
.ko-team-away { flex-direction: row-reverse; }
.ko-logo { width: 32px; height: 32px; object-fit: contain; flex-shrink: 0; }
.ko-name { font-size: 13px; font-weight: 600; flex: 1; }
.ko-name-right { text-align: right; }
.ko-sep { font-size: 11px; color: var(--text-muted); flex-shrink: 0; }
.ko-score {
  font-size: 22px;
  font-weight: 800;
  min-width: 24px;
  text-align: center;
  flex-shrink: 0;
}
.ko-score-right { }
.score-live { color: var(--accent-red); }

.ko-venue {
  padding: 6px 14px 10px;
  font-size: 11px;
  color: var(--text-muted);
  border-top: 1px solid var(--border);
}

@media (max-width: 640px) {
  .view-header { flex-direction: column; align-items: flex-start; }
  .ko-grid { grid-template-columns: 1fr; }
  .all-groups { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 400px) {
  .all-groups { grid-template-columns: 1fr; }
}
</style>
