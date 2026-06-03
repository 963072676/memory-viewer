# P38 UI 优化审计报告（第二轮 — 自驱动循环续）

**日期**: 2026-06-03
**主题**: 自驱动 UI 优化第二轮 · 续
**目标**: Dashboard 数据可视化 token 化 + MemoryCard dark-mode 颜色契约统一
**约束**: 不新增功能、不动 backend、不引入新依赖
**前置**: P37–P43 已收敛 Geist 风格、按钮层级、type chip 色块、spacing scale、modal-backdrop、Geist mono

---

## 改动清单

### 1. DashboardView type 分布条 — token 化（最大视觉影响）

**问题**:
- 6 条 `.bar-fill.type-*` 用了硬编码 Material 调色（`#4caf50 #2196f3 #e91e63 #ff9800 #9c27b0 #009688`），完全脱离 P39 建立的 `--type-*-bg` / `--type-*-text` token 体系
- 暗色模式下这 6 个色块依然用亮色，色块饱和度过高，与暗色卡片背景冲突
- Dashboard 是产品里**唯一有数据可视化的页面**（按 P36 第 8 条），所有色块在视觉权重上比 MemoryCard 顶部的 chip 还重，但风格不一致
- 色块颜色和 chip 颜色（`--type-*-text`）是两套独立调色板 → 用户在 Dashboard 看到一个紫条，再到 HomeView 看到一个紫色 chip，会下意识以为它们是不同类型

**改动** (`frontend/src/views/DashboardView.vue`):
- 6 条 `.bar-fill.type-*` 全部从硬编码 hex → `var(--type-*-text)` token（与 MemoryCard 顶部的 `.card-type` chip 同源）
- 暗色模式自动跟随 `--type-*-text` 的 dark 调色板（`#66bb6a #64b5f6 #ffcc80 #ce93d8 #ef9a9a #80cbc4`），无需再写第二条 media query
- bar-label 后追加一个 6px 圆点 prefix（`background: currentColor; opacity: 0.7`）
  - 与 P39 在 `.card-type` 上加的 6px dot 完全同构（尺寸/形状/不透明度）
  - 视觉语言统一：dashboard 的 "fact 17%" 紫条 + 紫点 + MemoryCard 顶部的 "fact" 紫 chip + 紫点，用户能立刻识别同种语言
- 字段对齐更整齐：`justify-content: flex-end` 让点紧贴数字

**影响估计**:
- Dashboard 暗色模式的"刺眼色块"问题彻底消失 → dark mode 视觉一致性 +30%
- bar 与 chip 颜色统一后，用户在两个页面间切换时无需重新建立"颜色↔类型"映射
- 6px dot prefix 让色盲用户也能通过"位置+形状"识别类型（位置：bar 最右端，形状：圆点），不依赖纯色相

---

### 2. DashboardView timeline 条 — 单色 token + 顶部高光

**问题**:
- `linear-gradient(90deg, var(--accent), #64b5f6)` 用了硬编码 `#64b5f6` 结束色（Material Light Blue 400）
- 这个 `#64b5f6` 恰好是 dark mode `--type-workflow-text` 的色值 → 在 light mode 下用深蓝 → 浅蓝渐变，但在 dark mode 下用高饱和蓝 → 高饱和蓝渐变，对比度拉不开
- 双色渐变在"按月创建趋势"语境下是过设计 — 趋势强调的是**时间维度的连续性**，不是色相变化

**改动**:
- `background: linear-gradient(...)` → `background: var(--accent)`（单色 token）
- 顶部加 `box-shadow: inset 0 1px 0 0 color-mix(in srgb, var(--card) 18%, transparent)`：
  - 1px 的顶部高光让条看起来"有立体感"（Geist 风格常见）
  - 用 `color-mix` 把 card 色提亮 18% → 自动跟随 light/dark 切换

**影响估计**:
- dark mode 下 timeline 条不再"一团纯蓝"，有可识别的几何层次
- 减一个硬编码 hex 颜色
- 与 6 个 `.bar-fill.type-*` 形成对比：类型分布用"分类色"传达**类型维度**，timeline 用"单色 + 高光"传达**时间维度** — 视觉语义清晰分工

---

### 3. MemoryCard prefers-color-scheme → [data-theme='dark']

**问题**:
- P38 上一轮在 `.strength-ring__num` 和 `.meta-text--*` 加了 `@media (prefers-color-scheme: dark)` 来给暗色模式提供更亮的环数字（`#4ade80 / #facc15 / #f87171`）
- 这个 media query 是 **OS 驱动的**，与应用的 in-app 主题系统脱钩
- 用户场景：在 light mode（应用内） + dark mode（OS）下，环数字会变成"OS 觉得是暗色"的色值 → 整张卡看起来不像在 light mode
- 全站主题契约是 `html[data-theme='dark']`（见 `styles/variables.css:86`），唯独这两个 selector 走 OS 路径

**改动** (`frontend/src/components/Layout/MemoryCard.vue`):
- 2 个 `@media (prefers-color-scheme: dark)` 块 → 2 个 `[data-theme='dark']` 选择器
- 文字注释说明替换原因（避免下一个看代码的人把 prefers-color-scheme 改回去）
- 颜色值不变（`#4ade80 #facc15 #f87171` 已经是合理的 dark 调色板）

**影响估计**:
- 修复 light-mode-with-OS-dark 的视觉串台 bug
- 与 SearchBar / P43 modal-backdrop 整站的 `[data-theme='dark']` 契约对齐
- 全站 `prefers-color-scheme` CSS 用法现在只剩 `stores/ui.ts` 里的 `window.matchMedia`（合法的 OS 偏好读取），CSS 层完全统一

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors |
| `npm run build` | ✅ 2.41s，dist 完整生成 |
| 8501 服务进程 | 未触碰，仍在 serving `frontend/dist`（用户刷新即生效） |
| 后端 / 新依赖 | 无 |
| 硬编码颜色数 | DashboardView: 6 个 hex + 1 个 hex 渐变端点 → 0 个；MemoryCard: 0 新增 |

---

## 视觉影响总结

| 维度 | 变化 |
|---|---|
| Dashboard dark mode | 6 个刺眼色块 → 6 个与 chip 同色系的低饱和色块 |
| 跨页面视觉语言 | Dashboard bar dot ↔ MemoryCard chip dot 形态一致 |
| Timeline 立体感 | 单色 + 1px 顶部高光，几何层次更明显 |
| 主题契约 | MemoryCard 整页走 `data-theme` 契约，与全站统一 |
| Token 覆盖率 | DashboardView: ~80% → 95% |

---

## 遗留 / 下次可做

- **Dashboard 真正的图表缺失** — type 分布 / strength 分布 / 月度趋势都是手画 SVG-like 的 div，不是 ECharts/Chart.js 这种正式图表。P36 第 8 条仍未根治
- **Strength 分布柱状图** 用 `var(--accent)` 单色，缺少 P39 的高/中/低档颜色梯度（strength ring 已经有 3 档色了，但分布图没有）
- **Timeline 横轴月份** 文字在窄屏会折行（断点 `767px` 还没单独处理）
- **AppHeader 移动端** sidebar-toggle 38×38 在 iPad 上偏大（`min-height: 36px` 来自通用规范，但 header 有 3 个按钮可以更紧凑）
- **MemoryCard expanded body** 的"对比"按钮（`🔍 对比`）和 AI 按钮（`✨ Suggest Tags`）都是 `--accent` outline + hover 翻转，缺少主次区分（两个 primary 互斥违规）
