<template>
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
</template>

<script setup>
defineProps({
  system: {
    type: Object,
    required: true
  }
})
</script>
