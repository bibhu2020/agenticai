<script setup>
import { ref, onMounted } from 'vue'
import { adminTrigger, adminStatus, getLocalZip, adminUpdateLocalZip } from '../services/api.js'

const SESSION_KEY = 'news_admin_passphrase'

const passphrase = ref('')
const authed = ref(false)
const authError = ref(null)
const checking = ref(false)

const triggering = ref(false)
const triggerMessage = ref(null)
const status = ref(null)
const statusLoading = ref(false)

const localZip = ref('')
const zipSaving = ref(false)
const zipMessage = ref(null)

async function checkPassphrase(candidate) {
  checking.value = true
  authError.value = null
  try {
    await adminStatus(candidate)
    authed.value = true
    passphrase.value = candidate
    sessionStorage.setItem(SESSION_KEY, candidate)
    await refreshStatus()
    await loadLocalZip()
  } catch (e) {
    authError.value = 'Incorrect passphrase.'
    sessionStorage.removeItem(SESSION_KEY)
  } finally {
    checking.value = false
  }
}

async function refreshStatus() {
  statusLoading.value = true
  try {
    status.value = await adminStatus(passphrase.value)
  } catch {
    status.value = null
  } finally {
    statusLoading.value = false
  }
}

async function forceTrigger() {
  triggering.value = true
  triggerMessage.value = null
  try {
    await adminTrigger(passphrase.value)
    triggerMessage.value = { type: 'success', text: 'Agent run triggered — check back in a few minutes.' }
    await refreshStatus()
  } catch (e) {
    triggerMessage.value = { type: 'error', text: 'Could not trigger the agent run.' }
  } finally {
    triggering.value = false
  }
}

async function loadLocalZip() {
  try {
    const data = await getLocalZip()
    localZip.value = data.zip || ''
  } catch {
    localZip.value = ''
  }
}

async function saveLocalZip() {
  zipSaving.value = true
  zipMessage.value = null
  try {
    await adminUpdateLocalZip(passphrase.value, localZip.value)
    zipMessage.value = { type: 'success', text: 'Zip code saved — use "Force trigger agent" below to apply it now, or it takes effect on the next daily run.' }
  } catch (e) {
    const detail = e?.response?.data?.detail
    zipMessage.value = { type: 'error', text: detail || 'Could not save the zip code.' }
  } finally {
    zipSaving.value = false
  }
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString()
}

onMounted(() => {
  const saved = sessionStorage.getItem(SESSION_KEY)
  if (saved) checkPassphrase(saved)
})
</script>

<template>
  <div class="admin-view">
    <h1 class="view-title">⚙️ Admin</h1>

    <div v-if="!authed" class="card gate">
      <p class="gate-label">Enter the admin passphrase to continue</p>
      <form @submit.prevent="checkPassphrase(passphrase)" class="gate-form">
        <input
          v-model="passphrase"
          type="password"
          placeholder="Passphrase"
          class="passphrase-input"
          autocomplete="off"
        />
        <button type="submit" class="btn btn-primary" :disabled="checking || !passphrase">
          {{ checking ? 'Checking…' : 'Unlock' }}
        </button>
      </form>
      <p v-if="authError" class="auth-error">{{ authError }}</p>
    </div>

    <div v-else class="admin-panel">
      <div class="card status-card">
        <h3>Last agent run</h3>
        <div v-if="statusLoading" class="loading-spinner"><div class="spinner"></div></div>
        <dl v-else-if="status" class="status-grid">
          <dt>Status</dt><dd>{{ status.status || '—' }}</dd>
          <dt>Conclusion</dt><dd>{{ status.conclusion || '—' }}</dd>
          <dt>Started</dt><dd>{{ formatDate(status.created_at) }}</dd>
          <dt v-if="status.html_url">Run</dt>
          <dd v-if="status.html_url"><a :href="status.html_url" target="_blank" rel="noopener">View on GitHub →</a></dd>
        </dl>
        <p v-else class="empty-state">No run history available yet.</p>
        <button class="btn btn-outline" @click="refreshStatus" :disabled="statusLoading">↻ Refresh status</button>
      </div>

      <div class="card zip-card">
        <h3>📍 Local tab zip code</h3>
        <p class="trigger-hint">Sets the location used for the Local tab's news, weather, and events.</p>
        <form @submit.prevent="saveLocalZip" class="zip-form">
          <input
            v-model="localZip"
            type="text"
            inputmode="numeric"
            pattern="\d{5}"
            maxlength="5"
            placeholder="75454"
            class="zip-input"
            autocomplete="off"
          />
          <button type="submit" class="btn btn-primary" :disabled="zipSaving || !localZip">
            {{ zipSaving ? 'Saving…' : 'Save' }}
          </button>
        </form>
        <p v-if="zipMessage" :class="['trigger-message', zipMessage.type]">{{ zipMessage.text }}</p>
      </div>

      <div class="card trigger-card">
        <h3>Force-trigger the daily agent</h3>
        <p class="trigger-hint">Manually runs the news digest agent now, outside its normal 06:00 UTC schedule.</p>
        <button class="btn btn-primary" @click="forceTrigger" :disabled="triggering">
          {{ triggering ? 'Triggering…' : '▶ Force trigger agent' }}
        </button>
        <p v-if="triggerMessage" :class="['trigger-message', triggerMessage.type]">{{ triggerMessage.text }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-view { display: flex; flex-direction: column; gap: 20px; max-width: 560px; margin: 0 auto; }
.view-title { font-size: 22px; font-weight: 700; }

.gate { padding: 24px; display: flex; flex-direction: column; gap: 14px; }
.gate-label { color: var(--text-secondary); font-size: 14px; }
.gate-form { display: flex; gap: 10px; }
.passphrase-input {
  flex: 1;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
}
.passphrase-input:focus { outline: none; border-color: var(--accent-primary); }
.auth-error { color: var(--accent-red); font-size: 13px; }

.admin-panel { display: flex; flex-direction: column; gap: 16px; }
.status-card, .trigger-card, .zip-card { padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.status-card h3, .trigger-card h3, .zip-card h3 { font-size: 15px; font-weight: 700; }

.zip-form { display: flex; gap: 10px; }
.zip-input {
  flex: 1;
  max-width: 140px;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
}
.zip-input:focus { outline: none; border-color: var(--accent-primary); }

.status-grid { display: grid; grid-template-columns: auto 1fr; gap: 6px 14px; font-size: 13px; }
.status-grid dt { color: var(--text-muted); }
.status-grid dd { color: var(--text-secondary); }
.status-grid a { color: var(--accent-secondary); }

.trigger-hint { font-size: 13px; color: var(--text-muted); }
.trigger-message { font-size: 13px; }
.trigger-message.success { color: #4ADE80; }
.trigger-message.error { color: var(--accent-red); }
</style>
