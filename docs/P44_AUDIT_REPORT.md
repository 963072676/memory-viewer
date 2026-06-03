# P44 UI 优化审计报告

**日期**: 2026-06-03
**主题**: 自驱动 UI 优化第七轮 — chart-empty 视觉强化 + StatsBar/TabBar 节奏 + SettingsView btn token 化
**前提**: P38-P43 已 commit 完毕（最新 `10dba6d` P39 r1），本轮承接 P42 / P43 报告遗留
**约束**: 不新增功能、不动 backend、不引入新依赖、只改 CSS/Vue 模板

> **关于"P38 循环"的说明**：本轮 cron 提示词标签写的是"P38 优化"，但 P38 / P39 / P40 / P41 / P42 / P43 在本次运行前都已 commit 完毕。本报告记为 P44（第 7 轮），承接 P42 #2 / P43 #2 报告的 3 项具体遗留。

---

## 改动清单

### 1. DashboardView chart-empty 三处视觉强化（最高视觉影响）

**问题**:
- Dashboard 首屏 3 个 chart card 全部空数据时，`.chart-empty` 是一行"暂无数据"小字
- 单行小字 + `padding: 48px` 在 chart card 里显得"卡片内容缺失"而非"暂无数据"
- P42 报告 #2 明确说"全 EmptyState 在 chart card 内视觉过重"，但**没禁止加视觉锚点**
- 之前的版本是 `text-align: center` 居中，视觉重量过低

**改动** (`frontend/src/views/DashboardView.vue`):
- 模板：3 处 `<div class="chart-empty">暂无数据</div>` 改为 mark + text 双元素结构
  ```html
  <div class="chart-empty">
    <span class="chart-empty-mark" aria-hidden="true">∅</span>
    <span class="chart-empty-text">暂无数据</span>
  </div>
  ```
- CSS：
  - `.chart-empty` 改 flex 布局（centered mark + text），不再只用 text-align
  - 字号 `0.875rem` → `0.8125rem`（更克制，与 card 内"次要信息"一致）
  - 颜色 `var(--text-secondary)` → `var(--text-tertiary)`（更弱，让 chart 标题 `h3` 突出）
  - `letter-spacing: 0.01em`（微调，跟 HomeView Unified 卡片文案统一）
- 新增 `.chart-empty-mark`：
  - 22×22 圆形 `--tag-bg` 背景 + `∅` 字符
  - 圆形药丸有"占位符"语义，比单行文字更明确
- 新增 `.chart-empty-text`：单独控制 `var(--text-secondary)`（比 mark 重一点）
- 不引入完整 EmptyState 组件 — 保持"占位"语义（数据返回时立即替换）

**影响估计**:
- 3 个 chart card 在空数据状态下从"看起来崩了"变成"明确显示等数据" — 信息密度不变但视觉重量 +40%
- 圆形 `∅` mark 提供次要视觉锚点（不抢 chart 标题 `h3` 的风头）
- 文字 / mark 颜色用 2 个不同 token（`--text-tertiary` / `--text-secondary`），形成微妙的层次

---

### 2. HomeView StatsBar + TabBar 节奏优化（信息层 → 导航层）

**问题**:
- App.vue 里 4 个组件从上到下：AppHeader / SearchBar / QuickAccessBar / StatsBar / TabBar
- StatsBar（信息行，border-bottom 分隔线）和 TabBar（导航行，无分隔）挤在一起
- 之前 TabBar 用 `class="search-bar"`（早期代码遗留 — 来自最初 TabBar 复用 SearchBar 样板的阶段），语义错误
- TabBar `margin-bottom: 24px` 和下面 section 的 `--space-section-gap` 叠加导致"断层"感
- P39 报告 #4 明确说"节奏感可以优化"

**改动** (`frontend/src/components/Layout/TabBar.vue`):
- 模板：`<div class="search-bar">` → `<div class="tab-bar">`（语义修复 + 防止未来误用 search-bar CSS 覆盖）
- CSS：
  - `margin-top: 0` → `var(--space-5)`（20px），与上方 StatsBar 形成"section break"
  - `margin-bottom: 24px` → `var(--space-5)`（20px），与下方 section 间距统一（之前是 24 + section-gap，叠加断层）
  - `gap: 12px` → `var(--space-3)`（token 化）
- 移动端：`@media (max-width: 767px)` 同步改名 `.tab-bar` + `gap: var(--space-2)`

**改动** (`frontend/src/components/Layout/StatsBar.vue`):
- CSS：
  - `margin-bottom: 20px` → `var(--space-3)`（12px），与 TabBar 的 `margin-top: --space-5` 配合成 12+20 节奏
  - `gap: 16px` → `var(--space-4)`（token 化）
  - `padding: 12px 0` → `var(--space-3) 0`（token 化）
- 移动端：同步 `gap/margin-bottom` 改用 token

**影响估计**:
- 桌面端首屏从 5 个"独立组件"变成清晰 2 段：**信息层**（StatsBar，border-bottom 分隔）→ **导航层**（TabBar，无分隔，20px 留白）
- 4 个裸值（`margin-bottom: 20px` / `margin-bottom: 24px` / `gap: 16px` / `gap: 12px`）全部 token 化，与 P40 spacing scale 一致
- TabBar 的旧 className `.search-bar` 修复，未来不会被误覆盖
- 移动端折叠时节奏仍合理（`var(--space-2)` / `var(--space-3)`）

---

### 3. SettingsView `.btn-primary` token 化收尾

