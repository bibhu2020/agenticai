import { reactive, computed } from 'vue'
import { getAllNews } from './services/api.js'
import { ALL_TABS } from './categories.js'

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

const currentTrack = computed(() => state.queue[state.currentIndex] || null)

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
  audioEl.src = track.audioUrl
  audioEl.play().catch(() => {
    state.isPlaying = false
    _flashError('Could not play this article — the audio file may be unavailable.')
  })
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
  audioEl.pause()
  audioEl.removeAttribute('src')
  state.queue = []
  state.currentIndex = -1
  state.isPlaying = false
  state.progress = 0
  state.duration = 0
}

audioEl.addEventListener('ended', () => next())
audioEl.addEventListener('timeupdate', () => { state.progress = audioEl.currentTime })
audioEl.addEventListener('durationchange', () => { state.duration = audioEl.duration || 0 })
audioEl.addEventListener('play', () => { state.isPlaying = true })
audioEl.addEventListener('pause', () => { state.isPlaying = false })

export function usePlayer() {
  return { state, currentTrack, playQueue, playAllTabs, togglePlay, next, prev, seek, stop }
}
