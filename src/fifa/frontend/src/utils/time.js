/**
 * Parse a "YYYY-MM-DD HH:MM AM/PM CDT" string (CDT = UTC-5) into a JS Date.
 * Returns null if unparseable.
 */
function parseCdt(timeCdt) {
  if (!timeCdt || timeCdt === 'TBD') return null
  const m = timeCdt.match(/(\d{4})-(\d{2})-(\d{2})\s+(\d{1,2}):(\d{2})\s+(AM|PM)/)
  if (!m) return null
  const [, yr, mo, dy, hStr, min, ampm] = m
  let h = parseInt(hStr)
  if (ampm === 'PM' && h !== 12) h += 12
  if (ampm === 'AM' && h === 12) h = 0
  // CDT = UTC-5; add 5 hours to get UTC milliseconds
  return new Date(Date.UTC(+yr, +mo - 1, +dy, h + 5, +min))
}

/** "Jun 24, 2:30 PM" in the browser's local timezone */
export function toLocalDateTime(timeCdt) {
  const d = parseCdt(timeCdt)
  if (!d) return timeCdt || ''
  return d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

/** "2:30 PM" in the browser's local timezone */
export function toLocalTime(timeCdt) {
  const d = parseCdt(timeCdt)
  if (!d) return timeCdt || ''
  return d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
}

/** Short TZ abbreviation from the browser, e.g. "EDT", "PDT" */
export function localTZAbbr() {
  return new Date().toLocaleTimeString(undefined, { timeZoneName: 'short' }).split(' ').pop()
}
