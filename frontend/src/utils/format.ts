export function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function truncateText(text: string, maxLen: number = 100): string {
  if (!text || text.length <= maxLen) return text
  return text.slice(0, maxLen) + '...'
}

export function strengthPercent(strength: number): string {
  return `${Math.min(10, Math.max(0, strength)) * 10}%`
}
