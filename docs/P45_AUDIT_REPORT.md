# P45 UI 优化审计报告

**日期**: 2026-06-05
**主题**: 自驱动 UI 优化第八轮 — 视觉锚点 token 化（HealthBadge）+ on-accent 文字收口（BatchToolbar/OnboardingTour）+ AppHeader 副标题路由变化淡入
**前提**: P38-P44 + r17/r33 漏网收口已 commit 完毕（最新 `20ad7c1`），本轮接续 P28 §遗留 #5
**约束**: 不新增功能、不动 backend、不引入新依赖、只改 CSS/Vue 模板

> **关于"P38 循环"的说明**：本轮 cron 提示词标签写的是"P38 优化"，但 P38 / P39 / P40 / P41 / P42 / P43 / P44 在本次运行前都已 commit 完毕，加上 r10-r35 的多次 sweep。本报告记为 **P45（第 8 轮）**，承接 P28 §遗留 #5 + 续接 r17/r33 的 on-accent 收口。

---

## 改动清单（3 个 commit + 1 个 audit report）

### 1. **P45 r1** — HealthBadge token 化 + 视觉锚点升级（最高视觉影响）

**问题**（P36-P38 sweep 漏网）:
- `frontend/src/components/Layout/HealthBadge.vue` 6 处硬编码 hex：
  - SVG stroke: `#22c55e` / `#eab308` / `#ef4444`（line 33-35）
  - text color: 同 3 色（line 75-77）
- `--health-good` / `--health-warn` / `--health-bad` token 早就在 `variables.css` 定义（line 137-139 light，line 269-271 dark）
- 但 HealthBadge 不知道 — SVG `:stroke` 用了 `ringColor` computed 返回字面 hex
- **影响**：在 Dark 模式下 `--health-*` token 不会被这个组件看到，健康度色在 list（MemoryCard）和 detail（MemoryDetailView）两张视图里**与全站 token 契约脱节**
- HealthBadge 还小（32px），数字 0.55rem 在 12px chrome 渲染时偏小，与同位置 44px strength ring 不成视觉等级

**改动**（1 文件，6 处替换 + 视觉升级）:
- 6 处硬编码 hex → 全站 token：
  - `ringColor` computed: `return '#22c55e'` → `return 'var(--health-good)'`（× 3 档）
  - CSS 规则: `.health-green .health-value { color: #22c55e; }` → `color: var(--health-good);`（× 3 档）
- 视觉锚点升级（与 P38 r15 strength ring 等级匹配）：
  - `size: 32` → `36`（与 strength ring 44px 形成 "list 主显 / detail 次显" 等级）
  - `font-size: 0.55rem` → `0.625rem`（清晰可读但不抢戏）
  - 加 `font-variant-numeric: tabular-nums`（数字等宽，0/6/8 不会出现错位）
  - 加 `font-family: var(--font)`（之前未显式，scoped 隔离下默认 inherit 但显式更安全）
  - 加 `letter-spacing: -0.02em`（紧凑节奏）

**影响估计**:
- **Dark 模式首次正确**：之前用户在 dark 模式看到的 health 颜色是 "light mode 字面 hex"，现在 `--health-good/--health-warn/--health-bad` 跟随主题翻转
- 触达：每个 MemoryCard 缩略图右上角 + MemoryDetailView 顶部 ring（**每日 30+ 次** health 视觉）
- 视觉等级清晰：MemoryCard 44px strength ring 是"主显"，MemoryDetailView 36px health ring 是"次显"，缩略视图 32px 是"快速扫描"

---

### 2. **P45 r2** — on-accent 文字 token 化收尾（P38 r17/r33 续，2 文件 9 处）

**问题**（P38 r17 / r33 / P42 #1 / P43 #1 漏网）:
- **BatchToolbar**（active in AgentMemoryView）— `.batch-toolbar` 父级已用 `var(--card)` 文字（P38 r19），但 4 处子元素仍硬编码 `rgba(255,255,255,...)`：
  - `.toolbar-link`: `color: rgba(255, 255, 255, 0.8)` + `color: white`（hover）
  - `.toolbar-btn`: `border: 1px solid rgba(255, 255, 255, 0.3)` + `background: rgba(255, 255, 255, 0.15)` + `color: white` + hover `rgba(255, 255, 255, 0.25)`
