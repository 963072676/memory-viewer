import { useI18n } from 'vue-i18n'
import { useUIStore } from '@/stores/ui'

type ThemeMode = 'light' | 'dark' | 'system'

export function useTheme() {
  const uiStore = useUIStore()
  const { t } = useI18n()

  const modeOrder: ThemeMode[] = ['light', 'dark', 'system']

  function toggleTheme() {
    const idx = modeOrder.indexOf(uiStore.theme as ThemeMode)
    const next = modeOrder[(idx + 1) % modeOrder.length]
    uiStore.setTheme(next)
  }

  /** Human-readable label for the current mode */
  function modeLabel(): string {
    const map: Record<ThemeMode, string> = {
      light: 'i18n.light',
      dark: 'i18n.dark',
      system: 'i18n.system',
    }
    const key = map[uiStore.theme as ThemeMode]
    return key ? t(key) : uiStore.theme
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
