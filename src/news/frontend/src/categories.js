// Metadata for each backend category (used for per-article origin badges
// when several backend categories are merged under one menu tab below).
export const SOURCE_META = {
  world:      { label: 'World',     icon: '🌍' },
  usa:        { label: 'USA',       icon: '🇺🇸' },
  usa_stock:  { label: 'USA Stock', icon: '📈' },
  trump:      { label: 'Trump',     icon: '🏛️' },
  india:      { label: 'India',     icon: '🇮🇳' },
  odisha:     { label: 'Odisha',    icon: '🛕' },
  sports:     { label: 'Sports',    icon: '🏅' },
  cricket:    { label: 'Cricket',   icon: '🏏' },
  ai:         { label: 'AI',        icon: '🤖' },
  quantum:    { label: 'Quantum',   icon: '⚛️' },
  local:          { label: 'Local News', icon: '📍' },
  local_weather:  { label: 'Weather',    icon: '🌤️' },
  local_events:   { label: 'Events',     icon: '🎟️' },
}

// Menu tabs shown in the nav. Each tab merges one or more backend
// categories (`sources`) into a single feed.
export const TABS = [
  { key: 'world',      label: 'World',      icon: '🌍', sources: ['world', 'usa', 'usa_stock', 'trump'] },
  { key: 'india',      label: 'India',      icon: '🇮🇳', sources: ['india', 'odisha'] },
  { key: 'sports',     label: 'Sports',     icon: '🏅', sources: ['sports', 'cricket'] },
  { key: 'technology', label: 'Technology', icon: '💻', sources: ['ai', 'quantum'] },
  { key: 'local',      label: 'Local',      icon: '📍', sources: ['local_weather', 'local', 'local_events'] },
]

export function tabMeta(key) {
  return TABS.find(t => t.key === key) || { key, label: key, icon: '📰', sources: [key] }
}

export function sourceMeta(key) {
  return SOURCE_META[key] || { label: key, icon: '📰' }
}