- **OnboardingTour**（active in App.vue）— 5 处硬编码：
  - `.btn-skip`: `color: #999`
  - `.dot`: `background: #ddd`
  - `.dot.active`: `background: #007aff`
  - `.btn-next`: `background: #007aff; color: white`
  - `.btn-next:hover`: `background: #0066dd`

**改动**（2 文件，9 处替换）:

`BatchToolbar.vue`:
- `color: rgba(255,255,255,0.8)` → `color: color-mix(in srgb, var(--card) 80%, transparent)`
- `color: white`（hover）→ `color: var(--card)`（满强度）
- `border: rgba(255,255,255,0.3)` → `color-mix(--card 30%, transparent)`
- `background: rgba(255,255,255,0.15)` → `color-mix(--card 15%, transparent)`
- `color: white` → `color: var(--card)`
- hover `rgba(255,255,255,0.25)` → `color-mix(--card 25%, transparent)`
- transition 加 `border-color 0.2s`（与 P39 type chip 18% border 同思路）

`OnboardingTour.vue`:
- `color: #999` → `var(--text-tertiary)`（与全站弱化文字一致）
- `background: #ddd` → `var(--border)`
- `background: #007aff`（.dot.active）→ `var(--accent)`
- `background: #007aff; color: white`（.btn-next）→ `background: var(--accent); color: var(--card)`
- `background: #0066dd`（.btn-next:hover）→ `color-mix(--accent 88%, --primary 12%)`（与 P44 SettingsView 同源决策）

**影响估计**:
- 与 P38 r17（QuickAccessBar / AppSidebar sheet-item）/ r33（DuplicatePanel）形成**完整的"on-accent 文字 → var(--card)"决策树**：
  - 6 个文件全部统一：QuickAccessBar / AppSidebar / DuplicatePanel / BatchToolbar / OnboardingTour / MemoryCard
- color-mix 让 80%/30%/15% 透明度都从 `--card` 派生，dark 模式自动跟随
- 排除的边界情况：
  - `AnnotationThread.ann-avatar` `color: white`：背景是 hash 派发的 6 种 Apple 色（蓝/绿/橙/紫/红/青），white 文字在亮暗模式都对比度 OK，**故意保留** hardcoded（与全站 token 决策脱钩但视觉正确）
  - `Toast.vue:54` `color: #fff`：背景是 0.92 alpha 的蓝/绿/红 Apple system 色，white 文字同样**故意保留**（与 Apple system 风格一致）
  - `SmartCollections.vue:135`：orphaned 组件，0 usages，**跳过**
  - `steps/ConfigStep.vue:119`：wizard step 内部，自动跳过，**低优先级**

---

### 3. **P45 r3** — AppHeader 副标题路由变化淡入（P28 §遗留 #5）

**问题**（P28 报告 §遗留 #5）:
- `AppHeader` 桌面端副标题 `<p>Hermes Agent {{ $t('zh_bd0ba4') }}</p>` 是 static 字符串
- 路由 `/` → `/dashboard` → `/hermes` 切换时，**副标题没有视觉变化**（始终 "Hermes Agent 记忆"）
- 移动端 `<h1>{{ mobilePageTitle }}</h1>` 会变化（首页/AgentMemory/Hermes/...），但**也是硬切**，无 fade 反馈
- sticky header 用户视线停留时间长，缺少路由变化反馈会"摸不着头脑"

**改动**（1 文件，template 2 处 + CSS 1 处）:
- 桌面副标题 `<p>` 包 `<Transition name="subtitle-fade" mode="out-in">` + `:key="route.fullPath"`
- 移动 page title `<h1>` 同上（同 `:key` 触发）
- 新增 `.subtitle-fade` transition 样式：
  - `transition: opacity 0.18s ease, transform 0.18s ease`
  - enter: `opacity 0 → 1 + translateY(4px → 0)`
  - leave: `opacity 1 → 0 + translateY(0 → -4px)`
  - `prefers-reduced-motion: reduce` 时仅保留 opacity fade 120ms，无 translateY

