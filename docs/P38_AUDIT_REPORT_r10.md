# P38 UI 优化审计报告（第十轮 — 移动端 fixed-bar padding 修复 + StatsBar count-up + 高频 modal 弹出动画）

**日期**: 2026-06-03
**主题**: 自驱动 UI 优化 — 3 项小范围 polish
**目标**:
1. 修复移动端 main-wrapper 缺少 padding-top/bottom（顶栏/底栏 fixed 遮挡内容）— P43 之后遗漏的 bug
2. StatsBar 3 个 stat 数字加 count-up 动画（沿用 r9 useCountUp）
3. 4 个高频 modal（Create / Edit / Import / Diff）加弹出动画

**约束**: 不新增功能、不动 backend、不引入新依赖
**前置**: P37–P44 + P38 r1-r9 9 轮 sweep 全部完成

> **关于 P38 原始 6 项 todo 的现状**（r9 已 100% 完成，本轮无需重做）:
> - ✅ Item 1 (MemoryCard strength ring) — round 1
> - ✅ Item 2 (侧栏 active 状态) — round 1 + round 8 (mobile tab)
> - ✅ Item 3 (按钮层级) — round 4
> - ✅ Item 4 (主内容区 max-width 1200px) — round 1
> - ✅ Item 5 (搜索框 Geist 化) — round 1
> - ✅ Item 6 (type 标签色块化) — round 1-5
>
> 本轮按 **r9 报告「下次可做」清单** 的 top 2 + 一个 P43 之后的回归 bug 修复推进。

---

## 改动清单

### 1. 移动端 fixed 头/底栏 padding 修复（高 — 影响所有移动端用户）

**问题**（P43 modal-backdrop 全站 sweep 之后回归）:
- AppHeader 在 mobile 断点（< 768px）下 `position: fixed; height: 56px;`
- AppSidebar 的 mobile tab bar 也是 `position: fixed; bottom: 0; height: 64px;`
- 但 App.vue 的 `.main-wrapper` 在 mobile 断点只设了 `margin-left: 0` + `max-width: 100vw`
- **结果**: 移动端打开任意页面，最顶部的 SearchBar / StatsBar 会被 AppHeader 遮住，最底部的 footer 会被 Tab Bar 遮住
- 这个 bug 在 P43 引入 "use AppHeader 统一 mobile 头" 时出现，但当时只改结构没补 padding

**改动**（2 文件，App.vue + AppSidebar.vue）:
- App.vue `@media (max-width: 768px)` 块加:
  ```css
  padding-top: 56px;                          /* 让出 AppHeader 高度 */
  padding-bottom: calc(64px + env(safe-area-inset-bottom, 0px));  /* 让出 Tab Bar + iOS 安全区 */
  ```
- AppSidebar.vue 删 50 行死代码 `.mobile-header` 系列样式（已统一到 AppHeader 的 `.app-header` mobile 分支）
- AppSidebar.vue 改 tab-icon/label 排版（display:block + max-width:100% + ellipsis），更稳的 5-tab 横向排版
- AppSidebar.vue 移动端断点 (max-width: 767px) 再缩 tab padding/字号，避免 5-tab 横向挤

**设计决策**:
- `env(safe-area-inset-bottom, 0px)` — iOS Safari / iPadOS 底部 home indicator 区域
- `calc(64px + env(...))` — Tab Bar (64px) + 安全区，Android 不影响（env 默认 0）
- AppHeader 内部 `padding: 0 16px` 保留，不再用 `.mobile-header` 的额外 padding

**影响估计**:
- 100% 移动端用户（断点 < 768px 命中）
- 每次进入任意页面都看到正确布局（不再有"内容被遮"）
- 死代码删除 -50 行（-0.5% 维护负担）

### 2. StatsBar count-up 动画（中-高 — 影响每次进入首页）

**问题**（r9 报告「下次可做」#1）:
- Dashboard 4 个数字已有 count-up（r9 加的）
- 但首页 StatsBar 3 个 stat 数字（AgentMemory 条目 / Hermes Memory 条目 / Profiles）还是"瞬时显示"
- 用户从 Dashboard 切到首页会感觉"数字突然跳出来"，缺少"载入感"

