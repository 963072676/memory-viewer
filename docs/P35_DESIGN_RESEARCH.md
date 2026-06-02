# P35 — 优秀 UI 调研报告（Vercel + shadcn/ui + Geist）

> **时间**：2026-06-03 · **目标**：作为后续 P36-P∞ UI 优化的「模式参考库」
> **来源**：Vercel Dashboard (2026-02 redesign) + shadcn/ui 规则 + Geist Design System v2

---

## 1. 卡片设计 (Card)

### Vercel/shadcn 标准
- **复合结构**：`CardHeader` (title + description + action) + `CardContent` + `CardFooter`
- **Hover** 只改 `border/bg` 颜色，**禁止** `hover:shadow-lg` / `hover:translate-y`
- **阴影即边框**：`box-shadow: 0 0 0 1px rgba(0,0,0,0.08)` 替代 `border:1px solid`
- **多层材质**：`material-base` (列表卡，6px radius) / `material-medium` (详情卡，12px radius)

### 当前 Memory Viewer 现状
- `MemoryCard.vue` 已用 `unified-card` 复合结构但缺少 `CardAction` slot
- hover 效果未统一（直接看 CSS）

---

## 2. 按钮层级 (Button Hierarchy)

### Vercel/shadcn 标准
- **每屏/每 section 最多 1 个 primary** 按钮
- `primary` = 主操作（New/Save）｜`secondary` (outline) = 支持操作 ｜`ghost` = 行内操作 ｜`destructive` = 危险
- **Destructive 强制 AlertDialog** 二次确认
- 文案 **Verb + Noun Title Case**（"Delete Memory" 不是 "Delete"）

---

## 3. 字体层级 (Typography)

### Vercel/Geist 标准
- **5 个语义类别**：`heading / label / copy / button / mono`
- **最多 3 个字重**（400/500/600），**禁止 bold 700**
- Headlines 用 `letter-spacing: -0.02em` 收紧代替加粗
- 数字用 `font-variant-numeric: tabular-nums`

---

## 4. 间距系统 (Spacing)

### Vercel/shadcn 标准
- **8pt grid + 4pt sub-grid**：4 / 8 / 12 / 16 / 24 / 32 / 48 / 64
- **禁止** `space-x-*` / `space-y-*` → 改用 `flex gap-*`
- **禁止** `p-[15px]` 任意值

---

## 5. 颜色克制 (Color Restraint)

### Vercel/Geist 标准
- **4 级灰度**：`#FAFAFA → #F2F2F2 → #EBEBEB → #171717`
- **1 个交互强调色** `#0072F5`（Vercel）/ `#171717`（Geist）
- **状态色仅作 ≤10px dot**（不掺在背景填充里）
- 不用 `dark:` 前缀硬覆盖 → 用 semantic token 自动切换

---

## 6. 数据表格 (Data Table)

### Vercel/Geist/shadcn 标准
- 数字列必须 `tabular-nums`
- 缺失值渲染 `—` (em dash)，不用 `N/A` / `null` / `""`
- 表头是 `<button>` 可排序
- 时间用相对时间（2m ago），7 天后切绝对日期
- 分页范围用 en-dash（`21–40 of 142`）
- 空状态用 `<Empty>` 组件

---

## 7. 状态指示器 (Status Indicators)

### Vercel/Geist 标准
- **StatusDot** = 生命周期（带动画 ≤10px）
- **Badge** = 静态分类（无动画，纯文字）
- **状态点单独成行**，不和 "Status: Ready" 文字重复表达
- 颜色↔含义固定：`green=healthy / red=error / amber=warning / blue=info / gray=neutral`

---

## 8. Dashboard 布局 (Overview)

### Vercel Dashboard 2026-02 新版
- 可缩放侧栏（图标-only ↔ 图标+文字）
- 内容三段：面包屑 → 标题+操作 → 内容卡
- Overview 主页刻意移除冗余 header
- Stats 卡：标题 14/500 → 数值 32/600 → 副标 12/400
- 顶部 filter chips：Search + Pill + Count badge
- Time-grouped activity feed (竖线连续)

---

## 9. Dark Mode

### Vercel 标准
- **Dark mode 是默认**（不是 toggle 里第二项）
- **纯黑 `#000` 画布**（非近黑灰）
- Surface 提升靠 box-shadow 而非色调变亮
- 状态色 dark 模式独立调色（更高饱和度）

---

## 10. 可落地 checklist（直接对照 Memory Viewer）

| # | 模式 | 检查项 |
|---|---|---|
| 1 | 卡片 hover | 是否只改 `border/bg` 颜色，无 `hover:shadow-lg`？ |
| 2 | Primary 唯一 | 每个 section 是否只有 1 个 primary 按钮？ |
| 3 | Destructive | Delete 类操作是否 AlertDialog？ |
| 4 | 字号 ≤ 6 | 全局 distinct font size 数是否 ≤ 6？ |
| 5 | 字重 ≤ 3 | 是否出现 `font-bold` (700)？ |
| 6 | Spacing 8/4 倍数 | 有 `[15px]` / `space-y-*` 吗？ |
| 7 | Raw 颜色 | `text-(emerald|red|blue|amber)-(\d00)` 出现？ |
| 8 | tabular-nums | 数字列对齐？ |
| 9 | 缺失值 = `—` | 表格 null 渲染为 `—`？ |
| 10 | StatusDot ≤ 10px | 状态点大小？ |
| 11 | 纯黑 dark | dark 模式背景是否 `#000`？ |
| 12 | Empty 组件 | 空状态有专门组件？ |
| 13 | Time relative | 时间显示相对？ |
| 14 | 按钮文案 | Title Case + Verb + Noun？ |

---

## 参考链接

- Vercel Dashboard: https://vercel.com/dashboard
- shadcn/ui: https://ui.shadcn.com
- Geist Design System: https://vercel.com/geist
- Vercel DESIGN.md: https://github.com/educlopez/design-bites/blob/main/design-mds/vercel.com/DESIGN.md