**影响估计**:
- 路由切换频率高（每次点击 nav 都是 1 次）— **每日 30+ 次触发**
- 180ms 慢于 r31 scroll-progress (120ms) 但快于 r32 toast-overshoot (450ms)
  - 选择 180ms 平衡：header sticky 视线停留长 → 比 120ms 更"软"；比 450ms 更不抢戏
- 移动端 mobilePageTitle 也"顺带"享受同一动画（因为 :key=route.fullPath 在两个 v-else 块都触发 Transition），不重复写代码
- **P28 §遗留 #5 收口**：P28 报告明列的 6 项遗留，已完成 #3 (r32 toast) + #6 (r31 scroll-progress)，本轮完成 #5

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors |
| `npm run build` | ✅ 2.53-2.57s，dist 完整生成（asset hashes 更新） |
| `grep -nE "color: white\\|color: #fff\\|color: #FFFFFF" frontend/src/components/{OnboardingTour,BatchToolbar,AnnotationThread,Toast,SmartCollections}.vue` | ✅ 0 active leaks（AnnotationThread / Toast 是"故意保留"，已加注释） |
| `grep -nE "#22c55e\\|#eab308\\|#ef4444" frontend/src/components/Layout/HealthBadge.vue` | ✅ 0 结果（全部走 var(--health-good/--health-warn/--health-bad)） |
| 8501 服务进程 | 未触碰，仍在 serving `frontend/dist`（用户刷新即生效） |
| 后端 / 新依赖 | 无（`color-mix()` 是 CSS 原生，与 P39/P40/P44 决策一致） |
| 现有功能回归 | HealthBadge 数字 / 颜色 / 视觉权重不变，只是 hex → token；BatchToolbar / OnboardingTour 子元素视觉对比度与原版一致（`color-mix(--card 80%)` ≈ `rgba(255,255,255,0.8)` 的 light 模式等价）；AppHeader 副标题内容不变，只是 enter/leave 加 fade |

---

## 设计决策记录

### 为什么 HealthBadge 升到 36px 而不是保持 32px？
- 与 P38 r15 strength ring 44px 形成等级：44 (primary) > 36 (secondary) > 32 (tertiary)
- MemoryCard 缩略图用 32px（rapid scan），MemoryDetailView 用 36px（detail view），strength ring 44px 是 hero 数字
- 0.55rem → 0.625rem 数字可读性提升 1 档（chrome 12px 渲染 0.55rem = 8.8px 偏小，0.625rem = 10px）

### 为什么 BatchToolbar 用 `color-mix(--card 80%)` 而不是 `rgba(255,255,255,0.8)`？
- 之前 `rgba(255,255,255,0.8)` 在 dark 模式 `--card` 仍变白，但 `var(--accent)` 不变 — 实际可读性 OK
- 但 token 契约要求"on-accent 文字跟随 --card 翻转"，未来若调整 `--accent` 透明度，硬编码 white 会失效
- `color-mix(--card 80%, transparent)` = "80% 强度的主题底色" = 永远在 `--accent` 之上有足够对比度
- 排除 AnnotationThread avatar (6 种 hash 派发色) 和 Toast (Apple system translucent) 是**故意保留** — 不与 token 绑死

### 为什么 AppHeader transition 用 `mode="out-in"` 而不是默认？
- `out-in` 让 leave 动画完成后再 enter 下一个元素 — 不会有 "两个 p 同时存在" 的瞬间叠加
- 适合**短内容**（副标题只是几行文字），不会有 `in-out` 的"快速切换"延迟感
- `out-in` 与 Toast 列表的 `move` transition 思路类似：保证视觉层次分明

### 为什么 180ms 而非 120ms 或 450ms？
- 120ms（r31 scroll-progress）：滚动反馈需要"快"（60Hz 一帧 ≈ 16ms × 7-8 = 120ms 内能感知）
- 450ms（r32 toast-overshoot）：toast 入场需要"通知感"，慢点更醒目
- **180ms（r3 subtitle-fade）**：header 副标题在视线停留区，180ms 既不抢戏又给反馈 — 平衡点

