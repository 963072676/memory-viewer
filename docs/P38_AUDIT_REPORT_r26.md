# P38 UI 优化审计报告（第 12 轮 — r26 HomeView 搜索结果视觉收口）

**日期**: 2026-06-04
**主题**: 自驱动 UI 优化第 12 轮 — **HomeView 搜索结果区域 2 处"角落不一致"收口**
**目标**: 修复 search-result-card 与上下其它 Card（MemoryCard / unified-card / hermes-card）形成的"粗糙"对比；修复 type-badge 在搜索结果与统一卡片两种视觉语言并存
**约束**: 不新增功能、不动 backend、不引入新依赖、不重启 8501
**前置**: P38 r1-r25 共 25 轮 sweep 已穷尽"硬编码颜色 / 视觉锚点 / 按钮 / 阅读排版 / 图表色板"5 个维度

> **关于"第 12 轮"**：前 11 轮（r1-r25）记录在 `P38_AUDIT_REPORT.md` / `_r6` / `_r8` / `_r9` / `_r10` / `_r11` / `_r12` / `_r13` / `_r14` / `_r15` / `_r16` / `_r21` / `_r22` / `_r23` / `_r24` / `_r25`。本报告为**第 12 轮 — HomeView 搜索结果区域视觉收口**。

---

## 为什么从 r25 图表切到"HomeView 搜索结果"

cron 任务给本轮的 6 候选里：

| # | 候选 | 评估 | 决策 |
|---|---|---|---|
| 1 | MemoryCard 视觉锚点（strength ring/颜色梯度）| r15 升 38→44px + 数字 + 渐变 + r24 high-tier glow + 100% 满级环 — **已深度做透** | ❌ skip |
| 2 | 侧栏 active 状态强化 | AppSidebar 已有 3 套（desktop 左 rail / mobile 顶 rail / sheet 填充）— **已完备** | ❌ skip |
| 3 | 按钮层级全局审计 | r21/r23 完成（.action-btn 系统 + 11 modal 收口）— **已完备** | ❌ skip |
| 4 | 主内容区 max-width + 居中 | r24 完成（--content-max token）— **已完备** | ❌ skip |
| 5 | 搜索框 input Geist 化 | SearchBar.vue 已有 recessed bg + accent focus glow + semantic mode — **已完备** | ❌ skip |
| 6 | Memory type 标签色块化 | **HomeView 搜索结果里的 `.type-badge` 仍是纯灰 pill**（r19 HomeView source-badge 收口时**漏掉搜索结果区域**的 `.type-badge`） | ✅ **本轮做** |

扫描后发现 2 个独立但同区域的视觉收口机会：

1. **`.type-badge` 双语言并存**：搜索结果里 `result.type` 走 plain gray pill；同页面的 unified-card 走 colored chip with dot。**同数据，两种视觉语言**，违反"全站 type 表达同源"。
2. **`.search-result-card` 无 hover**：r12/r13 已对 MemoryCard / unified-card / hermes-card / collection-card / dashboard-widget / template-card **6 套 Card 全部补了 hover**；唯独 search-result-card 仍是裸静态 card，跨 view 切换形成"粗糙"对比。

**视觉影响估计**（按 P38 6 候选 24 轮 sweep 标准）：

- 搜索结果 `type` 标签从灰升级为彩色 chip：用户在搜索结果与下方 unified-card 间切换时，**一眼看出"这是同一种记忆类型"**（视觉锚点）。统一感立即提升 1 档。
- search-result-card hover：用户鼠标 hover 时**视觉反馈**（translateY + 阴影），与全站 6 套 Card 形成一致 affordance —— "我点了会进详情"的暗示。

---

## 改动清单

### 1. HomeView.vue 搜索结果 `.type-badge` → `.unified-type.chip`（彩色 chip + 5px dot）

**问题**：
- 第 17、32 行的 `result.type` 用 `<span class="type-badge">`（plain gray pill: `var(--tag-bg) / var(--text-secondary)`）
- 同页面下方第 75 行 `m.type` 用 `<span class="unified-type chip chip--<type>">`（彩色 bg + colored ink + 5px dot + uppercase + 1px border）
- **同一种记忆类型，两种视觉表达**：用户在搜索结果与下方 unified-card 间切换时会感知到"语言切换"。

**改动**（1 文件，2 行替换）：

```diff
 <div class="result-meta">
-  <span v-if="result.type" class="type-badge">{{ result.type }}</span>
+  <span v-if="result.type" class="unified-type chip" :class="'chip--' + result.type">{{ result.type }}</span>
   <span v-if="result.profile" class="profile-badge">{{ result.profile }}</span>
 </div>
 ... (semantic results 同款替换)
```

**视觉影响**：
- `result.type === 'pattern'` 现在显示 `var(--type-pattern-bg) / var(--type-pattern-text)` 绿底绿字 + 5px 绿点
- `result.type === 'bug'` 显示 `var(--type-bug-bg) / var(--type-bug-text)` 红底红字 + 5px 红点
- 5 档类型（pattern / workflow / fact / preference / bug / architecture）**全部自动**走 variables.css 已有的 token family
- dark 模式自动跟随 type-* token 的 dark 调色（--type-pattern-bg: #1b3a1b 等已定义）
- 搜索结果 `result.type` 与 unified-card `m.type` **同源 = 同一视觉语言**

