<script setup>
import { ref, reactive, onMounted, nextTick, computed, watch } from 'vue'
import { 
  Rocket, 
  Search, 
  Activity, 
  MessageSquare, 
  LayoutDashboard,
  BrainCircuit,
  ShieldCheck,
  Landmark,
  AlertTriangle,
  ExternalLink,
  ChevronRight,
  Loader2,
  TrendingUp,
  XCircle,
  Clock,
  Heart,
  Zap,
  LineChart,
  Crown,
  Sparkles
} from 'lucide-vue-next'

const ticker = ref('NVDA')
const provider = ref('openai')
const isAnalyzing = ref(false)
const activeAgent = ref(null)
const logs = ref([])
const results = ref([])
const error = ref(null)
const logContainer = ref(null)

const workflowAgents = [
  { id: 'TechnicalAnalyst', name: 'Technical', role: 'Analyzes chart patterns, SMAs, EMAs, RSI, and MACD for trend identification' },
  { id: 'VolatilityAnalyst', name: 'Volatility', role: 'Studies IV vs HV, VIX context, and option chain liquidity' },
  { id: 'SentimentAnalyst', name: 'Sentiment', role: 'Evaluates market sentiment from news and social media' },
  { id: 'FundamentalAnalyst', name: 'Fundamental', role: 'Reviews P/E ratio, PEG, and balance sheet health' },
  { id: 'StrategyAdvisor', name: 'Strategy', role: 'Recommends optimal option strategies with specific strikes from option chain' },
  { id: 'RiskManager', name: 'Risk', role: 'Final validation and risk assessment before trade execution' }
]

const providers = [
  { id: 'openai', name: 'OpenAI GPT-4o' },
  { id: 'google', name: 'Google Gemini Pro' },
  { id: 'groq', name: 'Groq Llama 3.3' }
]

const agentIcons = {
  'TeamManager': Crown,
  'TechnicalAnalyst': LineChart,
  'VolatilityAnalyst': Zap,
  'SentimentAnalyst': MessageSquare,
  'FundamentalAnalyst': Landmark,
  'StrategyAdvisor': BrainCircuit,
  'RiskManager': ShieldCheck,
  'System': LayoutDashboard,
  'User': Search,
  // Backward compatibility
  'MarketAnalyst': Activity 
}

const agentColors = {
  'TeamManager': '#facc15', // Yellow/Gold
  'TechnicalAnalyst': '#3b82f6', // Blue
  'VolatilityAnalyst': '#ec4899', // Pink/Magenta
  'SentimentAnalyst': '#10b981', // Emerald
  'FundamentalAnalyst': '#f59e0b', // Amber
  'StrategyAdvisor': '#8b5cf6', // Purple
  'RiskManager': '#ef4444', // Red
  'System': '#94a3b8', // Slate
  'User': '#60a5fa',  // Light Blue
  'MarketAnalyst': '#3b82f6'
}

// Cookie Helpers
const setCookie = (name, value, days = 30) => {
  const date = new Date();
  date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
  const expires = "expires=" + date.toUTCString();
  document.cookie = name + "=" + value + ";" + expires + ";path=/;SameSite=Lax";
}

