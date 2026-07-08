export const HEADER_TABS = [
  { key: 'world',  label: 'World',  icon: '🌍' },
  { key: 'usa',    label: 'USA',    icon: '🇺🇸' },
  { key: 'india',  label: 'India',  icon: '🇮🇳' },
  { key: 'odisha', label: 'Odisha', icon: '🛕' },
  { key: 'sports', label: 'Sports', icon: '🏅' },
]

export const FOOTER_TABS = [
  { key: 'cricket',   label: 'Cricket',   icon: '🏏' },
  { key: 'usa_stock', label: 'USA Stock', icon: '📈' },
  { key: 'ai',        label: 'AI',        icon: '🤖' },
  { key: 'quantum',   label: 'Quantum',   icon: '⚛️' },
  { key: 'trump',     label: 'Trump',     icon: '🏛️' },
]

export const ALL_TABS = [...HEADER_TABS, ...FOOTER_TABS]

export function tabMeta(key) {
  return ALL_TABS.find(t => t.key === key) || { key, label: key, icon: '📰' }
}
