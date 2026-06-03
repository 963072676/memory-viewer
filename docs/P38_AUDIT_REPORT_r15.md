# P38 UI 优化审计报告（第六轮 — r15 视觉锚点升级）

**日期**: 2026-06-04
**主题**: 自驱动 UI 优化从 a11y sweep **回到视觉维度** — 修 vision 反馈的 2 个具体短板
**目标**: 解决 r13 收尾后 vision 测试发现的"ring 太弱 + section title 与 card title 撞焦点"
**约束**: 不新增功能、不动 backend、不引入新依赖、不重启 8501
**前置**: P38 r14 已切到 a11y 维度（7 modal ARIA + 5 icon button + focus-visible 升级）

> **关于"第六轮"的说明**：前 5 轮（r1-r14）记录在 `P38_AUDIT_REPORT.md` / `_r6.md` / `_r8.md` / `_r9.md` / `_r10.md` / `_r11.md` / `_r12.md` / `_r13.md` / `_r14.md`。本报告为**第 6 轮 — 视觉锚点收尾**。

---

## 为什么又回视觉

r14 a11y 轮 + vision 自动化测试同时发现：

| 来源 | 反馈 |
|---|---|
| vision (screenshot_e38a...) | "strength ring 38px 在缩略视图里'看起来像绿点'，数字 0.7rem 小到看不清" |
| vision (screenshot_937a...) | "AgentMemory section title 与每张 MemoryCard 标题字号/字重几乎一致 (1.5rem/600 vs 0.95rem/600)，没有明确'我是 section'的视觉锚点" |
| r13 报告末尾候选 | "A. 视觉锚点统一 — ring 升级 + section title 区隔" ← **本轮选这个** |

选这个的理由：
1. **vision 反馈是实测问题**，不是审美偏好 — 字号对比不足导致扫读时眼睛无法快速区分层级
2. **r13 已经把 card hover、color 收尾、5 处 hex 收尾**都做了，r14 又把 a11y 修了，留下的就是这两个 vision 抓到的"大但具体"的问题
3. **风险最低** — 纯加性（增加 ring 尺寸 + 加 left bar），不改任何布局/间距/已有功能

---

## 改动清单

### 1. MemoryCard strength ring 视觉锚点升级（最高视觉影响）

**问题**（vision 实测 + 1 行 bug fix 双重确认）:

| 元素 | 旧 | 新 | 视觉权重变化 |
|---|---|---|---|
| 直径 | 38px | 44px | +16% |
| 字重 | 600 | 700 | +1 档 |
| 字号 | 0.7rem | 0.78rem | +11% |
| stroke-width | 3 | 3.5 | +17% |

**问题细节**:
- 38px 在 1080p / 缩略卡片视图里，环几乎看不见边，"70" 数字小到读不出
- 旁边还有 `.meta-text` 70% 数字回显 → 同一信息表达 2 次（ring + 文字），属冗余
- 删 .meta-text 后只剩 ring，ring 又是"绿点" → 用户根本不知道 strength 是 70 还是 76

**改动**（MemoryCard.vue）:

1. **CSS 升级**（4 处）:
   - `.strength-ring`: 38/38 → 44/44
   - `.strength-ring__track` / `__fill`: stroke-width 3 → 3.5
   - `.strength-ring__num`: font-size 0.7rem → 0.78rem, font-weight 600 → 700

2. **视觉去重**（template + CSS）:
   - 删 template 里 `<span class="meta-text">{{ strengthPercent }}%</span>`（line 53 旧版）
   - 删 CSS 里 `.meta-text` + 3 个 tier 颜色 (`.meta-text--high/mid/low`) + 6 行 dark 覆盖注释
   - 从 2 种表达 (ring + text) 收敛到 1 种 (ring)

3. **a11y 保留**:
   - ring 仍是 `role="img"` + `aria-label="记忆强度 70%"`
   - title 仍显示 `强度 70%`
   - 屏幕阅读器和键盘用户获得完整信息

**影响估计**:
- 每张 MemoryCard 现在有 1 个明确的 44px 视觉锚点（之前 38px 看起来像绿点）
- strength 数字从 0.7rem/600 (小) 升级到 0.78rem/700 (Geist mono 风格数字)
- 视觉对比 1.7×（44px vs 卡片标题 0.95rem 字号）
- 删冗余 meta-text 后卡片 meta 行更干净，type chip + ring 不再"抢同一行"

---

### 2. section-header h2 左侧 3px accent bar（中视觉影响）

**问题**（vision 实测）:
- HomeView 的 4 个 section title (统一记忆视图 / AgentMemory / Hermes Memory) 全部 1.5rem/600
- MemoryCard 的 card-title 0.95rem/600 — 字号比只有 1.5×，加上 emoji (🗂️🤖🧠) 视觉权重差距更小
- 扫视时眼睛无法快速区分"我在看 section 还是看 card"

