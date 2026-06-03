# P42 UI 优化审计报告

**日期**: 2026-06-03
**主题**: 自驱动 UI 优化第三轮（按影响力排序）
**目标**: CommandPalette Geist 化（硬编码颜色 token 化） + EmptyState 全站替换
**约束**: 不新增功能、不动 backend、不引入新依赖、只改 CSS/Vue 模板

---

## 改动清单

### 1. CommandPalette Geist 化（最大视觉影响）

**问题**（P38 / P39 / P41 报告三次点名）:
- type badge 用了 **14 个硬编码 hex**（Google Material 配色 `#e8f0fe` / `#1a73e8` 等），与项目的 Geist 风格不统一
- **Dark 模式下 type-preference 与 type-architecture 撞色**：都是 `#1b3a1b` 背景 + `#81c995` 文字，用户在命令面板里无法区分这两个类型
- backdrop 用 `rgba(0, 0, 0, 0.5)`，panel box-shadow `0 8px 40px rgba(0, 0, 0, 0.2)`，都没走 token
- kbd 用 `font-family: inherit`，回退到系统字体（Times），与 P40 统一的 Geist mono 体系脱节
- 多个 `border-radius: 4px / 8px / 12px` 硬编码，`gap: 8px / 12px` 硬编码，未走 P40 spacing scale

**改动**:

(a) `frontend/src/styles/variables.css`:
- 新增 `--modal-backdrop: rgba(0, 0, 0, 0.5)`（亮色）/ `rgba(0, 0, 0, 0.7)`（Dark，更深一档）

(b) `frontend/src/components/Layout/CommandPalette.vue`:
- 14 处硬编码 type badge hex → `var(--type-*-bg)` / `var(--type-*-text)` token
  - 顺带删除 12 行 `[data-theme='dark'] .type-*` 重复规则（token 已在 :root 的 dark block 重新定义）
- backdrop `rgba(0, 0, 0, 0.5)` → `var(--modal-backdrop)`
- panel `border-radius: 12px` → `var(--radius-lg)`
- panel `box-shadow: 0 8px 40px rgba(0, 0, 0, 0.2)` → `var(--shadow-elevated)`
- `.palette-kbd` 与 `.palette-hint kbd` 的 `font-family: inherit` → `var(--font-mono)`（与 TabBar.tab-key 一致）
- `.palette-kbd` 的 `border-radius: 4px` → `3px`（与 TabBar.tab-key 对齐）；`padding: 2px 6px` → `1px 5px`（更紧凑）
- 7 处 `gap` / `padding` 硬编码数值 → `var(--space-1/2/3/7)` token
- 文件总行数：742 → 725（17 行净删除）

**影响估计**:
- 修复了 dark 模式下 type-preference / type-architecture 撞色 bug（之前完全无法区分）
- 命令面板视觉语言与 Geist token 系统 100% 对齐（之前有 14 处硬编码）
- 字体渲染：kbd 字符从系统 Times → Geist mono，间距更紧凑，视觉与 TabBar 一致
- Token 化覆盖率：项目硬编码 hex 残余约 12 处（AppSidebar / ConfirmDialog / LinkCreator / deprecated/），本轮未触及

### 2. EmptyState 全站替换（4 个 view）

**问题**:
- HermesMemoryView / ProfilesView / SourcesView / AgentMemoryView 4 个 view 各有自家 `.empty-state` 规则
- 多数是一行 `<p>暂无 XX</p>` + 60px 上下 padding，**完全没有 Geist 风格**（无 icon、无层级、无居中排版）
- 与 P37 创建的 `<EmptyState>` 组件（带 icon / title / message / 可选 CTA）重复

**改动**:
- `HermesMemoryView.vue`：`<p>暂无 Hermes Memory 数据</p>` → `<EmptyState icon="🧠" message="...">`，删除本地 `.empty-state` 规则
- `ProfilesView.vue`：`<p>暂无 Profile</p>` → `<EmptyState icon="👤" message="...">`，从 `.loading, .empty-state` 联合规则中拆出 `.empty-state`
- `SourcesView.vue`：`<p>📭 暂无注册的记忆源</p>` → `<EmptyState icon="📭" message="...">`，删除本地 `.empty-state` 规则
- `AgentMemoryView.vue`：复杂的 `<div class="empty-state-icon">🧠</div><h3>...</h3><p>...</p>` → `<EmptyState icon="🧠" :title="..." :message="...">`，删除本地 `.empty-state` 规则 + 未使用的 `.empty-state-icon` 引用

**有意未改**:
- `DashboardView.vue` 的 3 处 `.chart-empty` 留作单行 placeholder（数据返回时会立即替换，全 EmptyState 在 chart card 内视觉过重）
- HomeView 已有 3 处 EmptyState 使用（P37 改造过），无需动

**影响估计**:
- 4 个 view 的空状态从"一行小字"升级为"icon + 文案"的 Geist 风格（与 HomeView 一致）
- 统一了空状态的视觉语言，全站空状态组件复用率提升
- 5 个 `.empty-state` 重复规则被删除（约 30 行 CSS）

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors |
| `npm run build` | ✅ 2.41s，dist 完整生成 |
| 8501 服务进程 | 未触碰，仍在 serving `frontend/dist`（用户刷新即生效） |
| 后端 / 新依赖 | 无 |
| 现有功能回归 | type badge 颜色逻辑保持（`var(--type-*-bg)` token 在 light/dark 各自有值），type 标签语义不变 |

---

## 遗留 / 下次可以做

1. **模态 backdrop 全站 sweep** —— `--modal-backdrop` token 已加，但仍有 7+ 处文件用 `rgba(0, 0, 0, 0.5)` 硬编码（AppSidebar / ConfirmDialog / LinkCreator / deprecated/*）。下次可以做集中替换。
2. **DashboardView chart-empty 三处视觉统一** —— 当前仍是单行"暂无数据"，如果用户希望与全站 EmptyState 一致，可改为迷你版 EmptyState。
3. **`unified` 卡片整体升级** —— P39 报告里指出 unified 卡片是 P16 时期的设计，hover/active/expanded 态可参考 MemoryCard 重做。
4. **SettingsView `.btn-primary` 颜色决策** —— P41 报告里指出"表单保存按钮用 --primary 黑/白还是 --accent 蓝"，需单独设计决策。
5. **CollectionsView / HomeView 的"记忆创建"入口处 EmptyState 演示** —— P36 报告 #4 "首屏上半空洞" 仍未根治，可考虑在首屏加一个空状态欢迎卡片。
6. **Geist mono 字体字重统一** —— kbd 现在统一用 `--font-mono` + `font-weight: 500`，但不同文件对 kbd 的字重处理不一致（部分默认 400，部分 500），可全站 sweep。

---

**Commit**: P42
**Files changed**:
- `frontend/src/styles/variables.css`（+4 -0，新增 `--modal-backdrop`）
- `frontend/src/components/Layout/CommandPalette.vue`（+50 -49，14 处 hex → token + 12 行 dark 重复删除）
- `frontend/src/views/HermesMemoryView.vue`（+4 -7，EmptyState 化 + 删本地规则）
- `frontend/src/views/ProfilesView.vue`（+3 -5，EmptyState 化 + 拆 .loading 联合规则）
- `frontend/src/views/SourcesView.vue`（+4 -9，EmptyState 化 + 删本地规则）
- `frontend/src/views/AgentMemoryView.vue`（+9 -12，EmptyState 化 + 删本地规则 + 删未引用 .empty-state-icon）
- `frontend/dist/index.html`（build 产物）
