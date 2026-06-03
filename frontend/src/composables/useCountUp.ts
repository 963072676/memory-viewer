/**
 * useCountUp — 数字 count-up 动画 composable
 *
 * P38 r9: Dashboard 进入感增强。从 0 → target 的缓动滚动动画，
 * 替代原版的"瞬时显示"，让首屏统计有"载入感"。
 *
 * 设计要点:
 * 1. 零依赖 — 纯 `requestAnimationFrame`，不引入新库
 * 2. 缓动函数 — `easeOutCubic`（强调"快进 + 慢停"，数字快速接近目标后微调）
 * 3. 减少动效偏好 — `prefers-reduced-motion` 时直接返回 target
 * 4. 自动取消 — 组件 unmount / 再次触发时清理 RAF，避免内存泄漏
 * 5. 格式化 — 支持 `format` 函数（如 `toLocaleString()` 千分位）
 *
 * 用法:
 * ```vue
 * <script setup>
 * const { value: totalDisplay } = useCountUp(() => stats.value?.total ?? 0, {
 *   duration: 800,
 *   format: (n) => n.toLocaleString(),
 * })
 * </script>
 *
 * <template>
 *   <div class="summary-value">{{ totalDisplay }}</div>
 * </template>
 * ```
 */

import { ref, watch, onUnmounted, type Ref } from 'vue'

export interface UseCountUpOptions {
  /** 动画时长（ms），默认 800 */
  duration?: number
  /** 数字格式化函数，默认 Math.round */
  format?: (n: number) => string
  /** 缓动函数，默认 easeOutCubic */
  easing?: (t: number) => number
  /** 起始值，默认 0 */
  start?: number
}

/** easeOutCubic: t→0 极快，t→1 极慢，强调"目标到达"的视觉确认 */
function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3)
}

export function useCountUp(
  source: Ref<number | null | undefined> | (() => number | null | undefined),
  options: UseCountUpOptions = {},
) {
  const {
    duration = 800,
    format = (n: number) => Math.round(n).toString(),
    easing = easeOutCubic,
    start = 0,
  } = options

  const value = ref<string>(format(start))
  let rafId: number | null = null
  let currentFrom = start
  let currentTo = start
  let currentDisplayValue = start

  // 检测用户是否偏好减少动效
  const prefersReducedMotion =
    typeof window !== 'undefined' &&
    window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

  function resolve(): number {
    const v = typeof source === 'function' ? source() : source.value
    return typeof v === 'number' && Number.isFinite(v) ? v : 0
  }

  function tick(timestamp: number, begin: number) {
    const elapsed = timestamp - begin
    const t = Math.min(elapsed / duration, 1)
    const eased = easing(t)
    currentDisplayValue = currentFrom + (currentTo - currentFrom) * eased
    value.value = format(currentDisplayValue)
    if (t < 1) {
      rafId = requestAnimationFrame((ts) => tick(ts, begin))
    } else {
      // 强制设置最终值，避免缓动函数的浮点误差
      currentDisplayValue = currentTo
      value.value = format(currentTo)
      rafId = null
    }
  }

  function animateTo(target: number) {
    // 减少动效偏好：直接跳到目标值
    if (prefersReducedMotion) {
      currentDisplayValue = target
      value.value = format(target)
      return
    }

    // 取消进行中的动画
    if (rafId !== null) {
      cancelAnimationFrame(rafId)
      rafId = null
    }
    // 从当前显示值继续（不重置到 0），保证刷新时平滑过渡
    currentFrom = currentDisplayValue
    currentTo = target
    rafId = requestAnimationFrame((ts) => tick(ts, ts))
  }

  // 监听 source 变化，自动触发动画
  if (typeof source === 'function') {
    // 函数形式：手动控制 — 暴露 animateTo
    // 不自动 watch（避免闭包陷阱）
  } else {
    watch(
      source,
      (newVal) => {
        animateTo(typeof newVal === 'number' && Number.isFinite(newVal) ? newVal : 0)
      },
      { immediate: true },
    )
  }

  onUnmounted(() => {
    if (rafId !== null) {
      cancelAnimationFrame(rafId)
      rafId = null
    }
  })

  return {
    value,
    animateTo,
    /** 内部状态：当前正在动画的显示值（数字形式，未格式化） */
    _current: currentDisplayValue,
  }
}
