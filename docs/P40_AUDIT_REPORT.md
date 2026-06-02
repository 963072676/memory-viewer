# P40 UI 优化审计报告

**日期**: 2026-06-03
**主题**: 自驱动 UI 优化第四轮 — Header 对齐轴线 / Spacing scale token / kbd 字体 Geist 一致性
**前提**: P38（strength 锚点 / 侧栏 left rail / SearchBar）+ P39（按钮层级 / type chip）已落地
**约束**: 不新增功能、不动 backend、不引入新依赖

---

## 改动清单

### 1. AppHeader max-width 与内容对齐轴线（视觉严谨度）

**问题**:
- `.header-content` 用了 `max-width: 1400px`，而下方的 `.main-wrapper .container` 是 `1200px`
- 在 1920+ 宽屏上，header 居中轴线和内容居中轴线错位 100px
- header 左侧 ☰ 按钮、右侧 🌗 按钮、tab栏、卡片栅格四者本应共享一条隐形轴线，现在不齐

**改动** (`frontend/src/components/Layout/AppHeader.vue`):
- `.header-content` `max-width: 1400px` → `1200px`
- 与 `App.vue` 的 `.main-wrapper .container` 共享 1200px 边界

**影响估计**:
- 1920+ 屏左右边界完全对齐（之前 header 比内容"漂"出 100px 不严谨）
- 小屏（< 1200px）行为完全不变（两边都用 `margin: 0 auto` + 内部 padding 兜底）
- 是"用户未必看得到、但盯久了会觉得对齐"的细节，专业感 +1

---

### 2. Spacing scale token（HomeView 节奏系统化）

**问题**:
- HomeView 内部间距裸值混用：`8px / 12px / 16px / 20px / 24px / 32px / 48px`
- 没有"4-px 节奏"系统，section 与 section、section 与 header、card 与 card 之间的间距是"当时感觉对就那样"
- P35 报告里 Geist/Vercel 风格的精髓之一就是 spacing scale，variables.css 里有 color / radius / shadow token 但**唯独缺 spacing**

**改动**:

(a) `frontend/src/styles/variables.css`:
- 新增 9 个 `--space-1` 到 `--space-9` 基础 token（4/8/12/16/20/24/32/48/64px）
- 加 3 个语义化别名：`--space-section-gap` (48px) / `--space-header-gap` (20px) / `--space-card-gap` (20px)
- 主题无关（亮色 / Dark 模式都不需要不同值），所以只放在 `:root`

(b) `frontend/src/views/HomeView.vue`:
- `.section` `margin-bottom: 48px` → `var(--space-section-gap)`
- `.section-header` `margin-bottom: 20px` → `var(--space-header-gap)`，gap 12px → `var(--space-3)`
- `.section-actions` `gap: 8px` → `var(--space-2)`
- `.action-btn` `padding: 8px 14px` → `var(--space-2) var(--space-4)`，border-radius `8px` → `var(--radius-md)`
- `.card-grid` `gap: 20px` → `var(--space-card-gap)`
- `h2` `margin-bottom: 20px` → `var(--space-5)`

**影响估计**:
- HomeView 内的所有间距从"看感觉"变成"看 token"，未来修改节奏只动 variables.css
- 为 P41+ 在 DashboardView / MemoryDetailView / CollectionsView 等其他页面也走同一套 token 留好接口
- 暗色模式自动跟随（spacing 不分主题，色彩分主题）

**为什么不全部 sweep？** P36 审计报告里有很多页面都有类似裸值间距，但硬约束是"每次改 2-3 项、立即验证"。本次只动 HomeView 内部间距变量，**为后续"全站 token 化"留出可扩展接口**，避免一次改太多导致回滚困难。

---

### 3. kbd 字体 Geist 一致性（TabBar + MemoryCard）

**问题**:
- P38 报告里专门指出"搜索框的 kbd 提示用了 `monospace` generic，应使用 `var(--font-mono)`"
- P38 只改了 SearchBar，但同样问题在 **TabBar `.tab-key`** 和 **MemoryCard `.file-tag`** 都还存在
- Chrome 默认会把 `monospace` 回退到 Courier New / Times，与 Geist 整体调性冲突

