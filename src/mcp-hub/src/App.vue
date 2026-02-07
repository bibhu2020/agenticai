<template>
  <div id="mcp-hub">
    <TopNav :serverCount="servers.length" />

    <main class="dashboard-content">
      <div v-if="!selectedServer">
        <SummaryBar :system="system" />

        <TrendSection 
          :usageData="usageData" 
          v-model:selectedRange="selectedRange"
          @update:selectedRange="setRange"
        />

        <ServerList 
          :servers="servers" 
          @view-server="viewServer"
        />
      </div>

      <!-- Detail Deep Dive -->
      <ServerDetail 
        v-else 
        :server="selectedServer" 
        :logs="currentLogs"
        @close="closeServer"
      />
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import TopNav from './components/TopNav.vue'
import SummaryBar from './components/SummaryBar.vue'
import TrendSection from './components/TrendSection.vue'
import ServerList from './components/ServerList.vue'
import ServerDetail from './components/ServerDetail.vue'

const servers = ref([])
const system = ref({ uptime: '99.9%', throughput: '0/hr', latency: '0ms' })
const usageData = ref({ labels: [], datasets: [] })
const selectedServer = ref(null)
const currentLogs = ref('Initializing terminal...')
const selectedRange = ref('1h')
let logTimer = null

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
</style>
