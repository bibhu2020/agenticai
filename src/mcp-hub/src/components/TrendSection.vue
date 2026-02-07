<template>
  <section class="trend-section">
    <div class="trend-header">
       <div class="v-header">USAGE TRENDS</div>
       <div class="range-selector">
          <button v-for="r in ranges" :key="r" :class="{ active: selectedRange === r }" @click="$emit('update:selectedRange', r)">{{ r.toUpperCase() }}</button>
       </div>
    </div>
    
    <div class="trend-container">
      <div class="chart-legend left-legend">
          <div v-for="chart in getCharts" :key="chart.name" 
               :class="['legend-item', { muted: chart.hidden }]"
               @click="toggleDataset(chart.name)">
             <span class="dot" :style="{ background: chart.color }"></span>
             {{ chart.name }}
          </div>
      </div>
      <div class="y-axis">
         <span v-for="tick in yTicks" :key="tick">{{ tick }}</span>
      </div>
      <div class="trend-chart">
         <svg viewBox="0 0 1000 200" class="sparkline" preserveAspectRatio="none" @mousemove="handleHover" @mouseleave="hoverInfo = null">
            <!-- Grid -->
            <line v-for="tick in [0, 50, 100, 150]" :key="tick" x1="0" :y1="190 - tick" x2="1000" :y2="190 - tick" stroke="var(--border)" stroke-width="0.5" stroke-dasharray="4,4" />
            
            <!-- Area Fills -->
            <template v-for="chart in getCharts" :key="'area-'+chart.name">
              <path v-if="!chart.hidden"
                    :d="chart.areaPath" 
                    :fill="chart.color" 
                    style="opacity: 0.08; pointer-events: none;" 
                    vector-effect="non-scaling-stroke" />
            </template>

            <!-- Paths -->
            <template v-for="chart in getCharts" :key="'path-'+chart.name">
              <path v-if="!chart.hidden"
                    :d="chart.path" 
                    fill="none" 
                    :stroke="chart.color" 
                    stroke-width="2.5" 
                    stroke-linecap="round" 
                    stroke-linejoin="round"
                    vector-effect="non-scaling-stroke" 
                    class="trend-path" />
            </template>

            <!-- Hover Vertical -->
            <line v-if="hoverInfo" :x1="hoverInfo.x" y1="0" :x2="hoverInfo.x" y2="200" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="2,2" vector-effect="non-scaling-stroke" />
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
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  usageData: {
    type: Object,
    required: true
  },
  selectedRange: {
    type: String,
    required: true
  }
})

defineEmits(['update:selectedRange'])

const ranges = ['1h', '24h', '7d', '30d']
const hiddenDatasets = ref(new Set())
const hoverInfo = ref(null)
const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#4ade80']

const toggleDataset = (name) => {
  if (hiddenDatasets.value.has(name)) {
    hiddenDatasets.value.delete(name)
  } else {
    hiddenDatasets.value.add(name)
  }
}

const maxUsage = computed(() => {
  if (!props.usageData.datasets.length) return 1
  return Math.max(...props.usageData.datasets.flatMap(ds => ds.data), 1)
})

const yTicks = computed(() => {
  const max = maxUsage.value
  const roundMax = Math.ceil(max / 5) * 5 || 5
  return [roundMax, Math.floor(roundMax * 0.66), Math.floor(roundMax * 0.33), 0]
})

const visibleXLabels = computed(() => {
  const labels = props.usageData.labels
  if (!labels.length) return []
  
  const len = labels.length
  
  const formatTime = (ts) => {
    const d = new Date(ts * 1000)
    if (props.selectedRange === '1h') return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    if (props.selectedRange === '24h') return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
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
  const labels = props.usageData.labels
  const datasets = props.usageData.datasets
  if (!labels.length || !datasets.length) return []

  const step = 1000 / (labels.length - 1)
  const max = maxUsage.value

  return datasets.map((ds, idx) => {
    const points = ds.data.map((v, i) => ({
      x: i * step,
      y: 190 - (v / max) * 180,
      val: v,
      label: labels[i]
    }))
    
    let d = ""
    let areaPath = ""
    
    if (points.length > 0) {
      d = `M ${points[0].x} ${points[0].y}`
      if (points.length > 1) {
        for (let i = 0; i < points.length - 1; i++) {
          const p0 = points[i]
          const p1 = points[i+1]
          const cp1x = p0.x + (p1.x - p0.x) / 3
          const cp2x = p0.x + 2 * (p1.x - p0.x) / 3
          d += ` C ${cp1x} ${p0.y} ${cp2x} ${p1.y} ${p1.x} ${p1.y}`
        }
      }
      areaPath = d + ` L ${points[points.length-1].x} 190 L ${points[0].x} 190 Z`
    }

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
  
  const labels = props.usageData.labels
  if (!labels.length) return
  const step = 1000 / (labels.length - 1)
  const idx = Math.round(x / step)
  
  if (idx >= 0 && idx < labels.length) {
    const date = new Date(labels[idx] * 1000)
    const formattedLabel = props.selectedRange === '1h' 
        ? date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        : date.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })

    const entries = props.usageData.datasets.map((ds, i) => ({
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
</script>