**改动**:

(a) `frontend/src/components/Layout/TabBar.vue`:
- `.tab-key` `font-family: monospace` → `var(--font-mono)`
- 顺手补 `background: var(--card)`（与 SearchBar 的 kbd 一致）和 `line-height: 1.2`（避免 mono 字体基线偏移）

(b) `frontend/src/components/Layout/MemoryCard.vue`:
- `.file-tag` `font-family: monospace` → `var(--font-mono)`
- 不动 `font-size`（避免破坏 `.tag` 的 0.7rem 一致性）

**影响估计**:
- tab 栏的快捷键提示（1/2/3）、记忆卡片的文件名标签（如 `Dockerfile`）都会用 SF Mono / JetBrains Mono 渲染
- 与 P38 的搜索框 ⌘K / / 提示完全一致，跨 section 的 mono 字体语言统一
- 不修改 dead code（`views/deprecated/` 下还有 9 处 `monospace` 引用，但那些是已废弃页面，不在硬约束范围）

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors（每改一项都验证了一次） |
| `npm run build` | ✅ 2.45s，dist hash: `index-Dac_zJXi.js` |
| 8501 端口服务 | ✅ HTTP 200，新 hash 已下发（uvicorn serve dist，未触碰 backend） |
| 8501 后端进程 | 未触碰（`ps aux | grep uvicorn` 命令未执行） |
| 跨页面回归 | 只改 HomeView / AppHeader / TabBar / MemoryCard 的 CSS，未触 JS / TS 逻辑 |
| 新依赖 | 无（spacing token 全部走 CSS 变量） |

---

## 设计决策记录

### 为什么是 1200px 而非 1280px / 1400px？
- 1200px 是 Vercel / Geist 官方文档的 canonical content width
- 1200px 下中文每行约 30-40 字、英文约 80-100 字符，都接近最优阅读长度（45-75 字符）
- 与 P37 设计的 `--radius: 12px` / `--space-7: 32px` 等 token 同属"小而美"系

### 为什么 spacing token 不分主题？
- 间距不随亮/暗模式变化，所有主题用同一套值
- 强行分主题会让"暗色模式间距更大"这种诡异问题出现

### 为什么没改 `.tab-key` 的 `border-radius: 3px`？
- 搜索框的 kbd 是 `border-radius: 3px`（TabBar 已对齐）
- 没改意味着延续 P38 的视觉系统，避免在 P40 里"统一 A 又不统一 B" 的小动作

---

## 已知遗留（未在 P40 解决）

1. **`views/deprecated/` 下还有 9 处 `font-family: monospace`** —— 这些是已废弃页面，下一轮可批量扫掉
2. **AppHeader 内边距 `padding: 12px 24px` 与 SearchBar `padding: ... 24px` 不完全统一** —— 24px 都来自 `--space-6`，但首页其他 .section padding 不一致（12/16/20px 都有）
3. **DashboardView 等其他页面 spacing 仍是裸值** —— 留作 P41+ 全站 spacing token 化时统一处理
4. **TabBar 容器类名仍叫 `.search-bar`**（实际是 tabs + 工具栏）—— 改类名涉及 1 处 selector 复用检查，风险大于收益，留作未来重构

---

## 下次可以做什么

1. **spacing token 全站 sweep**：把 DashboardView / MemoryDetailView / CollectionsView / SourcesView / ProfilesView / AgentMemoryView 的裸值间距全部走 `--space-*`
2. **`font-family: monospace` 全站清理**（含 deprecated/）—— 一行 sed 替换为 `var(--font-mono)`
3. **空状态 EmptyState 升级**：检查 `views/MemoryDetailView.vue` 等页面的空状态，统一用 P37 的 Geist 化 EmptyState
4. **Focus ring 全局统一**：用 `:focus-visible` 替代部分组件硬编码的 `:focus`，提供键盘可达性
5. **Modal 边框风格统一**：CreateMemoryModal / ImportModal / EditMemoryModal / DedupModal / ShareModal 的边框风格不一，可统一为 `--shadow` 边框（1px shadow-as-border）
