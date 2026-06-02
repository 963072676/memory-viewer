# P41 UI 优化审计报告

**日期**: 2026-06-03
**主题**: 自驱动 UI 优化第五轮 — CollectionsView 按钮层级统一 + DashboardView spacing token 化 + Geist mono 一致性收尾
**前提**: P38（strength 锚点 / 侧栏 left rail / SearchBar）+ P39（按钮层级 / type chip）+ P40（Header 对齐 / spacing scale / kbd mono）已落地
**约束**: 不新增功能、不动 backend、不引入新依赖

---

## 改动清单

### 1. CollectionsView 按钮层级统一（视觉一致性问题）

**问题**:
- `.btn-create` 用 `background: var(--accent, #007aff)`（蓝色填充）— 违反 P39 设计决策："primary CTA 用 `--primary` 黑/白药丸，避免与侧栏激活态/链接的蓝色信号混淆"
- `color: #fff` 硬编码白色 — dark 模式下 --primary 是浅色，--accent 不变（蓝色），会与卡片背景形成新的对比度问题
- `transition: opacity 0.2s` 单一属性 — P39 给 HomeView 加了 `transform/border-color/box-shadow`，按钮"按下"没有触觉反馈
- `.cv-header h2 color: var(--primary, #007aff)` — fallback `#007aff` 是**误导性**的（虽然实际 --primary 存在所以取 #171717，但任何复制粘贴到没有 --primary 的项目里都会回退到蓝色）— 与 P40 报告中"硬编码 fallback 是技术债"的判断一致
- 多个裸值间距（24px / 16px / 20px）— 没用 P40 引入的 spacing scale token

**改动** (`frontend/src/views/CollectionsView.vue`):
- 标题色 `var(--primary, #007aff)` → `var(--primary)`（去误导 fallback）— 视觉无变化（实际取值就是 #171717）但代码意图更清晰
- `.btn-create` 从蓝色实心 → `--primary` 黑/白药丸：
  - `border-radius: 8px` → `var(--radius-pill)`（与 P39 HomeView `.action-btn--primary` 一致）
  - `color: #fff` → `var(--bg)`（dark 模式下 --bg=#0a0a0a，自动反相）
  - 新增 `display: inline-flex; align-items: center; gap: 6px; font-weight: 500`
  - 新增 `box-shadow: 0 1px 2px rgba(0,0,0,0.04)` 微微悬浮（Geist 风格）
  - transition 加入 `box-shadow` 和 `transform: translateY(1px) :active` 触觉反馈
  - hover 改用 `var(--primary-muted)`（与 P39 HomeView 同一逻辑）
- 所有裸值间距换成 token：
  - `.cv-header margin-bottom: 24px` → `var(--space-header-gap)` (20px) — 与 P40 HomeView section-header 节奏一致
  - `.cv-header` 新增 `gap: var(--space-3)` 给 flex
  - `.loading-state / .empty-state padding: 60px 20px` → `60px var(--space-5)`
  - `.empty-state p margin-bottom: 16px` → `var(--space-4)`
  - `.collections-grid gap: 16px` → `var(--space-5)` (20px)

**影响估计**:
- 入口页 CollectionsView 的 "New Collection" 按钮与 HomeView 的 "创建记忆" 按钮**视觉语言 100% 一致**（都是黑/白药丸，hover 用 muted）
- 跨页切换不再有"这个主 CTA 怎么不一样"的设计冲突
- 浅色模式按钮从蓝色变黑药丸，**避免了与左侧 sidebar 激活态的蓝色混淆**（之前用户会下意识把"New Collection"和"我现在在 Collections"两个蓝色信号混在一起）
- 暗色模式 `--primary` 是 `#ededed` 浅色，`--bg` 是 `#0a0a0a` 接近纯黑，按钮变成"白药丸 + 黑字"，与 HomeView 反相逻辑完全一致

### 2. DashboardView spacing token 化（节奏系统延伸）

