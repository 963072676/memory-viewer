/**
 * P49 r3: Collection hex → var() 引用 自动迁移 helper.
 *
 * 背景:
 * - P48 r2 之前 collection.color 存字面 hex (e.g. '#0072f5')，picker 选择后存为
 *   'var(--collection-color-1)' 引用。
 * - 两套数据共存: 旧 collection 仍存 hex, 新 collection 存 var() 引用.
 * - 旧 collection 在 dark 模式仍渲染 light hex 拼 alpha (i.e. 暗色背景下"亮色块"),
 *   而新 collection 自动跟随主题. 这是 P48 §遗留 #2.
 *
 * 决策:
 * - 仅在 fetch 后做"显示时"迁移, 不写回 backend (避免 P48 r2 已经设计好的"两套数据共存"破裂).
 * - 命中已知 10 色 → 替换为 var() 引用; 命中不到 → 保持原 hex 透传.
 *   (未来若 Picker 扩到 12/15 色, 加映射即可.)
 */

const HEX_TO_VAR: Record<string, string> = {
  '#0072f5': 'var(--collection-color-1)',
  '#22c55e': 'var(--collection-color-2)',
  '#ff9f0a': 'var(--collection-color-3)',
  '#ef4444': 'var(--collection-color-4)',
  '#8b5cf6': 'var(--collection-color-5)',
  '#5856d6': 'var(--collection-color-6)',
  '#ff2d55': 'var(--collection-color-7)',
  '#00c7be': 'var(--collection-color-8)',
  '#ff6482': 'var(--collection-color-9)',
  '#30b0c7': 'var(--collection-color-10)',
  // dark 模式 400 阶旧值（dark 模式也存过 hex 400 阶）
  '#60a5fa': 'var(--collection-color-1)',
  '#4ade80': 'var(--collection-color-2)',
  '#fbbf24': 'var(--collection-color-3)',
  '#f87171': 'var(--collection-color-4)',
  '#a78bfa': 'var(--collection-color-5)',
}

/**
 * 把 collection.color 从 hex 转换为对应的 var() 引用 (如果命中映射表).
 * 已为 var() 引用或未命中则原样返回.
 *
 * @example
 *   migrateCollectionColor('#0072f5')  // → 'var(--collection-color-1)'
 *   migrateCollectionColor('var(--collection-color-3)')  // → 原样
 *   migrateCollectionColor('#abcdef')  // → '#abcdef' (unknown hex 透传)
 */
export function migrateCollectionColor(color: string | null | undefined): string {
  if (!color) return 'var(--collection-color-1)'
  // 已经是 var() 引用 → 原样
  if (color.startsWith('var(')) return color
  // 小写化查找 (用户可能用大写输入)
  const normalized = color.toLowerCase()
  return HEX_TO_VAR[normalized] || color
}