const getCookie = (name) => {
  const nameEQ = name + "=";
  const ca = document.cookie.split(';');
  for(let i=0;i < ca.length;i++) {
    let c = ca[i];
    while (c.charAt(0)==' ') c = c.substring(1,c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
  }
  return null;
}

const getAgentIcon = (source) => {
  return agentIcons[source] || LayoutDashboard
}

const getAgentColor = (source) => {
  return agentColors[source] || '#94a3b8'
}

const scrollToBottom = async () => {
  await nextTick()
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
}

const startAnalysis = () => {
  if (!ticker.value || isAnalyzing.value) return
  
  isAnalyzing.value = true
  logs.value = []
  results.value = []
  error.value = null
  
  const tickers = ticker.value.split(',').map(t => t.trim().toUpperCase()).filter(t => t)
  
  if (tickers.length === 0) {
    error.value = "Please enter at least one ticker."
    isAnalyzing.value = false
    return
  }

  analyzeTicker(tickers[0])
}

const pendingResult = ref(null)
const currentEventSource = ref(null)
const currentAnalysisId = ref(null)

const cancelAnalysis = async () => {
  if (currentAnalysisId.value) {
    try {
      // Send cancel request to backend
      await fetch(`/cancel/${currentAnalysisId.value}`, { method: 'POST' })
    } catch (e) {
      console.error('Failed to cancel analysis:', e)
    }
  }
  
  if (currentEventSource.value) {
    currentEventSource.value.close()
    currentEventSource.value = null
  }
  
  isAnalyzing.value = false
  activeAgent.value = null
  currentAnalysisId.value = null
  
  logs.value.push({
    id: Math.random().toString(36).substr(2, 9),
    source: 'System',
    content: 'Analysis cancelled by user.',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  })
  scrollToBottom()
}

const analyzeTicker = (symbol) => {
  // Use relative path for same-origin serving (FastAPI mounting frontend)
  const url = `/analyze?ticker=${symbol}&provider=${provider.value}`
  
  const eventSource = new EventSource(url)
  currentEventSource.value = eventSource
  pendingResult.value = null

  eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        activeAgent.value = null
        if (pendingResult.value) {
          results.value.push(pendingResult.value)
          pendingResult.value = null
        }
        eventSource.close()
        isAnalyzing.value = false
        return
      }

    try {
      const data = JSON.parse(event.data)
      if (data.error) {
        error.value = data.error
        eventSource.close()
        isAnalyzing.value = false
        return
      }

      if (data.content || data.source) {
        // Capture analysis_id from first message
        if (data.analysis_id && !currentAnalysisId.value) {
          currentAnalysisId.value = data.analysis_id
        }
        
        if (data.source && data.source !== 'System') {
          activeAgent.value = data.source
        }
        
        logs.value.push({
          id: Math.random().toString(36).substr(2, 9),
          source: data.source,
          content: data.content,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        })
        scrollToBottom()
      }

      // If RiskManager output, try to parse JSON for summary
      if (data.source === 'RiskManager') {
        const jsonMatch = data.content.match(/```json\s*([\s\S]*?)\s*```/) || data.content.match(/\{[\s\S]*"final_decision"[\s\S]*\}/)
        if (jsonMatch) {
          try {
            const rawJson = jsonMatch[1] || jsonMatch[0]
            const parsed = JSON.parse(rawJson)
            
            pendingResult.value = {
                ticker: symbol,
                ...parsed
            }
          } catch (e) {
             console.log("Failed to parse result JSON", e)
          }
        }
      }
    } catch (e) {
      console.error("Error parsing message", e)
    }
  }

  eventSource.onerror = (err) => {
    console.error("SSE Error:", err)
    error.value = "Connection to server lost. Make sure the backend is running at http://localhost:8000"
    eventSource.close()
    currentEventSource.value = null
    isAnalyzing.value = false
  }
}