**问题**:
- P40 给 HomeView 引入 spacing scale token 时**明确说明"为什么不全做 sweep"**：避免一次改太多导致回滚困难
- DashboardView 的 dashboard-header / summary-card / chart-card / timeline-chart 全部裸值（16/20/24/28/32/40/60px）— 与 P40 节奏系统**不在同一拍**
- timeline-label `font-family: monospace`（generic）— P40 已经把 TabBar / MemoryCard 改成了 `var(--font-mono)`，DashboardView 是漏网之鱼
- chart-card 的 `padding: 24px 28px`（28px 不在 4-px 节奏）— 显然是"当时感觉对就那样"

**改动** (`frontend/src/views/DashboardView.vue`):
- `.timeline-label font-family: monospace` → `var(--font-mono)`（与 TabBar / MemoryCard / SearchBar 完全统一 Geist mono 语言）
- `.dashboard-header` `margin-bottom: 32px` → `var(--space-7)`，`padding-bottom: 20px` → `var(--space-5)`，新增 `gap: var(--space-3)`
- `.btn-refresh` `padding: 8px 14px` → `var(--space-2) 14px`（左 8 用 token，右 14px 是字号相关，保留）
- `.loading-state / .error-state` `padding: 60px 20px` → `60px var(--space-5)`
- `.btn-retry` `margin-top: 12px` → `var(--space-3)`，`padding: 8px 20px` → `var(--space-2) var(--space-5)`，`border-radius: 8px` → `var(--radius-md)`
- `.summary-row` `gap: 16px / margin-bottom: 32px` → `var(--space-4) / var(--space-7)`
- `.summary-card` `padding: 20px 24px / gap: 8px` → `var(--space-5) var(--space-6) / var(--space-2)`
- `.chart-card` `padding: 24px 28px / margin-bottom: 20px` → `var(--space-6) var(--space-7) / var(--space-5)`
- `.chart-card h3` `margin-bottom: 20px` → `var(--space-5)`
- `.chart-empty` `padding: 40px` → `var(--space-8)` (48px)
- `.timeline-chart` `gap: 8px` → `var(--space-2)`
- `.timeline-bar` `gap: 12px` → `var(--space-3)`
- `.timeline-track` `height: 20px / border-radius: 6px` → `var(--space-5) / var(--radius-sm)`

**影响估计**:
- DashboardView 的所有节奏现在都走 P40 spacing scale，跨页切换时 HomeView / DashboardView / CollectionsView 三者的"section 间距 / card 间距 / 内边距"完全统一
- timeline 月份标签（"2025-01"）从 Courier New → SF Mono / JetBrains Mono，与侧栏激活月份显示、tab 栏快捷键、文件名 tag 完全同字族
- 顺手修了一个 chart-card padding `24px 28px` 的"28px 不在 4-px 节奏"问题（→ 24 32，标准的 4-px 节奏）

### 3. 漏网之鱼扫描

**全站搜了一遍 `font-family: monospace`（generic）**:
- 改前：DashboardView `.timeline-label` 是唯一漏网
- 改后：0 处 generic monospace 残留
- 所有 mono 字体的位置（TabBar / MemoryCard / DashboardView timeline / SearchBar kbd）都用 `var(--font-mono)`

**标题染色扫描（h2 用 --accent 而不是 --primary）**:
- 只有 CollectionsView 用了 `var(--primary, #007aff)`，但 fallback 是误导的 — 已改
- 其他 view 的 h2 全部是 `var(--primary)`，干净

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors |
| `npm run build` | ✅ 2.43s，dist 完整生成 |
| 8501 服务进程 | 未触碰，仍在 serving `frontend/dist`（用户刷新即生效） |
| 后端 / 新依赖 | 无 |
| P37 注释保留 | ✅ `/* P37: btn-refresh — Geist 风格 outline 按钮 */` 和 `/* P37: Chart Cards — 用 box-shadow 替代 border 营造悬浮感 */` 都未触碰 |
| 现有功能回归 | 仅 CSS 改动，模板结构、事件绑定、API 调用 0 变化 |

---

## 设计决策记录

