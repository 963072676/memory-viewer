export type TooltipPlacement = 'top' | 'bottom' | 'left' | 'right'

export interface RectLike {
  top: number
  right: number
  bottom: number
  left: number
  width: number
  height: number
}

export interface ResolveTooltipPositionOptions {
  preferred: TooltipPlacement
  target: RectLike
  tooltip: Pick<RectLike, 'width' | 'height'>
  viewportWidth: number
  viewportHeight: number
  viewportLeft?: number
  viewportTop?: number
  gap?: number
  edgeMargin?: number
}

export interface FindAvailableStepOptions {
  startIndex: number
  direction: 1 | -1
  totalSteps: number
  isAvailable: (index: number) => boolean
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), Math.max(min, max))
}

export function findAvailableStepIndex({
  startIndex,
  direction,
  totalSteps,
  isAvailable,
}: FindAvailableStepOptions) {
  for (let index = startIndex; index >= 0 && index < totalSteps; index += direction) {
    if (isAvailable(index)) return index
  }
  return -1
}

export function resolveTooltipPosition({
  preferred,
  target,
  tooltip,
  viewportWidth,
  viewportHeight,
  viewportLeft = 0,
  viewportTop = 0,
  gap = 16,
  edgeMargin = 12,
}: ResolveTooltipPositionOptions) {
  const viewportRight = viewportLeft + viewportWidth
  const viewportBottom = viewportTop + viewportHeight
  const available = {
    top: target.top - viewportTop - gap,
    bottom: viewportBottom - target.bottom - gap,
    left: target.left - viewportLeft - gap,
    right: viewportRight - target.right - gap,
  }
  const required = {
    top: tooltip.height,
    bottom: tooltip.height,
    left: tooltip.width,
    right: tooltip.width,
  }
  const opposite: Record<TooltipPlacement, TooltipPlacement> = {
    top: 'bottom',
    bottom: 'top',
    left: 'right',
    right: 'left',
  }

  const fallback = opposite[preferred]
  const placement = available[preferred] >= required[preferred]
    ? preferred
    : available[fallback] > available[preferred]
      ? fallback
      : preferred

  let left = target.left + target.width / 2 - tooltip.width / 2
  let top = target.bottom + gap

  if (placement === 'top') top = target.top - gap - tooltip.height
  if (placement === 'right') {
    left = target.right + gap
    top = target.top + target.height / 2 - tooltip.height / 2
  }
  if (placement === 'left') {
    left = target.left - gap - tooltip.width
    top = target.top + target.height / 2 - tooltip.height / 2
  }

  return {
    placement,
    left: clamp(
      left,
      viewportLeft + edgeMargin,
      viewportRight - tooltip.width - edgeMargin,
    ),
    top: clamp(
      top,
      viewportTop + edgeMargin,
      viewportBottom - tooltip.height - edgeMargin,
    ),
  }
}
