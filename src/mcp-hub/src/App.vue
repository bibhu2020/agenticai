
<template>
  <div id="mcp-hub">
    <nav class="top-nav">
      <div class="nav-brand">
        <a href="/" style="display: flex; align-items: center; color: inherit; text-decoration: none;">
          <svg class="brand-logo" viewBox="0 0 180 180" fill="none" xmlns="http://www.w3.org/2000/svg">
            <g clip-path="url(#clip0_19_13)">
              <path d="M18 84.8528L85.8822 16.9706C95.2548 7.59798 110.451 7.59798 119.823 16.9706V16.9706C129.196 26.3431 129.196 41.5391 119.823 50.9117L68.5581 102.177" stroke="currentColor" stroke-width="12" stroke-linecap="round"/>
              <path d="M69.2652 101.47L119.823 50.9117C129.196 41.5391 144.392 41.5391 153.765 50.9117L154.118 51.2652C163.491 60.6378 163.491 75.8338 154.118 85.2063L92.7248 146.6C89.6006 149.724 89.6006 154.789 92.7248 157.913L105.331 170.52" stroke="currentColor" stroke-width="12" stroke-linecap="round"/>
              <path d="M102.853 33.9411L52.6482 84.1457C43.2756 93.5183 43.2756 108.714 52.6482 118.087V118.087C62.0208 127.459 77.2167 127.459 86.5893 118.087L136.794 67.8822" stroke="currentColor" stroke-width="12" stroke-linecap="round"/>
            </g>
            <defs>
              <clipPath id="clip0_19_13"><rect width="180" height="180" fill="white"/></clipPath>
            </defs>
          </svg>
          MCP<span>HUB</span>
        </a>
      </div>
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
             <div class="chart-legend">
                <div v-for="chart in getCharts" :key="chart.name" 
                     :class="['legend-item', { muted: chart.hidden }]"
                     @click="toggleDataset(chart.name)">
                   <span class="dot" :style="{ background: chart.color }"></span>
                   {{ chart.name }}
                </div>
             </div>
             <div class="range-selector">
                <button v-for="r in ranges" :key="r" :class="{ active: selectedRange === r }" @click="setRange(r)">{{ r.toUpperCase() }}</button>
             </div>
          </div>
          
          <div class="trend-container">
            <div class="y-axis">
               <span v-for="tick in yTicks" :key="tick">{{ tick }}</span>
            </div>
            <div class="trend-chart">
               <svg viewBox="0 0 1000 120" class="sparkline" @mousemove="handleHover" @mouseleave="hoverInfo = null">
                  <!-- Grid -->
                  <line v-for="tick in [0, 33, 66, 100]" :key="tick" x1="0" :y1="110 - tick" x2="1000" :y2="110 - tick" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="4,4" />
                  
                  <!-- Area Fills -->
                  <path v-for="chart in getCharts" :key="'area-'+chart.name" 
                        v-if="!chart.hidden"
                        :d="chart.areaPath" 
                        :fill="chart.color" 
                        style="opacity: 0.1; pointer-events: none;" />

                  <!-- Paths -->
                  <path v-for="chart in getCharts" :key="chart.name" 
                        v-if="!chart.hidden"
                        :d="chart.path" 
                        fill="none" 
                        :stroke="chart.color" 
                        stroke-width="2.5" 
                        stroke-linecap="round" 
                        stroke-linejoin="round" 
                        class="trend-path" />

                  <!-- Hover Vertical -->
                  <line v-if="hoverInfo" :x1="hoverInfo.x" y1="0" :x2="hoverInfo.x" y2="115" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="2,2" />
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
const hiddenDatasets = ref(new Set())
const selectedServer = ref(null)
const currentLogs = ref('Initializing terminal...')
const selectedRange = ref('1h')
const ranges = ['1h', '24h', '7d', '30d']
const hoverInfo = ref(null)
let logTimer = null

const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#4ade80']

const toggleDataset = (name) => {
  if (hiddenDatasets.value.has(name)) {
    hiddenDatasets.value.delete(name)
  } else {
    hiddenDatasets.value.add(name)
  }
}

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
  
  // Format labels to local time
  const formatTime = (ts) => {
    const d = new Date(ts * 1000)
    if (selectedRange.value === '1h') return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    if (selectedRange.value === '24h') return d.toLocaleTimeString([], { hour: '2-digit', minute: '00' })
    return d.toLocaleDateString([], { month: '2-digit', day: '2-digit' })
  }

  if (len <= 6) return labels.map(formatTime)
  
  const step = Math.ceil((len - 1) / 5)
  
  return labels.map((l, i) => {
    if (i === 0 || i === len - 1 || i % step === 0) return formatTime(l)
    return ''
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
    
    // Smoothing (Bezier curves)
    let d = ""
    if (points.length > 0) {
      d = `M ${points[0].x} ${points[0].y}`
      for (let i = 0; i < points.length - 1; i++) {
        const p0 = points[i]
        const p1 = points[i+1]
        const cp1x = p0.x + (p1.x - p0.x) / 3
        const cp2x = p0.x + 2 * (p1.x - p0.x) / 3
        d += ` C ${cp1x} ${p0.y} ${cp2x} ${p1.y} ${p1.x} ${p1.y}`
      }
    }

    const areaPath = d + ` L ${points[points.length-1].x} 110 L ${points[0].x} 110 Z`

    return {
      name: ds.name,
      color: colors[idx % colors.length],
      path: d,
      areaPath,
      points,
      hidden: hiddenDatasets.value.has(ds.name)
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
    const date = new Date(labels[idx] * 1000)
    const formattedLabel = selectedRange.value === '1h' 
        ? date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        : date.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })

    const entries = usageData.value.datasets.map((ds, i) => ({
      name: ds.name,
      val: ds.data[idx],
      color: colors[i % colors.length]
    })).sort((a,b) => b.val - a.val)
    
    hoverInfo.value = {
      x: idx * step,
      label: formattedLabel,
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
  }, 300000)
})
</script>

<style>
/* App specific overrides */
#mcp-hub {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
}

.brand-logo {
  height: 28px;
  width: 28px;
  margin-right: 12px;
  color: var(--accent);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.2s;
}

.legend-item:hover {
  transform: translateY(-1px);
}

.legend-item.muted {
  opacity: 0.3;
}

.legend-item .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  box-shadow: 0 0 5px currentColor;
}

.trend-path {
  transition: opacity 0.3s;
}

.sparkline {
  overflow: visible;
}
</style>