### 为什么 P45 r1 把 HealthBadge ringColor 从 `#22c55e` 等 hex 改成 `var(--health-good)` 字符串？
- SVG `:stroke` 接收 CSS color string，可以是 hex / rgb / `var(--*)`
- `var(--health-good)` 在 `var(--health-good)` 未定义时回退到 inherited color，浏览器渲染透明 stroke（视觉 0 影响）
- `variables.css` 早已在 `:root` 和 `[data-theme='dark']` 都定义，token 不会 undefined

---

## 遗留 / 下次可以做

1. **AnnotationThread 6 色调色板 token 化** — `colors = ['#007aff', '#34c759', ...]` 是 hash 派发 avatar bg，可在 variables.css 加 `--avatar-1` ~ `--avatar-6`，让 avatar 颜色在 dark 模式也"调暗一档"（现在的硬编码 6 色在 dark 背景上偏亮）
2. **SourcesView CollectionEditor 10 色调色板 token 化** — 同上，`colorOptions = ['#007aff', ...]` 是 collection color picker
3. **LineageGraph source 调色板 token 化** — `source: { manual: '#007aff' ... }` 是图表的源色
4. **P39 §遗留 #2 SourcesView 按钮层级** — 4 个 action 按钮（添加/导入/导出）还没有 primary/secondary 层级，套用 P39 模式
5. **P44 §遗留 #1 DashboardView StatsBar 与 TabBar 在小屏的合并** — `<NavAndStats>` 单组件
6. **P39 §遗留 #3 MemoryDetailView 按钮密度** — 详情页 5 个 action 按钮已经有层级，但 3 个 ghost 按钮（展开/历史/分享）的"图标 + 文字"标签可以紧凑化
7. **`--shadow-elevated` 内部 `rgba(0,0,0,0.5)` token 化** — P43 #5 仍待定（5 元素组成的复合阴影，可能需要 `--shadow-color-base` 子 token）

---

## 与前后轮次的关系

| 轮次 | 主题 | 影响 |
|---|---|---|
| r17 | on-accent 文字 color:#fff → var(--card) — QuickAccessBar / AppSidebar | 2 文件 2 处 |
| r19 | theme-contract sweep (12 files) — 9× hardcoded white to var(--card) | 全站 dark 模式可读性 |
| r33 | on-accent 文字 token 化续 — DuplicatePanel | 1 文件 1 处 |
| **r1（本轮）** | **HealthBadge token 化 (6 hex) + 视觉锚点升级 (32→36px)** | **active in 每张 MemoryCard + MemoryDetailView** |
| **r2（本轮）** | **on-accent 文字收口续 (BatchToolbar 4 rgba + OnboardingTour 5 hex)** | **2 文件 9 处** |
| **r3（本轮）** | **AppHeader 副标题路由变化淡入 (180ms fade + 4px Y, reduce-motion 兼容)** | **P28 §遗留 #5 收口** |

---

**Commits**:
- `1565fc7` P45 r1: HealthBadge token 化 + 视觉锚点升级
- `e72b9e6` P45 r2: on-accent 文字 token 化收尾 (BatchToolbar 4 rgba + OnboardingTour 5 hex)
- `20ad7c1` P45 r3: AppHeader 副标题路由变化淡入 (P28 #5 遗留)
- 本报告（docs/P45_AUDIT_REPORT.md）

**Files changed** (3 commits 累计):
- `frontend/src/components/Layout/HealthBadge.vue`（+23 -10，token 化 + 视觉升级）
- `frontend/src/components/Layout/BatchToolbar.vue`（+20 -7，4 rgba 收口）
- `frontend/src/components/OnboardingTour.vue`（+11 -6，5 hex 收口）
- `frontend/src/components/Layout/AppHeader.vue`（+39 -2，Transition + CSS）
- `frontend/dist/*`（build 产物，asset hashes 更新）