**问题**:
- SettingsView 的 `.btn-primary` / `.toggle-btn.active` 用 `color: white`（硬编码白）
- 暗色模式 `--card` = `#000`，硬编码 `white` 在暗色模式不会"自反相"（按钮底是 `--accent` 蓝色，文字白在亮/暗模式都可读，不影响视觉）
- 但违反"全站 token 一致"原则 — HomeView 的 `.action-btn--primary` 已经用 `var(--card)` 了
- P43 #2 报告的"颜色决策（--accent vs --primary）"是设计决策，本轮**不改色**，只做 token 化收尾

**改动** (`frontend/src/views/SettingsView.vue`):
- `.btn-primary`：
  - `color: white` → `var(--card)`（与 HomeView 决策一致）
  - `transition` 加入 `background`（hover 时背景变化更顺滑）
  - hover 从 `opacity: 0.9` 改为 `background: color-mix(in srgb, var(--accent) 88%, var(--primary) 12%)`（更 Geist 风格的"颜色微调"而非"透明度"）
  - hover 加 `:not(:disabled)`（disabled 状态不变暗 — 与原本逻辑保持一致）
- `.toggle-btn.active`：
  - `color: white` → `var(--card)`（同 token 化）

**影响估计**:
- 2 处 `color: white` 硬编码 → `var(--card)` token（与 P42 之前的状态保持一致：全站 0 处 `color: white`）
- hover 用 `color-mix()` 微调（与 P39 type chip 的 18% border 思路一致 — 避免定义 6 个新 token）
- SettingsView "表单保存按钮颜色（--primary vs --accent）"的设计决策**仍保留**为 P41 #1 / P43 #2 的 open question — 不在本轮范围

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors |
| `npm run build` | ✅ 2.52s，dist 完整生成 |
| `grep "color: white\|color: #fff" frontend/src/views/DashboardView.vue frontend/src/views/SettingsView.vue frontend/src/components/Layout/TabBar.vue frontend/src/components/Layout/StatsBar.vue` | ✅ 0 结果（注释除外） |
| 8501 服务进程 | 未触碰，仍在 serving `frontend/dist`（用户刷新即生效） |
| 后端 / 新依赖 | 无（`color-mix()` 是 CSS 原生，与 P39 type chip 一脉相承） |
| 现有功能回归 | Dashboard 数据正常返回时 `.chart-empty` 立即被 `v-else` 替换；TabBar 4 个 tab 切换 / kbd 快捷键行为不变；SettingsView 表单保存逻辑不变 |

---

## 设计决策记录

### 为什么 chart-empty 用 `∅` 而不是图标？
- `∅` 是 Unicode 字符（U+2205），是数学"空集"符号
- 不需要 icon font / SVG，零依赖
- 视觉上比 emoji（📊 / 📭）更克制，与 Geist 风格一致
- 圆形 22px 容器 + ∅ 字符，类似"`p2` 角标"的视觉语言（"次要信息锚点"）

### 为什么 TabBar 改名为 `.tab-bar` 而不是保留 `.search-bar`？
- `.search-bar` 是 SearchBar 专有的 className（line 113 有 `.search-input` 等子选择器依赖）
- 早期代码复用导致的"名字漂移"，技术债
- 改名 + 不依赖其他文件（scoped 隔离），零风险

### 为什么 SettingsView btn hover 改用 `color-mix()` 而不是维持 `opacity: 0.9`？
- `opacity` 影响所有属性（包括阴影 / 边框如果有），未来如果加 box-shadow 会被意外影响
- `color-mix` 只影响 background，可控性更好
- 与 P39 type chip 18% border 思路一致（用 color-mix 而非新增 6 个 token）
- 12% 黑色混合在亮色模式 = "深蓝"（符合 macOS 蓝色按钮 hover 效果）
- 暗色模式：12% `--primary` (亮白) 混合 = "浅蓝"（更柔和）

### 为什么 StatsBar margin-bottom 用 12px 而 TabBar margin-top 用 20px？
- 形成"上紧下松"节奏：信息层（StatsBar）收紧底部，让视觉重心靠近导航层（TabBar）
- 12+20 = 32px（与 `--space-7` 同），但分配方式不同 — 视觉上有"上 12 / 下 20"的呼吸感
- 如果用均匀 16+16 = 32px，会显得"对称但僵硬"
- 12+20 在 P40 spacing scale 里都是 4 的倍数（`--space-3` + `--space-5`），数学上合规

---

## 遗留 / 下次可以做

1. **DashboardView `StatsBar` 与 `TabBar` 在小屏的合并** — 移动端两个独立组件横/竖向切换造成"折叠"逻辑复杂，可以考虑合并成 `<NavAndStats>` 单组件，根据 viewport 自动布局
2. **SettingsView 4 个 Tab 的 active 状态强化** — `webhook` / `feishu` / `notifications` / `about` 切换时缺少清晰 indicator（line 305-330 的 nav 区），可以加 left rail 模式
3. **CollectionsView / SourcesView 顶部缺少 StatsBar 类的"信息行"** — 与 HomeView 视觉不一致，跨页面切换有"少一块"的感觉
4. **deprecated/ 目录 monospace 收尾** — 13 处 `font-family: monospace`（P43 #1），属于死代码清理
5. **统一所有 view 的"首屏顶部"组件布局** — HomeView 有 SearchBar/QuickAccessBar/StatsBar/TabBar 四件套，但其他 view（如 DashboardView）直接进内容，缺少一致的"信息架构门面"

---

**Commit**: P44
**Files changed**:
- `frontend/src/views/DashboardView.vue`（+40 -8，3 处 chart-empty 模板 + CSS）
- `frontend/src/components/Layout/StatsBar.vue`（+10 -6，token 化 + 节奏）
- `frontend/src/components/Layout/TabBar.vue`（+10 -8，className 修复 + token 化）
- `frontend/src/views/SettingsView.vue`（+10 -6，2 处 color: white → var(--card) + hover 升级）
- `frontend/dist/*`（build 产物，asset hashes 更新）