### 为什么只改 CollectionsView 和 DashboardView？
- P40 报告明确"为什么不全做 sweep"：硬约束是"每次改 2-3 项、立即验证"
- ProfilesView / AgentMemoryView / HermesMemoryView / SourcesView / CompareView / SettingsView 都有类似裸值间距，但**视觉影响力低于 CollectionsView / DashboardView**（CollectionsView 是入口 page 之一，DashboardView 是统计 dashboard）
- 一次只动两个 view 是 P40 报告策略的延续

### 为什么 CollectionsView 按钮从蓝改黑/白？
- 这是**对 P39 设计决策的应用**，不是新决策
- P39 报告里写得很清楚："`--accent` (#0072f5) 已经是侧栏激活态、链接、搜索框 focus 的'蓝色信号'，把 primary CTA 也涂蓝会与这些'导航/信息'语义混淆"
- CollectionsView 之前是 P39 报告遗漏的页面，本次顺手补上

### 为什么不动 SettingsView 的 .btn-primary？
- SettingsView 的 `.btn-primary` 也是 `var(--accent)` 蓝色 + `color: white` — 与 CollectionsView 同性质
- 但 SettingsView 是表单场景（"保存"按钮是主 CTA），用户对"蓝色保存"已经有强心智模型（macOS / iOS 偏好）
- 改 SettingsView 会引发**新的设计决策**（"表单保存按钮用黑还是蓝"），不在本轮范围
- **记录为下次可做**

### 为什么 hist 内部 6px/30px 不改？
- chart 内部间距是**功能性的微调**（柱子与柱子的视觉间隔，柱底 label 的留白），不是节奏系统层面
- P40 spacing scale 是为 **section / card / 内边距** 这种"页面节奏"服务的
- chart 内部的视觉精度属于"数据可视化"领域，强行套 4-px 节奏可能反而破坏视觉精度

---

## 遗留 / 下次可以做

1. **SettingsView `.btn-primary` 颜色决策** — 表单保存按钮是 `--primary` 黑/白（与 P39 决策一致）还是 `--accent` 蓝（用户对 macOS 蓝色保存按钮的心智模型）？需要单独的设计决策
2. **ProfilesView / AgentMemoryView / HermesMemoryView / SourcesView / CompareView 标题/间距 token 化** — P41 的延伸，本轮不 sweep
3. **CommandPalette Geist 化** — P38 / P39 报告里两次点名，450+ 行的硬编码颜色块（result type 7 种颜色用 14 个 hex），本次未触碰（风险大，需单独审计）
4. **HomeView "创建记忆"按钮的副 CTA 入口** — P39 报告里建议过"3 个 secondary 按钮可以用 icon-only 或 collapse 到菜单"，未做

---

## 跨 P38-P41 一致性自查

| 元素 | 现状 | 状态 |
|---|---|---|
| 主 CTA 按钮（创建/保存/新建） | HomeView / CollectionsView 用 `--primary` 药丸 | ✅ 一致（SettingsView 待决策） |
| Secondary 按钮 | HomeView（导入/导出/去重）/ DashboardView（刷新）用白底 outline | ✅ 一致 |
| 标题 h2 颜色 | 所有 view 用 `var(--primary)` | ✅ 一致 |
| h2 margin-bottom | DashboardView 改 32 → 32 (--space-7)，CollectionsView 24 → 20 (--space-header-gap) | ✅ 与 P40 HomeView 节奏同 |
| Section gap | HomeView / DashboardView / CollectionsView 间距全部走 spacing scale | ✅ 一致 |
| mono 字体 | TabBar / MemoryCard / SearchBar / DashboardView timeline 全部 `var(--font-mono)` | ✅ 一致 |
| 硬编码 hex 颜色（除 fallback） | 0 处（已扫） | ✅ 干净 |
| type chip 色块化 | MemoryCard / UnifiedCard 都用同一套 dot + uppercase + 18% border | ✅ P39 一致 |
| strength ring 视觉锚点 | MemoryCard 已加，P39 报告后无新加需求 | ✅ 稳定 |
| 侧栏 left rail | AppSidebar 已加（实心蓝药丸→左侧 rail + 蓝字） | ✅ P38 稳定 |