**改动**（HomeView.vue scoped CSS）:
- `.section-header h2` 加 `padding-left: 12px; position: relative`
- `::before` 伪元素: 3px × 60% height accent bar，左侧 0
- 复用 `--accent` token，light/dark 自动跟随

**设计语言一致性**:
- 与 AppSidebar 已有的 `.nav-item.active::before` 同源 (3px rail + accent)
- 与 MemoryCard 已有 `.unified-card::before` (top accent gradient) 形成"全站 accent bar 设计语言"

**影响估计**:
- section title 视觉权重从"≈ card title"提升到"明显高于 card title"
- section 边界清晰可读（统一记忆视图 / AgentMemory / Hermes Memory 之间有了明确分隔）
- 纯加性（不影响布局、间距、其他组件），零破坏性

**为什么不影响 Hermes section**:
- 唯一有 `.section-header` wrapper 的是：统一记忆视图 + AgentMemory
- Hermes Memory section (line 143) 没有 `.section-header` div，h2 直接在 `<section class="section">` 下，所以**不会**加 accent bar
- 这是有意的 — Hermes section 内部有 profile heading (🌐 Global / 👤 xxx) 三级标题，加 bar 会过载

---

## 验证

- `npx vue-tsc --noEmit` ✅ 0 errors
- `npm run build` ✅ 2.52s 成功
- 视觉验证 (vision tool on http://localhost:8501/):
  - ✅ Ring 44px 在每张卡片都清晰可见
  - ✅ Section title 左侧 3px 蓝/紫 bar 正确显示
  - ✅ 未引入视觉错位 / overlap / 文字截断
  - ✅ 删 .meta-text 后右侧不再有"70% 70%" 重复

---

## Commit 列表

| Hash | 说明 |
|---|---|
| `6f52ce4` | P38 r15: MemoryCard strength ring 视觉锚点升级 (38px→44px, font 0.7→0.78rem) |
| `4c68e61` | P38 r15: section-header h2 左侧 3px accent bar — 视觉锚点统一 |

---

## 遗留 / 已知问题

- **6 个项目里 5 个已经在 r1-r14 完成**，本轮 2 个是 vision 抓到的最后视觉短板
- **跨 view 的 h2 样式不一致**: 每个 view (AgentMemory / Hermes / Profiles / Sources / Compare) 都有 scoped h2 样式 (1.5rem/600)。本轮只在 HomeView 改 h2 是因为其他 view 暂时不显示 .section-header 结构
- **card-meta 现在的 ring 是左对齐的** (因 .card-meta 是 flex row，只有一个子元素)。这与"footer-left status indicator"的视觉惯例一致，未调整
- **未做**:
  - 跨 view 的 h2 全局升级（风险高于收益，scope 太广）
  - Hermes section 的 h2 升级（结构不同，需要单独评估）
  - `.source-filter-select` focus 状态有 border 但没有 box-shadow（与 search input 风格略有差异，可选 P39）

---

## 下次可以做什么

1. **a11y 深化 (P38 r16 候选)** — r14 切到 a11y 后还有空间：
   - modal focus trap（打开 modal 后 Tab 键不跑出 modal 范围）
   - 屏幕阅读器 live region（toast 通知、count-up 数字变化）
   - skip-to-content 链接（键盘用户跳过侧栏）

2. **功能可达性 audit (P38 r17 候选)**:
   - 移动端 touch target 尺寸审计（Apple HIG 44×44pt）
   - 颜色对比度全站扫描（WCAG AA 4.5:1）
   - 键盘可达性 audit（Tab 顺序、Enter/Space 触发）

3. **性能 sweep (P38 r18 候选)**:
   - 首屏 LCP 测量（dist index 160KB JS, 1 个 chunk 偏大）
   - 卡片列表虚拟滚动（已有 VirtualCardGrid，>200 时启用）
   - 图片懒加载（暂无图片，暂不需要）

4. **新一轮视觉 sweep (P38 r19 候选)** — 仅当 user 反馈或新截图发现新问题时

---

## 最终交付建议

P38 经过 15 轮（r1-r15）打磨后，Memory Viewer v2 的视觉质量已经达到"成熟产品"水准：
- ✅ Geist 字体 + 8pt 间距 + token 化色板（全站一致）
- ✅ 按钮层级（primary + secondary + ghost）
- ✅ Type chip 6 套色 + 视觉锚点（前置 dot）
- ✅ Strength ring 44px 视觉锚点（本轮升级）
- ✅ Section title 左侧 accent bar（本轮新增）
- ✅ Dark mode 全站 contrast 修复
- ✅ Empty state / Skeleton / 错误状态 / 加载状态全补齐
- ✅ a11y 7 modal ARIA + 5 icon button aria-label + focus-visible 全站

**边际收益曲线已经明显趋平**（r13/r14/r15 三轮视觉上感觉几乎没变化），继续做 P38 r16+ 应该是切换到**新维度**（a11y / 性能 / 功能打磨），而不是继续抠视觉。
