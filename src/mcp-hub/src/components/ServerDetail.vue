<template>
  <div class="detail-view">
    <header class="detail-header">
      <button @click="$emit('close')" class="back-btn">&larr; BACK TO OVERVIEW</button>
      <div class="detail-title">
        <span class="id-tag">{{ server.id.toUpperCase() }}</span>
        <h1>{{ server.name }}</h1>
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
        <p class="markdown-text">{{ server.description }}</p>
        
        <div class="v-header" style="margin-top: 2rem;">TOOLS</div>
        <ul class="tool-list">
          <li v-for="tool in server.tools" :key="tool">
            <code>{{ tool }}</code>
          </li>
        </ul>
      </section>

      <section class="code-section">
        <div class="v-header">USAGE EXAMPLE (PYTHON)</div>
        <div class="code-container">
          <pre><code>{{ server.sample_code }}</code></pre>
        </div>
        
        <div class="v-header" style="margin-top: 2rem;">LIVE SYSTEM LOGS</div>
        <div class="log-terminal">
          <pre><code>{{ logs }}</code></pre>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
defineProps({
  server: {
    type: Object,
    required: true
  },
  logs: {
    type: String,
    required: true
  }
})

defineEmits(['close'])
</script>
