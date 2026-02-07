<template>
  <div class="server-list">
    <div v-for="server in servers" :key="server.id" class="server-row" @click="$emit('view-server', server.id)">
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
</template>

<script setup>
defineProps({
  servers: {
    type: Array,
    required: true
  }
})

defineEmits(['view-server'])

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
</script>
