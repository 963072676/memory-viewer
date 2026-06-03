# P38 UI 优化审计报告（第三轮 — 收尾级 sweep）

**日期**: 2026-06-03
**主题**: 自驱动 UI 优化第三轮 · 收尾
**目标**: CompareView 颜色 token 化（消除最后一批 Material 硬编码）+ AgentMemoryView / MemoryDetailView 按钮层级统一
**约束**: 不新增功能、不动 backend、不引入新依赖
**前置**: P37–P43 已收敛 Geist 风格、按钮层级、type chip 色块、spacing scale、modal-backdrop、Geist mono、Dashboard type-bar token、暗色 mode 契约

---

## 改动清单

### 1. CompareView 三栏 diff 关系 — Material 硬编码 → `--diff-*` token（最大视觉影响）

**问题**:
- 6 处硬编码 Material 2014 调色：`#2196f3`（蓝）/ `#4caf50`（绿）/ `#f44336`（红）
- dark mode 单独写了 3 条 `[data-theme='dark']` 规则用 0.1 rgba 复制这 3 个 hex → dark mode 下三栏**完全没有视觉锚点**（颜色既不饱和也不亮）
- 整页只有左侧 3px 边框一种视觉线索，diff 关系表达力度太弱
- 这 6 个 hex 是项目里**最后一批 Material 硬编码色**（P36 审计漏掉 CompareView，因为它是低频功能页）

**改动** (`frontend/src/views/CompareView.vue` + `frontend/src/styles/variables.css`):

新增 3 对 token（`--diff-*-border` / `--diff-*-bg`），light/dark 模式各一套：
- **left-only** 冷静蓝 `#5b8def`（light）/ `#7aa2f0`（dark）— 呼应 `--accent` 但更弱
- **common** 稳定绿 `#19a66e`（light）/ `#34c77a`（dark）— 呼应 `--success` 但更稳
- **right-only** 暖橙 `#d97706`（light）/ `#f59e0b`（dark）— 与 `--type-fact-text` 同源（差异=提示）

每个 column 从"3px 左边框"升级为"3px 左边框 + 4px 同色内阴影 + bg 微调（rgba 0.08/0.10）"，diff 关系从"单一线条"变成"半色块"。

**影响估计**:
- 6 个 Material hex → 0，hex 硬编码数从 6 → 0
- dark mode 下三栏有了清晰的视觉锚点（之前几乎是黑色 + 暗红/暗绿/暗蓝边框，完全分不清）
- 3 个 diff token 后续可在其它"二元对比"页面复用（双向 sync 对比、A/B 测试、conflict diff 等）
- 省 1 个 `[data-theme='dark']` media query 块（token 自动跟随）

---

### 2. AgentMemoryView 按钮层级 — 5 个全平铺 → 1 primary + 4 secondary

**问题**:
- 5 个 `.action-btn`（+ 创建 / 导入 / 导出 / Bulk Auto-Tag / 去重）全部同一层级（描边 card）
- `.ai-autotag-btn` / `.dedup-btn` 单独写了 `border-color: var(--accent); color: var(--accent)` 描边样式 → **2 个假 primary** 与真 primary（如果之后有）撞色
- 这 2 个假 primary 的 hover 还会变成 accent 实色（`background: var(--accent); color: white`），**比创建按钮视觉权重还高** — 严重违反按钮层级原则

**改动** (`frontend/src/views/AgentMemoryView.vue`):
- 模板：「+ 创建」加 `.action-btn--primary` 类（最高频操作 → 主 CTA）
- 模板：Bulk Auto-Tag / 去重 去掉 `.ai-autotag-btn` / `.dedup-btn` 类，回到普通 `.action-btn`
- CSS：删除 2 个死代码块（`.ai-autotag-btn` / `.dedup-btn`）
- CSS：新增 `.action-btn--primary` 样式，与 HomeView (P39) / CollectionsView (P41) **完全对齐**：
  - `background: var(--primary); color: var(--card); border-color: var(--primary)`
  - hover `var(--primary-muted)`
  - box-shadow `0 1px 0 rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.08)`
  - 不用 pill 圆角（与 secondary 同 8px 圆角，保持设计语言一致）

**影响估计**:
- 「+ 创建」从 5 个等权按钮中**跳出来**，用户第一眼能识别主要操作
- 之前 2 个 accent 描边假 primary 取消 → 视觉噪声下降，页面"冷静度"提升
- 全站 primary 按钮样式现在只有 1 套（P39 + P41 + 本次 = 同源），不再有 3 套变体

