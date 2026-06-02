/**
 * Sanitize HTML to only allow <em> tags for search highlighting.
 * Prevents XSS attacks from malicious HTML injection.
 */
export function sanitizeHighlight(html: string): string {
  // Only allow <em> and </em> tags, strip everything else
  return html
    .replace(/<(?!\/?em\b)[^>]*>/gi, '')
    .replace(/on\w+="[^"]*"/gi, '')
    .replace(/on\w+='[^']*'/gi, '')
}

/**
 * Highlight query in text, returning safe HTML with <em> tags.
 */
export function highlightText(text: string, query: string): string {
  if (!query || !text) return text
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex = new RegExp(`(${escaped})`, 'gi')
  const highlighted = text.replace(regex, '<em>$1</em>')
  return sanitizeHighlight(highlighted)
}
