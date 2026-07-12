import { reactive, computed } from 'vue'

const LANG_KEY = 'news_lang_pref'

const state = reactive({ lang: localStorage.getItem(LANG_KEY) || 'en' })

function setLang(lang) {
  state.lang = lang
  localStorage.setItem(LANG_KEY, lang)
}

function toggleLang() {
  setLang(state.lang === 'hi' ? 'en' : 'hi')
}

const isHindi = computed(() => state.lang === 'hi')

function articleTitle(a) {
  return (state.lang === 'hi' && a.title_hi) || a.title
}

function articleSummary(a) {
  return (state.lang === 'hi' && a.summary_hi) || a.summary
}

function articleAudio(a) {
  return (state.lang === 'hi' && a.audio_hi) || a.audio
}

export function useLang() {
  return { state, isHindi, setLang, toggleLang, articleTitle, articleSummary, articleAudio }
}