---

### 3. MemoryDetailView 按钮层级 — 5 个 accent 实色 → primary + ghost × 3 + danger

**问题**（P36 漏网之鱼，影响最大）:
- `.action-btn` 默认 `background: var(--accent); color: white; border: none` — **实色蓝底白字**
- 5 个按钮（折叠/编辑/分享/历史/删除）全部用默认样式 → 5 个**同色同权的"假 primary"** 同时喊叫
- `.action-btn.danger` 用了 `var(--danger, #dc3545)` 硬编码回退值 → `#dc3545` 是 Bootstrap 红色，与全站 `--error: #ff3b30` 不一致
- 这是项目里**视觉最嘈杂的页面**之一，用户第一眼不知道该点哪个

**改动** (`frontend/src/views/MemoryDetailView.vue`):
- 重写 `.action-btn` 默认值：从 `accent 实色` → `card 描边`（ghost 形态）
- 新增 `.action-btn--primary`（编辑，最常用）
- 新增 `.action-btn--danger`（删除，破坏性）：`var(--error)` + `color-mix(30% error + border)` 半透明红描边
- 新增 `.action-btn--ghost`（折叠/分享/历史，utility）— 显式语义标记，无额外样式
- `.action-btn.danger` → `.action-btn--danger`（BEM 命名统一）
- 删除硬编码 `#dc3545` 回退值

**影响估计**:
- 5 按钮从"全部蓝底白字" → "1 实色黑底 + 3 描边 + 1 红字" 清晰三层视觉层级
- 编辑是主要操作 → primary 实色，用户第一眼能看到
- 删除是破坏性操作 → 红字描边（**不**用红底实色，避免抢戏）— 这是 shadcn/ui 的成熟设计
- 折叠/分享/历史都是"看+导航" → 最低权重的 ghost 描边，符合 Geist 的"安静按钮"哲学

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors |
| `npm run build` | ✅ built in 2.39s |
| Material 硬编码 hex 数 | 6 → 0（CompareView 全部清除） |
| 死代码 | 8 行 `.ai-autotag-btn` / `.dedup-btn` CSS 删除 |
| 按钮层级语言 | HomeView / CollectionsView / AgentMemoryView / MemoryDetailView **4 个页面用同款 primary 样式** |

---

## 视觉影响估计

| 改动 | 估计影响 | 影响对象 |
|---|---|---|
| CompareView 三栏 token 化 | **中-高** | 暗色模式用户**特别明显**（之前 diff 完全不可见，现在清晰） |
| AgentMemoryView 按钮层级 | **中** | 「+ 创建」从等权变主 CTA，5 按钮降噪 |
| MemoryDetailView 按钮层级 | **高** | 5 假 primary → 1 primary + 3 ghost + 1 danger，**全站最嘈杂页面之一**清理 |
| 全站 hex 硬编码清理 | **中** | dark mode 一致性 + 全站颜色契约维护成本降低 |

---

## 遗留

- **MemoryDetailView "重试"按钮**（line 28，错误状态）现在继承默认 ghost 样式 — 之前是 accent 实色。这是**好的变化**（错误状态不抢戏），但万一产品希望"重试"高亮强调，可单独加 `.action-btn--primary`。
- **CommandPalette** 里的 action 还是单色 — 不在这次 scope 内（属于命令面板，视觉上与按钮组不同）。
- **SettingsView / SourcesView** 的 `.action-btn` 仍是基本样式 — 没在这次 scope 内，但它们按钮数 ≤ 2，主次关系不明显，按钮层级问题不突出。

---

## 下次可以做什么

1. **Strength 数字节奏** — MemoryCard `.strength-ring__num` 用 Geist Mono 字体（已 P42 P43 完成大部分）— 检查是否还有散落的非 mono strength 数字
2. **Loading skeleton 统一** — 各页面 skeleton 卡片（AgentMemoryView / HomeView / MemoryDetailView）的尺寸不一致，可统一为 P43 风格的"shimmer 条"
3. **HomeView 第二个 section-header**（"统一记忆视图"section 已有，"AgentMemory" 和 "Hermes Memory" section 缺 section-actions 容器） — 给后两个加 actions 容器，让所有 section 结构一致
4. **Dnd panel / Conflict card** — P36 提到过，未深入