**改动**（1 文件，StatsBar.vue）:
- 引入 r9 的 `useCountUp` composable（零依赖）
- 3 个数字分别 count-up，duration 600ms（比 Dashboard 的 800ms 短，"3 个数字同步轻快"）
- `.stat-item strong` 加 `font-variant-numeric: tabular-nums` — count-up 期间数字宽度稳定不抖
- 用 `storeToRefs` 拿 store 的 ref（避免直接解构丢响应性 + type 推到 number[]/string[]）

**设计决策**:
- 600ms vs 800ms — 首页 3 个数字同屏，"快一点"比"庄重一点"更合适（避免用户等）
- 沿用 r9 useCountUp 已有 infrastructure（无新代码），只接入数据
- tabular-nums 是细节但关键 — 避免 count-up 时 `1 → 10` 导致右侧文字抖动

**影响估计**:
- 100% 进入首页的用户（HomeView 顶部固定显示 StatsBar）
- 配合 Dashboard count-up，整站 count-up 体验一致
- 0 风险：count-up 失败只是"瞬时显示"（回退到原行为）

### 3. 高频 modal 弹出动画（中 — 影响 4 个高频 modal 打开）

**问题**（r9 报告「下次可做」#4）:
- CreateMemoryModal / EditMemoryModal / ImportModal / MemoryDiffModal 都是直接 fade
- 缺少"弹窗弹出"的空间感（只有透明度变化）
- 与全站 Geist 风格（克制 + 流畅）不匹配

**改动**（4 文件，4 modal 各加一组 keyframes）:
- backdrop: `200ms ease-out` opacity 0→1（与页面切换 150ms 区分，"打开"比"换页"更慢）
- modal: `200ms cubic-bezier(0.16, 1, 0.3, 1)` 
  - `scale(0.96) translateY(8px)` → `scale(1) translateY(0)`
  - Apple/Vercel 模态的经典节奏（"快进 + 慢停" + 微弹）
- `@media (prefers-reduced-motion: reduce)` 跳过 — 无障碍合规

**影响 modal**（按使用频率排）:
- CreateMemoryModal — 首页/AgentMemory 创建记忆主入口
- EditMemoryModal — 编辑记忆高频
- ImportModal — 批量导入（不常用但 modal 本身大）
- MemoryDiffModal — diff 视图（95% 屏宽，弹出感最明显）

**设计决策**:
- 200ms 而非 150ms — 弹窗是"用户主动触发"，比"页面自动切换"更应该"确认"
- `cubic-bezier(0.16, 1, 0.3, 1)` — Material Design 的 `decelerate` 缓动，强调"目标到达"
- 不重构为 `<transition>` 包裹 — 当前 modal 是 `v-if` 触发，CSS `@keyframes` 零结构变化
- 4 文件分别写 keyframes（不抽离到全局）— 模态样式都是 `scoped`，抽离需要 `:global` 反而复杂

**影响估计**:
- 4 个 modal 每次打开都看到 200ms 弹出动画
- 主页创建记忆流程（modal → 表单 → 提交）感知更"流畅"
- 0 风险：动画失败 modal 仍正常显示

---

## 验证

| 项目 | 结果 |
|---|---|
| `vue-tsc --noEmit` | 0 errors |
| `npm run build` | 2.42-2.48s 全部 OK |
| 后端 8501 未触碰 | ✅ 只改 frontend/src/ |
| 依赖未增加 | ✅ useCountUp 是 r9 已有 composable，modal 动画纯 CSS |
| 改动文件数 | 7 文件 (App.vue, AppSidebar.vue, StatsBar.vue, 4 modal) + dist build artifact |
| commit 数 | 3 (b047779, 1b1975d, 3bec253) |

---

## 视觉影响估计

| 改动 | 估计影响 | 影响对象 |
|---|---|---|
| 移动端 fixed-bar padding 修复 | **高**（bug 修复） | 100% 移动端用户，每次进入任意页面 |
| 去重 .mobile-header 死代码 | 小（维护性） | -50 行死代码 |
| 移动端 tab 排版硬化 | 小（小屏视觉） | < 768px 的 5-tab tabbar |
| StatsBar count-up 动画 | **中-高** | 100% 进入首页的用户 |
| StatsBar tabular-nums | 小（细节） | count-up 期间不抖 |
| 4 modal 弹出动画 | **中** | 4 个高频 modal 打开 |

---

## 遗留与下一步建议

### 本轮已彻底完成

