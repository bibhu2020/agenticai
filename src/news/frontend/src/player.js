import { reactive, computed } from 'vue'
import { getAllNews } from './services/api.js'
import { ALL_TABS } from './categories.js'
import { router } from './router.js'

const audioEl = new Audio()
audioEl.preload = 'auto'

const state = reactive({
  queue: [],       // [{ category, index, title, audioUrl }]
  currentIndex: -1,
  isPlaying: false,
  progress: 0,     // seconds
  duration: 0,     // seconds
  error: '',
})

let _errorTimer = null
function _flashError(message) {
  state.error = message
  clearTimeout(_errorTimer)
  _errorTimer = setTimeout(() => { state.error = '' }, 4000)
}

let _wakeLock = null
async function _acquireWakeLock() {
  if (!('wakeLock' in navigator) || _wakeLock) return
  try {
    _wakeLock = await navigator.wakeLock.request('screen')
    _wakeLock.addEventListener('release', () => { _wakeLock = null })
  } catch {
    _wakeLock = null
  }
}
async function _releaseWakeLock() {
  if (!_wakeLock) return
  const lock = _wakeLock
  _wakeLock = null
  try { await lock.release() } catch { /* already released */ }
}
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible' && state.isPlaying) _acquireWakeLock()
})

const currentTrack = computed(() => state.queue[state.currentIndex] || null)

// Reassigning audioEl.src to move to a new track aborts any in-flight play()
// request on the previous one, and that rejection can arrive *after* the next
// track has already started loading. _loadToken identifies which _loadAndPlay
// call a given failure belongs to, so a stale rejection from an old, already-
// superseded load never gets misattributed to the track that replaced it.
let _loadToken = 0

function _handleLoadFailure(token) {
  if (token !== _loadToken) return
  state.isPlaying = false
  if (state.currentIndex < state.queue.length - 1) {
    // _loadAndPlay clears state.error as it starts the next track, so flash after.
    _loadAndPlay(state.currentIndex + 1)
    _flashError('Skipped an article — its audio file is unavailable.')
  } else {
    _flashError('Could not play this article — the audio file may be unavailable.')
    stop()
  }
}

function _loadAndPlay(index) {
  const track = state.queue[index]
  if (!track) { stop(); return }
  if (!track.audioUrl) {
    // no audio for this article — skip to the next one in the queue
    if (index < state.queue.length - 1) _loadAndPlay(index + 1)
    else stop()
    return
  }
  state.currentIndex = index
  state.error = ''
  const token = ++_loadToken
  audioEl.src = track.audioUrl
  audioEl.play().catch(() => _handleLoadFailure(token))

  const targetPath = `/${track.category}`
  if (router.currentRoute.value.path !== targetPath) {
    router.replace(targetPath)
  }
}

function playQueue(items, startIndex = 0) {
  const playable = items.filter(i => i.audioUrl)
  if (!playable.length) {
    _flashError('No audio available yet for these stories — check back after the next daily update.')
    return
  }
  state.queue = items
  _loadAndPlay(Math.max(0, Math.min(startIndex, items.length - 1)))
}

async function playAllTabs() {
  try {
    const data = await getAllNews()
    const items = []
    for (const tab of ALL_TABS) {
      const articles = data.categories?.[tab.key] || []
      articles.forEach((a, i) => {
        items.push({ category: tab.key, index: i, title: a.title, audioUrl: a.audio })
      })
    }
    playQueue(items, 0)
  } catch {
    _flashError('Could not load stories to play.')
  }
}

function togglePlay() {
  if (!currentTrack.value) return
  if (state.isPlaying) audioEl.pause()
  else audioEl.play().catch(() => {})
}

function next() {
  if (state.currentIndex < state.queue.length - 1) _loadAndPlay(state.currentIndex + 1)
  else stop()
}

function prev() {
  if (state.currentIndex > 0) _loadAndPlay(state.currentIndex - 1)
}

function seek(seconds) {
  if (!currentTrack.value) return
  audioEl.currentTime = seconds
}

function stop() {
  _loadToken++ // invalidate any in-flight load so its eventual failure is ignored
  audioEl.pause()
  audioEl.removeAttribute('src')
  state.queue = []
  state.currentIndex = -1
  state.isPlaying = false
  state.progress = 0
  state.duration = 0
}

audioEl.addEventListener('error', () => _handleLoadFailure(_loadToken))
audioEl.addEventListener('ended', () => next())
audioEl.addEventListener('timeupdate', () => { state.progress = audioEl.currentTime })
audioEl.addEventListener('durationchange', () => { state.duration = audioEl.duration || 0 })
audioEl.addEventListener('play', () => { state.isPlaying = true; _acquireWakeLock() })
audioEl.addEventListener('pause', () => { state.isPlaying = false; _releaseWakeLock() })

export function usePlayer() {
  return { state, currentTrack, playQueue, playAllTabs, togglePlay, next, prev, seek, stop }
}