**为什么不改 `result.tags` 的 `.type-badge` 标签**：
- `tags` 是用户自定义的**自由标签**（如 "javascript" / "react"），不是 6 档类型之一
- 强行套 chip--<tag> 会 404 找不到 token（fallback 到默认色）
- 保持 plain gray pill 是正确的"未分类"语义表达

### 2. HomeView.vue `.search-result-card` hover 状态（同源 r12/r13 全站 6 套 Card）

**问题**：
- r12 sweep 给 4 套 Card（MemoryCard / CollectionCard / DashboardWidget / TemplateCard）补了 hover
- r20 sweep 给 hermes-card 补了 hover
- **唯独 search-result-card 漏了** —— 静态 card（无 hover, 无 transition, 无 shadow）
- 视觉后果：用户从 MemoryDetailView / AgentMemoryView 进 HomeView 搜结果时，鼠标 hover **没反馈**，与全站其它 5 套 Card 的"统一 affordance 语言"断裂

**改动**（1 文件，新增 15 行 CSS）：

```diff
+/* P38 r26: search-result-card hover — 复用 r12/r13 全站 4 套 Card 同源 hover 语言
+   (transition 0.25s cubic-bezier, box-shadow 强 + transform translateY(-2px))。
+   之前 .search-result-card 只有静态 border + radius, 无 hover, 与上下
+   MemoryCard / unified-card / hermes-card / collection-card 形成 "粗糙" 对比.
+   加上 hover 后跨 view 切换无视觉跳变. */
 .search-result-card {
   background: var(--card);
   border: 1px solid var(--border);
   border-radius: var(--radius);
   padding: 16px;
+  transition: box-shadow 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
+              transform 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
+              border-color 0.2s ease;
+}
+
+.search-result-card:hover {
+  box-shadow: var(--shadow-hover);
+  transform: translateY(-2px);
+  border-color: var(--border-strong);
 }
```

**视觉影响**：
- hover 时：阴影从 `--shadow` 升级到 `--shadow-hover`（rgba 0.06 → 0.10、blur 2px → 12px、spread 1px → 1px）
- transform translateY(-2px)：与 MemoryCard / unified-card / hermes-card / collection-card 同号（统一"轻浮起"语言，**幅度比 hermes-card 的 -3px 略小**，因为 search-result-card 高度更高，-2px 已足够视觉锚点）
- border 变 `--border-strong`（#d4d4d4 / #3a3a3a）：与 hover 阴影**同步过渡**，避免"阴影浮起但 border 还停在原位"的割裂感
- transition 0.25s cubic-bezier：与 r12/r13 全站同源（与 ring 0.5s / count-up 0.3s 同手感族）

**为什么 translateY 用 -2px 而非 -3px**：
- MemoryCard / unified-card / collection-card：内容区高度 ~140-180px，-3px 视觉上"轻浮"明显
- search-result-card：内容区高度 ~120-160px（含 snippet 多行），-3px 会让上方 h3 title 与上下文 section-header 之间出现 3px 间隙"跳一下"
- -2px 是"够暗示但不抢戏"的最优值（与 r12 unified-card / collection-card 的设计语言同源）

---

## 不动的部分（保守原则）

- **搜索结果 `.profile-badge`** — 灰色 pill 是合理"用户标识"表达，profile 不是 type，不需要彩色
- **`.match-type-badge`** (语义匹配 / 关键词匹配) — 已有 2 档专用色（--semantic-accent / --accent），保留
- **`.result-source` "🤖 AgentMemory / 🧠 Hermes"** — 已有 source-badge 三色（r6 已收口）
- **`.type-badge` CSS 规则** — 仍保留（被 `result.tags` 自由标签使用），未删除
- **`.search-result-card h3 / .match-snippet / .result-meta`** 等内部排版 — 完全没动
- **search result 无数据 / 加载中状态** — 顶部 search-results 整体由 `v-if="uiStore.searchQuery && ..."` 控制，empty/loading 在 unified 区域已有 r8 EmptyState Geist 化，**不重复**
- **i18n / LanguageSwitcher / locales** — pre-existing WIP，按 r25 决定不动

---

## 自检

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors |
| `npm run build` | ✅ built in 2.42s，dist 完整生成 |
| 搜索结果 `result.type` 视觉表达 | 1 种（统一彩色 chip + dot）— 之前 2 种（gray pill + 彩色 chip） |
| `.search-result-card` hover 状态 | 1 套（与全站 6 套 Card 同源）— 之前 0 套 |
| 改动文件数 | 1（HomeView.vue） |
| 改动行数 | 2 行 template + 15 行 CSS = 17 行净增 |
| dark mode 自适配 | chip 颜色走 --type-* token（dark 调色已定义） |
| 不新增功能 | ✅ |
| 不动 backend | ✅ |
| 不引入新依赖 | ✅ |
| 不重启 8501 | ✅（dist 已刷新，8501 serve dist 自动拾取） |