const formatContent = (content) => {
    if (!content) return ''
    let html = content
        // Headers
        .replace(/^### (.*$)/gm, '<h5 class="content-h3">$1</h5>')
        .replace(/^## (.*$)/gm, '<h4 class="content-h2">$1</h4>')
        .replace(/^# (.*$)/gm, '<h3 class="content-h1">$1</h3>')
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Italic
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // Inline Code
        .replace(/`(.*?)`/g, '<code class="inline-code">$1</code>')
        // Blockquotes
        .replace(/^> (.*$)/gm, '<blockquote>$1</blockquote>')
        // Bullet Lists
        .replace(/^\s*[-*+]\s+(.*)$/gm, '<ul><li>$1</li></ul>')
        .replace(/<\/ul>\n<ul>/g, '\n') // Combine consecutive lists
        // Numbered Lists
        .replace(/^\s*\d+\.\s+(.*)$/gm, '<ol><li>$1</li></ol>')
        .replace(/<\/ol>\n<ol>/g, '\n') // Combine consecutive lists
        // New lines to br (only after block elements or within paragraphs)
        .replace(/\n/g, '<br>')
    
    return html
}

const getDecisionColor = (decision) => {
  if (!decision) return 'var(--text-secondary)'
  const d = decision.toUpperCase()
  if (d.includes('TRADE') || d.includes('BUY')) return 'var(--success)'
  if (d.includes('WAIT') || d.includes('HOLD')) return 'var(--warning)'
  return 'var(--danger)'
}

// Persistence Watcher
watch(provider, (newVal) => {
  setCookie('selected_provider', newVal);
})

onMounted(() => {
  const savedProvider = getCookie('selected_provider');
  if (savedProvider && providers.some(p => p.id === savedProvider)) {
    provider.value = savedProvider;
  }
})
</script>

<template>
  <div class="app-wrapper">
    <!-- Header Area -->
    <header class="main-header glass">
      <div class="logo">
        <div class="logo-icon">
          <TrendingUp class="icon-primary" :size="32" />
        </div>
        <div class="logo-text">
          <h1>MARKET<span>ANALYST</span></h1>
          <p>Multi-Agent Trading Intelligence</p>
        </div>
      </div>

      <div class="controls">
        <div class="input-group glass">
          <Search :size="18" class="search-icon" />
          <input 
            v-model="ticker" 
            placeholder="Enter Ticker (e.g. NVDA, AAPL)" 
            @keyup.enter="startAnalysis"
            :disabled="isAnalyzing"
          />
        </div>

        <div class="select-group glass">
          <BrainCircuit :size="18" class="brain-icon" />
          <select v-model="provider" :disabled="isAnalyzing">
            <option v-for="p in providers" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>

        <button 
          class="btn btn-primary" 
          @click="startAnalysis" 
          :disabled="isAnalyzing || !ticker"
        >
          <Loader2 v-if="isAnalyzing" class="animate-spin" :size="20" />
          <Rocket v-else :size="20" />
          <span>{{ isAnalyzing ? 'Analyzing...' : 'Launch Analysis' }}</span>
        </button>

        <button 
          v-if="isAnalyzing"
          class="btn btn-danger" 
          @click="cancelAnalysis"
          title="Cancel Analysis"
        >
          <XCircle :size="20" />
          <span>Cancel</span>
        </button>
      </div>
    </header>

    <main class="dashboard-content">
      <div class="workflow-breadcrumb glass">
        <div 
          v-for="agent in workflowAgents" 
          :key="agent.id" 
          :class="['breadcrumb-item', { active: activeAgent === agent.id }]"
          :title="agent.role"
        >
          <div class="item-icon-wrapper" :style="{ color: getAgentColor(agent.id) }">
            <component :is="getAgentIcon(agent.id)" :size="14" />
            <div v-if="activeAgent === agent.id" class="bulb" :style="{ backgroundColor: getAgentColor(agent.id) }"></div>
          </div>
          <span class="item-label">{{ agent.name }}</span>
          <ChevronRight v-if="agent.id !== 'RiskManager'" :size="14" class="separator" />
        </div>
      </div>

      <!-- Error Alert -->
      <div v-if="error" class="error-alert glass">
        <XCircle :size="24" />
        <p>{{ error }}</p>
        <button @click="error = null"><ChevronRight :size="20" /></button>
      </div>

      <div class="grid-layout">
        <!-- Live Analysis Stream -->
        <section class="panel-logs glass">
          <div class="panel-header">
            <h3><Activity :size="20" /> Live Agent Stream</h3>
            <div v-if="isAnalyzing" class="status-indicator">
              <span class="pulse"></span> Active
            </div>
          </div>
          
          <div class="log-viewport" ref="logContainer">
            <div v-if="logs.length === 0 && !isAnalyzing" class="empty-state">
              <LayoutDashboard :size="48" />
              <p>Ready to analyze. Enter a ticker to begin.</p>
            </div>

            <div v-for="log in logs" :key="log.id" class="log-entry" :style="{ borderLeftColor: getAgentColor(log.source) }">
              <div class="log-meta">
                <component :is="getAgentIcon(log.source)" :size="16" :style="{ color: getAgentColor(log.source) }" />
                <span class="source" :style="{ color: getAgentColor(log.source) }">{{ log.source }}</span>
                <span class="time">{{ log.timestamp }}</span>
              </div>
              <div class="log-content" v-html="formatContent(log.content)"></div>
            </div>
          </div>
        </section>

        <!-- Intelligence Hub (Summary & Cards) -->
        <section class="panel-results">
          <div class="summary-section glass">
            <div class="panel-header">
              <h3><ShieldCheck :size="20" /> Executive Summary</h3>
            </div>
            
            <div class="results-list">
                <div v-if="isAnalyzing" class="loading-state">
                  <div class="sparkles-wrapper">
                    <Sparkles :size="48" class="sparkle-icon" />
                    <div class="sparkle-particles">
                      <span class="particle"></span>
                      <span class="particle"></span>
                      <span class="particle"></span>
                      <span class="particle"></span>
                    </div>
                  </div>
                  <p>Agents analyzing market data...</p>
                </div>
                <div v-else-if="results.length === 0 && !pendingResult" class="empty-state mini">
                    <p>Analysis cards will appear here</p>
                </div>
                
                <TransitionGroup name="list" tag="div" class="transition-container">
                    <!-- Finalized Results -->
                    <div v-for="res in results" :key="res.ticker" class="result-card glass" :style="{ borderColor: getDecisionColor(res.final_decision) }">
                        <div class="card-header">
                            <div class="ticker-badge">{{ res.ticker }}</div>
                            <div class="decision-badge" :style="{ backgroundColor: getDecisionColor(res.final_decision) }">
                                {{ res.final_decision }}
                            </div>
                            <div v-if="res.fundamental_rating || res.rating" class="fundamental-badge" :class="res.fundamental_rating || res.rating">
                                <Heart :size="10" /> {{ res.fundamental_rating || res.rating }}
                            </div>
                            <div class="confidence-badge">
                                {{ res.confidence }}% Confidence
                            </div>
                        </div>
                        
                        <div class="card-body">
                            <h4>{{ res.actionable_recommendation }}</h4>
                            <div v-if="res.entry_price && res.entry_price !== 'N/A'" class="entry-info">
                                <Clock :size="14" />
                                <span>Entry Signal: <strong>{{ res.entry_signal }}</strong> at <strong>${{ res.entry_price }}</strong></span>
                            </div>
                            <p class="risk-info">
                                <AlertTriangle v-if="res.risk_warning" :size="14" />
                                {{ res.risk_warning || 'No specific risk warnings identified.' }}
                            </p>
                        </div>
                    </div>

                    <!-- Pending/Finalizing State -->
                    <div v-if="pendingResult && isAnalyzing" class="result-card glass finalizing pulse-border">
                        <div class="card-header">
                            <div class="ticker-badge">{{ pendingResult.ticker }}</div>
                            <div class="status-badge">FINALIZING...</div>
                        </div>
                        <div class="card-body">
                            <p>Agents are confirming the strategy. Hang tight...</p>
                        </div>
                    </div>
                </TransitionGroup>
            </div>
          </div>
        </section>
      </div>
    </main>

    <!-- Footer Disclaimer -->
    <footer class="main-footer glass">
      <div class="footer-content">
        <div class="disclaimer-info">
          <AlertTriangle :size="16" />
          <span><strong>Trading Disclaimer:</strong> Educational and research purposes only. AI-generated insights may be subject to latency or error. Consult a professional advisor before trading.</span>
        </div>
        <div class="copyright">
          &copy; 2024 Market Analyst AI
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding: 1.5rem;
  gap: 1.5rem;
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  z-index: 100;
}

.logo {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-icon {
  background: var(--accent-gradient);
  padding: 0.5rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.icon-primary {
  color: white;
}

.btn-danger {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.btn-danger:hover:not(:disabled) {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  box-shadow: 0 8px 24px rgba(239, 68, 68, 0.4);
  transform: translateY(-2px);
}

.logo-text h1 {
  font-size: 1.5rem;
  margin: 0;
  line-height: 1;
}

.logo-text h1 span {
  color: var(--accent-primary);
  font-weight: 400;
}

.logo-text p {
  font-size: 0.75rem;
  color: var(--text-secondary);
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-top: 0.25rem;
}

.controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.input-group, .select-group {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  gap: 0.75rem;
}

.input-group input {
  background: transparent;
  border: none;
  color: var(--text-primary);
  outline: none;
  font-size: 0.9rem;
  width: 200px;
}

.select-group select {
  background: transparent;
  border: none;
  color: var(--text-primary);
  outline: none;
  font-size: 0.9rem;
  cursor: pointer;
}

.select-group select option {
    background-color: var(--bg-color);
}

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  flex: 1;
}

.grid-layout {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 1.5rem;
  flex: 1;
}

.panel-logs {
  grid-column: 2; /* Move to right column */
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: calc(100vh - 240px);
}

.panel-header {
  padding: 1.25rem;
  border-bottom: 1px solid var(--glass-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.log-viewport {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.log-entry {
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 0.75rem;
  border-left: 4px solid var(--accent-primary);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  margin-bottom: 0.5rem;
}

.log-entry:hover {
  background: rgba(255, 255, 255, 0.04);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.log-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  color: var(--text-secondary);
  font-size: 0.75rem;
  letter-spacing: 0.05em;
}

.log-meta .source {
  font-weight: 800;
  text-transform: uppercase;
}

.log-meta .time {
  margin-left: auto;
  opacity: 0.5;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
}

.log-content {
  font-size: 1rem;
  line-height: 1.6;
  color: var(--text-primary);
  font-weight: 400;
  word-wrap: break-word;
}

.log-content :deep(strong) {
  color: #fff;
  font-weight: 700;
}

.log-content :deep(em) {
  color: var(--text-secondary);
  font-style: italic;
}

.log-content :deep(br) {
  display: block;
  content: "";
  margin-top: 0.5rem;
}

.log-content :deep(ul), .log-content :deep(ol) {
  margin: 0.75rem 0;
  padding-left: 1.5rem;
}

.log-content :deep(li) {
  margin-bottom: 0.4rem;
}

.log-content :deep(h3), .log-content :deep(h4), .log-content :deep(h5) {
  margin: 1.25rem 0 0.75rem 0;
  color: var(--text-primary);
  font-weight: 700;
  line-height: 1.3;
}

.log-content :deep(.inline-code) {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85em;
  color: var(--accent-primary);
}

.log-content :deep(blockquote) {
  border-left: 3px solid var(--accent-primary);
  background: rgba(255, 255, 255, 0.03);
  padding: 0.75rem 1rem;
  margin: 1rem 0;
  font-style: italic;
  border-radius: 0 0.5rem 0.5rem 0;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  gap: 1.5rem;
}

.sparkles-wrapper {
  position: relative;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sparkle-icon {
  color: var(--accent-primary);
  animation: sparkleGlow 2s ease-in-out infinite;
  filter: drop-shadow(0 0 12px rgba(59, 130, 246, 0.6));
}

@keyframes sparkleGlow {
  0%, 100% { 
    opacity: 1; 
    transform: scale(1) rotate(0deg);
  }
  50% { 
    opacity: 0.7; 
    transform: scale(1.15) rotate(180deg);
  }
}

.sparkle-particles {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

.particle {
  position: absolute;
  width: 8px;
  height: 8px;
  background: linear-gradient(135deg, #60a5fa, #3b82f6);
  border-radius: 50%;
  animation: particleFloat 3s ease-in-out infinite;
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.8);
}

.particle:nth-child(1) {
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.particle:nth-child(2) {
  top: 10%;
  right: 10%;
  animation-delay: 0.75s;
}

.particle:nth-child(3) {
  bottom: 10%;
  left: 10%;
  animation-delay: 1.5s;
}

.particle:nth-child(4) {
  bottom: 10%;
  right: 10%;
  animation-delay: 2.25s;
}

@keyframes particleFloat {
  0%, 100% {
    transform: translateY(0) scale(1);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  50% {
    transform: translateY(-20px) scale(1.2);
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-40px) scale(0.8);
    opacity: 0;
  }
}

.loading-state p {
  color: var(--text-secondary);
  font-size: 0.95rem;
  font-weight: 500;
  animation: fadeInOut 2s ease-in-out infinite;
}

@keyframes fadeInOut {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

.panel-results {
  grid-column: 1; /* Move to left column */
  grid-row: 1;    /* Ensure it stays on the first row */
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.summary-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 400px;
}

.results-list {
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.result-card {
    padding: 1.5rem;
    border-left: 4px solid var(--accent-primary);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.ticker-badge {
    padding: 0.25rem 0.75rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 0.5rem;
    font-weight: 800;
    font-size: 1rem;
}

.decision-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 0.5rem;
    font-weight: 700;
    font-size: 0.8rem;
    color: white;
}

.confidence-badge {
    margin-left: auto;
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.card-body h4 {
    font-size: 1.1rem;
    margin-bottom: 0.75rem;
    line-height: 1.4;
}

.entry-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    margin-bottom: 1rem;
    color: var(--text-primary);
}

.risk-info {
    font-size: 0.85rem;
    color: var(--text-secondary);
    display: flex;
    gap: 0.5rem;
    font-style: italic;
}

.info-card {
  padding: 1.25rem;
  border-left: 4px solid var(--warning);
}

.info-card h4 {
  color: var(--warning);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.info-card p {
    font-size: 0.8rem;
    color: var(--text-secondary);
}

.error-alert {
  padding: 1rem 1.5rem;
  border-left: 4px solid var(--danger);
  display: flex;
  align-items: center;
  gap: 1rem;
  color: var(--danger);
}

.error-alert p {
  flex: 1;
  font-weight: 500;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
  gap: 1rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--success);
}

.pulse {
  width: 8px;
  height: 8px;
  background: var(--success);
  border-radius: 50%;
  box-shadow: 0 0 0 rgba(16, 185, 129, 0.4);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 1024px) {
  .grid-layout {
    grid-template-columns: 1fr;
  }
  .panel-logs {
    height: 500px;
  }
}

.fundamental-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 0.5rem;
    font-weight: 800;
    font-size: 0.7rem;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 0.3rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--glass-border);
}

.fundamental-badge.Strong { color: var(--success); border-color: rgba(16, 185, 129, 0.3); }
.fundamental-badge.Stable { color: var(--accent-primary); border-color: rgba(59, 130, 246, 0.3); }
.fundamental-badge.Weak { color: var(--danger); border-color: rgba(239, 68, 68, 0.3); }

.status-badge {
    font-size: 0.7rem;
    font-weight: 800;
    color: var(--accent-primary);
    letter-spacing: 0.1em;
}

.pulse-border {
    animation: pulse-border 2s infinite;
}

@keyframes pulse-border {
  0% { border-color: var(--glass-border); }
  50% { border-color: var(--accent-primary); }
  100% { border-color: var(--glass-border); }
}

/* Transitions */
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.transition-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
.main-footer {
  margin-top: auto;
  padding: 1rem 2rem;
  z-index: 100;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
}

.disclaimer-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

.disclaimer-info strong {
  color: var(--warning);
}

.copyright {
  font-size: 0.8rem;
  color: var(--text-muted);
  white-space: nowrap;
}

@media (max-width: 1024px) {
  .footer-content {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
}
/* Breadcrumb Styling */
.workflow-breadcrumb {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.75rem 2rem;
  gap: 1.5rem;
  margin-bottom: 0.5rem;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  opacity: 0.4;
  transition: all 0.4s ease;
  cursor: help;
}

.breadcrumb-item:hover {
  opacity: 0.8;
}

.breadcrumb-item.active {
  opacity: 1;
  transform: scale(1.05);
}

.item-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.active .item-icon-wrapper {
  background: rgba(255, 255, 255, 0.15);
  border-color: currentColor;
  box-shadow: 0 0 20px currentColor, inset 0 0 10px currentColor; /* Brighter glow */
}

.item-label {
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-primary);
}

.separator {
  color: var(--text-muted);
  margin-left: 0.5rem;
}

.bulb {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  box-shadow: 0 0 10px currentColor;
  animation: bulb-pulse 1.5s infinite;
}

@keyframes bulb-pulse {
  0% { transform: scale(1); opacity: 1; box-shadow: 0 0 5px currentColor; }
  50% { transform: scale(1.4); opacity: 0.8; box-shadow: 0 0 15px currentColor; }
  100% { transform: scale(1); opacity: 1; box-shadow: 0 0 5px currentColor; }
}

@media (max-width: 1024px) {
  .grid-layout {
    grid-template-columns: 1fr; /* Stack columns on tablet/mobile */
  }

  .panel-results {
    grid-column: 1; /* Both take full width */
    min-height: auto;
  }
  
  .panel-logs {
    grid-column: 1;
    height: 500px;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 0.5rem;
  }

  header {
    flex-direction: column;
    align-items: stretch;
    gap: 1.5rem;
    padding: 1.5rem 1rem;
    height: auto;
  }
  
  .logo {
    justify-content: center;
    width: 100%;
  }

  .controls {
    flex-direction: column;
    width: 100%;
    gap: 0.75rem;
  }
  
  .input-group, 
  .select-group,
  .btn-primary,
  .btn-danger {
    width: 100%;
    min-width: 0;
  }

  .workflow-breadcrumb {
    flex-wrap: wrap; /* Allow wrapping if needed, or row */
    overflow-x: visible; /* No scroll needed now */
    padding-bottom: 0;
    width: 100%;
    justify-content: center; /* Center icons */
  }
  
  .item-label {
    display: none; /* Hide text on mobile as requested */
  }
}
</style>
