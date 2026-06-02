import { useUIStore } from '@/stores/ui'

type ThemeMode = 'light' | 'dark' | 'system'

export function useTheme() {
  const uiStore = useUIStore()

  const modeOrder: ThemeMode[] = ['light', 'dark', 'system']

  function toggleTheme() {
    const idx = modeOrder.indexOf(uiStore.theme as ThemeMode)
    const next = modeOrder[(idx + 1) % modeOrder.length]
    uiStore.setTheme(next)
  }

  /** Human-readable label for the current mode */
  function modeLabel(): string {
    const map: Record<ThemeMode, string> = {
      light: '浅色',
      dark: '深色',
      system: '跟随系统',
    }
    return map[uiStore.theme as ThemeMode] || uiStore.theme
  }

  /** Icon emoji for the current mode */
  function modeIcon(): string {
    const map: Record<ThemeMode, string> = {
      light: '☀️',
      dark: '🌙',
      system: '💻',
    }
    return map[uiStore.theme as ThemeMode] || '☀️'
  }

  return { theme: uiStore.theme, toggleTheme, modeLabel, modeIcon }
}