### 验证命令

```bash
# 验证 .search-result-card hover 已加
cd /opt/data/memory-viewer/v2
grep -nE "\.search-result-card[^{]*\{|hover" \
  frontend/src/views/HomeView.vue | head -10
# 期望: 看到 .search-result-card { ... transition: ... } 和 .search-result-card:hover

# 验证 type 现在用 chip 而非 plain type-badge
grep -nE "unified-type chip" frontend/src/views/HomeView.vue
# 期望: 3 行（之前 1 行）— 搜索结果 × 2 + 卡片区 × 1
```

---

## 视觉影响估计

| 改动 | 估计影响 | 影响对象 |
|---|---|---|
| 搜索结果 `type` 灰 → 彩色 chip | **高**（同源化数据视觉语言）| HomeView 搜索结果用户 |
| search-result-card hover | **中-高**（补齐全站 Card affordance）| HomeView 搜索结果用户 |

合并视觉影响：**中-高**（一个数据维度 + 一个交互维度同时收口）。

---

## 遗留与下一步建议

### 本轮已彻底完成（HomeView 搜索结果区域视觉收口）

- ✅ 搜索结果 `type` 标签 100% 走 chip 系统（与 unified-card / MemoryCard / HermesMemoryView 同源）
- ✅ search-result-card hover 与全站 6 套 Card 同源
- ✅ 1 文件改动，0 风险

### 仍可继续优化的方向（不属"硬伤"但视觉提升仍有空间）

1. **全站剩余 ~18 个文件 `var(--xxx, #hex)` fallback 清理**（r25 报告 §遗留 #1）— 纯技术债清理，0 视觉变化。建议 P39 专门做一次。
2. **3 个 Chart 的 SVG `<title>` / `<desc>` a11y**（r25 报告 §遗留 #5）— screen reader 用户感知图表语义。
3. **MemoryCard 在窄屏(<600px) 的 strength ring 缩小到 38px**（r15 升 44px 时未做响应式）— mobile ring 显得偏大，与文字比例不协调。
4. **HomeView 顶部 `unified-controls` select 与下方其它 view 的 control-select 收口** — SourcesView 已有类似 select，但 `border-radius / padding / font-size` 略有出入（8px/12px/0.85rem vs 6px/12px/0.8rem）。
5. **search-result-card 没有"打开/查看"按钮** — 现在只能 hover 反馈，没有 affordance 表达"点开是查看详情"。可以考虑在 hover 时右上角浮现 `→` 箭头（r12 unified-card 的 `.unified-card-arrow` 设计语言扩展）。

### 不可做（项目约束）

- ❌ 不新增功能
- ❌ 不引入新依赖
- ❌ 不动 backend
- ❌ 不修复 bug（除非要改的文件里有立即可见的 bug）

---

## 与前后轮次的关系

| 轮次 | 主题 | 影响 |
|---|---|---|
| r12 | 4 套 Card hover 同源 | MemoryCard / CollectionCard / DashboardWidget / TemplateCard |
| r20 | hermes-card hover + section-title 视觉锚点 | HermesMemoryView 补齐 |
| r24 | 主内容区流体 + ring 视觉锚点 + 阅读排版 | `--content-max` token / high-tier glow / 100% 满级环 / MemoryDetailView 70ch |
| r25 | 3 Chart token 化 sweep | HealthScoreGauge / UsageChart / DecayChart 0 硬编码 / bar 改蓝 |
| **r26（本轮）** | **HomeView 搜索结果视觉收口** | search-result-card hover + type chip 同源化 |

---

## 最终交付建议

P38 r1-r26 共 26 轮 sweep + 本轮已经把"硬编码颜色 / 视觉锚点 / 按钮 / 阅读排版 / 图表色板 / 搜索结果同源"6 个维度全部收口。

HomeView 搜索结果区域从 r26 之前的"孤立角落"（plain type pill + 无 hover 静态 card）提升到 r26 的"与全站 Card 系统 100% 对齐"（彩色 chip + 统一 hover 语言）。

下一阶段建议继续从 **UI sweep 收尾** 切换到 **a11y / 性能 / 功能完整性** 三个新维度（与 r25 报告 §最终交付建议一致）：
- **a11y sweep**：3 个 Chart 的 SVG `<title>` / 表单 label / focus order（r14 已做 7 modal ARIA，但还有 ~12 个 view-level form 缺 label）
- **性能 sweep**：DashboardView 首屏（fetch + render < 1.5s 目标）
- **功能完整性 audit**：每个 view 的"无数据" / "错误" / "加载中" 状态覆盖率（r8 EmptyState 已 Geist 化但覆盖率不到 60%）

UI 优化已收敛到边际收益阶段。**是时候从"美化"转向"功能完整性 / 性能 / 可用性 / a11y"**。