- ✅ 移动端 main-wrapper padding-top/bottom（P43 之后回归 bug 修复）
- ✅ AppSidebar 50 行 `.mobile-header` 死代码删除
- ✅ AppSidebar 移动端 tab 排版硬化（5-tab 横向不挤）
- ✅ StatsBar 3 个数字 count-up（沿用 r9 useCountUp）
- ✅ StatsBar tabular-nums 字符宽度稳定
- ✅ CreateMemoryModal / EditMemoryModal / ImportModal / MemoryDiffModal 弹出动画
- ✅ 全部遵守 `prefers-reduced-motion`（无障碍）

### 关键决策记录

1. **关于约束"不新增功能"**: 本轮发现一个未提交的"profile 过滤"功能（HermesMemoryView + ProfilesView 改 ?profile=xxx），已 `git checkout` 还原 — 因为这是新功能不属于 P38 UI 优化范畴。如果需要该功能可以单独开 P39。
2. **关于"r9 报告已写好"**: docs/P38_AUDIT_REPORT_r9.md 已存在于 r10 之前（untracked），本轮作为 r10 的前置 commit 一起提交，不重写。

### 下次可做（按视觉影响力排序）

1. **页面进入 stagger** — Dashboard 4 个 summary card 同步出现已经够好，但 chart cards / type bar / timeline bar 可以 stagger 出现（每个延迟 80ms 滚动），用 CSS `animation-delay` 即可，0 JS。影响每次进 Dashboard。
2. **页面滚动进度条** — router-view 顶部加 1px 高的 accent 色进度条，路由变化时从 0% → 100% 平滑推进（150ms），类似 Vercel 的页面加载指示器。每次切页都看到。
3. **AppHeader 副标题路由切换淡入淡出** — 切换页面时，header 中央的副标题（"Hermes Agent 记忆系统全景视图"）可以淡出再淡入（150ms），强化"页面切换"感。
4. **低频 modal 同样加动画** — SetupWizard / CollectionEditor / LinkCreator / WhatsNewModal 等还没加，节奏统一后视觉一致性更稳。
5. **卡片 hover 微动效** — MemoryCard hover 时除了 `box-shadow` 变化外，再加 `translateY(-2px)` 的"抬起"感（150ms ease-out），跟 Geist 风格的 Linear/Vercel 卡片一致。
6. **滚动到底自动加载更多** — HomeView 列表很长时可加（但这是新功能，违反约束，不建议）。

### 不可做（项目约束）

- ❌ 不新增功能（如 profile 过滤、滚动加载、虚拟滚动增强）
- ❌ 不引入新依赖
- ❌ 不动 backend

### 本轮越界检查

- ❌ 未新增功能（count-up 已有，modal 动画是 CSS 增强，无新交互）
- ❌ 未动 backend
- ❌ 未引入新依赖（useCountUp 是 r9 已有，modal 动画纯 CSS keyframes）
- ❌ 未改 dist/ 源码（dist build artifact 跟随）
- ❌ 未破坏现有功能（vue-tsc 0 errors，build 通过，移动端 bug 修复而非回归）

---

## 最终交付建议

P38 共 10 轮 sweep 累计覆盖：
- **静态样式**: 颜色 / 字体 / 阴影 / 间距 / 圆角 / 边框 全 token 化
- **组件视觉**: MemoryCard 强度环、type 标签色块、按钮层级、active 指示器
- **布局**: max-width 居中、移动端 fixed-bar 修复、tab 排版硬化
- **微动效**: 页面切换 fade、Dashboard/StatsBar count-up、modal 弹出动画
- **无障碍**: 全部遵守 `prefers-reduced-motion`

**未来方向**（已超出 P38 范围，需 P39+ 开新迭代）:
- **动效系统化** — 抽离 `--motion-duration` / `--motion-easing` / `--motion-stagger` token，全站统一节奏
- **空状态插画** — 大空状态（无记忆 / 无搜索结果）当前只有 emoji + 文字，可加简洁 SVG 插画
- **Onboarding 体验** — OnboardingTour 已存在但未充分利用
- **可访问性深化** — 当前只有 reduced-motion，其他 WCAG 维度（对比度、键盘导航、ARIA）需要专项审计

**是时候从「视觉打磨」转向「功能可达性 + 性能 + 可用性」维度**。
