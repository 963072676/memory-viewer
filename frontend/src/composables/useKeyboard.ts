import { onMounted, onUnmounted } from 'vue'
import { useUIStore } from '@/stores/ui'

export function useKeyboard() {
  const uiStore = useUIStore()

  function handleKeydown(e: KeyboardEvent) {
    // F47: Command Palette shortcut — always active, even in inputs
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault()
      window.dispatchEvent(new CustomEvent('toggle-command-palette'))
      return
    }

    // Don't trigger shortcuts when typing in inputs
    const target = e.target as HTMLElement
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
      if (e.key === 'Escape') {
        uiStore.setSearch('')
        ;(target as HTMLInputElement).blur()
      }
      return
    }

    switch (e.key) {
      case '/':
        e.preventDefault()
        const searchInput = document.querySelector<HTMLInputElement>('[data-search-input]')
        searchInput?.focus()
        break
      case 'Escape':
        uiStore.setSearch('')
        uiStore.showKeyboardHelp = false
        break
      case 'r':
      case 'R':
        // Refresh is handled by parent component
        window.dispatchEvent(new CustomEvent('app-refresh'))
        break
      case '1':
        uiStore.setTab('all')
        break
      case '2':
        uiStore.setTab('agentmemory')
        break
      case '3':
        uiStore.setTab('hermes')
        break
      case '?':
        uiStore.toggleKeyboardHelp()
        break
    }
  }

  onMounted(() => {
    document.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown)
  })
}
