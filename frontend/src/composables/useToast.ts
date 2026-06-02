import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'info'

export interface ToastMessage {
  id: number
  type: ToastType
  text: string
}

const toasts = ref<ToastMessage[]>([])
let nextId = 0

const DURATION = 4000

export function useToast() {
  function showToast(text: string, type: ToastType = 'info') {
    const id = nextId++
    toasts.value.push({ id, type, text })
    setTimeout(() => {
      removeToast(id)
    }, DURATION)
  }

  function removeToast(id: number) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  function success(text: string) {
    showToast(text, 'success')
  }

  function error(text: string) {
    showToast(text, 'error')
  }

  function info(text: string) {
    showToast(text, 'info')
  }

  return {
    toasts,
    showToast,
    removeToast,
    success,
    error,
    info,
  }
}
