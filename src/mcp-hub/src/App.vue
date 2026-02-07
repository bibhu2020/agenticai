
<template>
  <div id="mcp-hub">
    <header class="dashboard-header">
      <h1>MCP HUB</h1>
      <p class="text-secondary">Central discovery and monitoring for Model Context Protocol servers.</p>
    </header>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">Active Servers</div>
        <div class="stat-value">{{ servers.length }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Calls (Monthly)</div>
        <div class="stat-value">1.2M</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">System Uptime</div>
        <div class="stat-value">99.9%</div>
      </div>
    </div>

    <section class="analytics-section">
      <h2>Usage Trends</h2>
      <div id="usage-chart"></div>
    </section>

    <section class="servers-section">
      <h2>Available Servers</h2>
      <div class="server-grid">
        <div v-for="server in servers" :key="server.name" class="server-card">
          <header>
            <h3>{{ server.name }}</h3>
            <span class="status-badge status-online">Online</span>
          </header>
          <p class="text-secondary">{{ server.description }}</p>
          <div class="metrics-row">
            <div class="metric-item">
              <span class="metric-val">{{ server.metrics.hourly }}</span>
              <span class="metric-lab">Hourly</span>
            </div>
            <div class="metric-item">
              <span class="metric-val">{{ server.metrics.weekly }}</span>
              <span class="metric-lab">Weekly</span>
            </div>
            <div class="metric-item">
              <span class="metric-val">{{ server.metrics.monthly }}</span>
              <span class="metric-lab">Monthly</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import Plotly from 'plotly.js-dist-min'

const servers = ref([])
const usageData = ref({ labels: [], datasets: [] })

const fetchData = async () => {
  try {
    const res = await fetch('/api/servers')
    servers.value = await res.json()
    
    const usageRes = await fetch('/api/usage')
    usageData.value = await usageRes.json()
    
    renderChart()
  } catch (e) {
    console.error("Failed to fetch data", e)
  }
}

const renderChart = () => {
  if (!usageData.value.labels.length) return

  const traces = usageData.value.datasets.map((ds, i) => ({
    x: usageData.value.labels,
    y: ds.data,
    name: ds.name,
    type: 'scatter',
    mode: 'lines+markers',
    line: { shape: 'spline', color: i === 0 ? '#58a6ff' : '#bc8cff' }
  }))

  const layout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { color: '#8b949e', family: 'Inter' },
    margin: { l: 40, r: 20, t: 20, b: 40 },
    xaxis: { gridcolor: '#30363d', zeroline: false },
    yaxis: { gridcolor: '#30363d', zeroline: false },
    legend: { x: 0, y: 1.2, orientation: 'h' }
  }

  Plotly.newPlot('usage-chart', traces, layout, { responsive: true })
}

onMounted(() => {
  fetchData()
  // Refresh every 30s
  setInterval(fetchData, 30000)
})
</script>

<style>
.text-secondary {
  color: var(--text-secondary);
}
</style>
