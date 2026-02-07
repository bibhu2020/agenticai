
<template>
  <div id="mcp-hub">
    <nav class="top-nav">
      <div class="nav-brand">MCP<span>HUB</span></div>
      <div class="system-stats">
        <span class="pulse-dot"></span>
        {{ servers.length }} SERVERS ACTIVE
      </div>
    </nav>

    <main class="dashboard-content">
      <div v-if="!selectedServer">
        <div class="summary-bar">
          <div class="summary-item">
            <span class="label">UPTIME</span>
            <span class="value">{{ system.uptime }}</span>
          </div>
          <div class="summary-item">
            <span class="label">THROUGHPUT</span>
            <span class="value">{{ system.throughput }}</span>
          </div>
          <div class="summary-item">
            <span class="label">LATENCY</span>
            <span class="value">{{ system.latency }}</span>
          </div>
        </div>

        <section class="trend-section">
          <div class="trend-header">
             <div class="v-header">USAGE TRENDS</div>
             <div class="range-selector">
                <button v-for="r in ranges" :key="r" :class="{ active: selectedRange === r }" @click="setRange(r)">{{ r.toUpperCase() }}</button>
             </div>
          </div>
          <!-- ... (SVG remains same) ... -->
          <div class="trend-container">
            <div class="y-axis">
               <span v-for="tick in yTicks" :key="tick">{{ tick }}</span>
            </div>
            <div class="trend-chart">
               <svg viewBox="0 0 1000 120" class="sparkline" @mousemove="handleHover" @mouseleave="hoverInfo = null">
                  <line v-for="tick in [0, 33, 66, 100]" :key="tick" x1="0" :y1="110 - tick" x2="1000" :y2="110 - tick" stroke="var(--border)" stroke-width="1" stroke-dasharray="4,4" />
                  <path v-for="chart in getCharts" :key="chart.name" :d="chart.path" fill="none" :stroke="chart.color" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="trend-path" />
                  <line v-if="hoverInfo" :x1="hoverInfo.x" y1="0" :x2="hoverInfo.x" y2="120" stroke="var(--accent)" stroke-width="1" stroke-dasharray="2,2" />
               </svg>

               <div v-if="hoverInfo" class="chart-tooltip" :style="{ left: (hoverInfo.x / 10) + '%' }">
                  <div class="tooltip-header">{{ hoverInfo.label }}</div>
                  <div class="tooltip-body">
                     <div v-for="entry in hoverInfo.entries" :key="entry.name" class="tooltip-row" v-show="entry.val > 0">
                        <span class="dot" :style="{ background: entry.color }"></span>
                        <span class="name">{{ entry.name }}</span>
                        <span class="val">{{ entry.val }}</span>
                     </div>
                  </div>
               </div>
               
               <div class="chart-labels">
                  <span v-for="(l, i) in visibleXLabels" :key="i">{{ l }}</span>
               </div>
            </div>
          </div>
        </section>

        <div class="server-list">
          <div v-for="server in servers" :key="server.id" class="server-row" @click="viewServer(server.id)">
            <div class="row-status">
              <span :class="['status-indicator', getStatusStatus(server.status)]"></span>
            </div>
            <div class="row-info">
              <div class="row-header">
                <span class="server-id">{{ server.id.toUpperCase() }}</span>
                <span class="server-name">{{ server.name }}</span>
              </div>
              <div class="server-desc">{{ server.description }}</div>
            </div>
            <div class="row-metrics">
              <div class="metric">
                <span class="m-val">{{ server.metrics.hourly }}</span>
                <span class="m-lab">1H</span>
              </div>
              <div class="metric">
                <span class="m-val">{{ server.metrics.weekly }}</span>
                <span class="m-lab">7D</span>
              </div>
              <div class="metric">
                <span class="m-val">{{ server.metrics.monthly }}</span>
                <span class="m-lab">30D</span>
              </div>
            </div>
            <div class="row-stage">
               <span :class="['stage-badge', getStatusClass(server.status)]">{{ server.status }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Detail Deep Dive -->
      <div v-else class="detail-view">
        <header class="detail-header">
          <button @click="closeServer" class="back-btn">&larr; BACK TO OVERVIEW</button>
          <div class="detail-title">
            <span class="id-tag">{{ selectedServer.id.toUpperCase() }}</span>
            <h1>{{ selectedServer.name }}</h1>
          </div>
          <div class="detail-actions">
            <div class="status-indicator-pill">
              <span class="pulse-dot"></span> INTEGRATED LOG STREAM
            </div>
          </div>
        </header>

        <div class="detail-grid">
          <section class="doc-section">
            <div class="v-header">DETAILS</div>
            <p class="markdown-text">{{ selectedServer.description }}</p>
            
            <div class="v-header" style="margin-top: 2rem;">TOOLS</div>
            <ul class="tool-list">
              <li v-for="tool in selectedServer.tools" :key="tool">
                <code>{{ tool }}</code>
              </li>
            </ul>
          </section>

          <section class="code-section">
            <div class="v-header">USAGE EXAMPLE (PYTHON)</div>
            <div class="code-container">
              <pre><code>{{ selectedServer.sample_code }}</code></pre>
            </div>
            
            <div class="v-header" style="margin-top: 2rem;">LIVE SYSTEM LOGS</div>
            <div class="log-terminal">
              <pre><code>{{ currentLogs }}</code></pre>
            </div>
          </section>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'

const servers = ref([])
const system = ref({ uptime: '99.9%', throughput: '0/hr', latency: '0ms' })
const usageData = ref({ labels: [], datasets: [] })
const selectedServer = ref(null)
const currentLogs = ref('Initializing terminal...')
const selectedRange = ref('24h')
const ranges = ['1h', '24h', '7d', '30d']
const hoverInfo = ref(null)
let logTimer = null

const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#4ade80']

const viewServer = async (id) => {
  try {
    const res = await fetch(`/api/servers/${id}`)
    selectedServer.value = await res.json()
    window.scrollTo({ top: 0, behavior: 'smooth' })
    fetchLogs(id)
    logTimer = setInterval(() => fetchLogs(id), 5000)
  } catch (e) {
    console.error("Link Desync", e)
  }
}

const closeServer = () => {
  selectedServer.value = null
  if (logTimer) clearInterval(logTimer)
  currentLogs.value = 'Initializing terminal...'
}

const fetchLogs = async (id) => {
  try {
    const res = await fetch(`/api/servers/${id}/logs`)
    const data = await res.json()
    currentLogs.value = data.logs || 'No active log feed.'
  } catch (e) {
    currentLogs.value = 'Neural link disrupted. Retrying...'
  }
}

const setRange = (r) => {
  selectedRange.value = r
  fetchUsage()
}

const fetchUsage = async () => {
  try {
    const res = await fetch(`/api/usage?range=${selectedRange.value}`)
    usageData.value = await res.json()
  } catch (e) {
    console.error("Usage Desync", e)
  }
}

const maxUsage = computed(() => {
  if (!usageData.value.datasets.length) return 1
  return Math.max(...usageData.value.datasets.flatMap(ds => ds.data), 1)
})

const yTicks = computed(() => {
  const max = maxUsage.value
  return [max, Math.floor(max * 0.66), Math.floor(max * 0.33), 0]
})

const visibleXLabels = computed(() => {
  const labels = usageData.value.labels
  if (!labels.length) return []
  
  // Target max 6 labels to prevent overcrowding
  const len = labels.length
  if (len <= 6) return labels
  
  // Calculate a step that gives us roughly 6 ticks
  // e.g. 24 items -> step 4 -> 6 items
  const step = Math.ceil((len - 1) / 5)
  
  return labels.map((l, i) => {
    // Audit: Always show first and last. Show others if they match step.
    if (i === 0 || i === len - 1 || i % step === 0) return l
    return '' // Empty filtered label preserves flex spacing
  })
})

const getCharts = computed(() => {
  const labels = usageData.value.labels
  const datasets = usageData.value.datasets
  if (!labels.length || !datasets.length) return []

  const step = 1000 / (labels.length - 1)
  const max = maxUsage.value

  return datasets.map((ds, idx) => {
    const points = ds.data.map((v, i) => ({
      x: i * step,
      y: 110 - (v / max) * 100,
      val: v,
      label: labels[i]
    }))
    
    const d = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
    return {
      name: ds.name,
      color: colors[idx % colors.length],
      path: d,
      points
    }
  })
})

const handleHover = (event) => {
  const svg = event.currentTarget
  const rect = svg.getBoundingClientRect()
  const x = ((event.clientX - rect.left) / rect.width) * 1000
  
  const labels = usageData.value.labels
  if (!labels.length) return
  const step = 1000 / (labels.length - 1)
  const idx = Math.round(x / step)
  
  if (idx >= 0 && idx < labels.length) {
    const entries = usageData.value.datasets.map((ds, i) => ({
      name: ds.name,
      val: ds.data[idx],
      color: colors[i % colors.length]
    })).sort((a,b) => b.val - a.val)
    
    hoverInfo.value = {
      x: idx * step,
      label: labels[idx],
      entries
    }
  }
}

const sortedByUsage = computed(() => {
  return [...servers.value].sort((a, b) => (b.metrics.raw_monthly || 0) - (a.metrics.raw_monthly || 0)).slice(0, 5)
})

const getStatusClass = (status) => {
  if (!status) return 'stage-offline'
  const s = status.toLowerCase()
  if (s.includes('running')) return 'stage-online'
  if (s.includes('sleeping') || s.includes('building')) return 'stage-warning'
  return 'stage-offline'
}

const getStatusStatus = (status) => {
  if (!status) return 's-offline'
  const s = status.toLowerCase()
  if (s.includes('running')) return 's-online'
  if (s.includes('sleeping') || s.includes('building')) return 's-warning'
  return 's-offline'
}

const fetchData = async () => {
  try {
    const res = await fetch('/api/servers')
    const data = await res.json()
    servers.value = data.servers
    system.value = data.system
  } catch (e) {
    console.error("Link Desync", e)
  }
}

onMounted(() => {
  fetchData()
  fetchUsage()
  setInterval(() => {
    fetchData()
    fetchUsage()
  }, 15000)
})
</script>

<style>
/* App specific overrides */
#mcp-hub {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
}
</style>
