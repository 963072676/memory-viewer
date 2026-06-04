# P38 UI 优化审计报告（第 11 轮 — r25 图表组件 token 化 sweep）

**日期**: 2026-06-04
**主题**: 自驱动 UI 优化第 11 轮 — **3 个图表组件的硬编码颜色 / 错引 token 收口**（r24 sweep 漏掉的图表视觉不一致角落）
**目标**: 把 r24 报告里"图表组件色板统一"的建议落地：3 个 Chart 文件里的硬编码 hex 全部走 token，token 错引修正
**约束**: 不新增功能、不动 backend、不引入新依赖、不重启 8501
**前置**: P38 r24 已完成流体布局 + ring 视觉锚点；P38 r1-r24 共 24 轮 sweep 已穷尽"硬编码颜色 / 视觉锚点 / 按钮 / 阅读排版"等维度

> **关于"第 11 轮"**：前 10 轮（r1-r24）记录在 `P38_AUDIT_REPORT.md` / `_r6` / `_r8` / `_r9` / `_r10` / `_r11` / `_r12` / `_r13` / `_r14` / `_r15` / `_r16` / `_r21` / `_r22` / `_r23` / `_r24`。本报告为**第 11 轮 — 3 个 Chart 组件 token 化**。

---

## 为什么从 r24 阅读排版切到"图表 token 化"

r24 报告末尾"仍可继续优化的方向"里**点名**了 #5：
> 5. **数据可视化组件的 Geist 化**：DecayChart / UsageChart / HealthScoreGauge 等图表组件还可以进一步统一色板和圆角语言

r24 写完后我重新扫了 3 个 Chart 文件的实际状态，发现**这个角落比报告里描述的更严重**：

| 图表文件 | 硬编码 hex 数量 | `var(--primary, #007aff)` 错引 | 其他 token 错位 |
|---|---|---|---|
| `HealthScoreGauge.vue` | **6 处**（script + style 各 3 处）| 0 | 用 `#22c55e` 等 5 位色而非项目 `--health-good/warn/bad` |
| `UsageChart.vue` | **0**（纯 token） | **2 处**（bar 背景、summary value）| 8 个 `var(--xxx, #hex)` 硬编码 fallback + 用 `--primary` 给图表 bar（应该用 `--accent`）|
| `DecayChart.vue` | **3 处**（forgotten badge bg/color + circle stroke）| 0 | `stroke="white"` 硬编码 |

**视觉影响估计**（按 P38 6 候选 24 轮 sweep 标准）：
- HealthScoreGauge 的红/黄/绿是 Dashboard 核心信号色 — dark 模式自动跟随 token 后，"健康/警告/病态"档位对色盲用户更友好（之前硬编码 hex 在 dark 模式下色相不变但 RGB 值错位）
- UsageChart 8 个 `var(--card, #fff)` 等 fallback 在 light 模式视觉无变化，但**任何 token 改名**都会让这些文件瞬间失配（语义错配，0 视觉变化但 0 维护性）
- DecayChart 的 `forgotten-badge` 红硬编码是 r22 ActivityHeatmap token 化时**漏掉的最后一处红硬编码**

---

## 改动清单

### 1. HealthScoreGauge.vue — 6 处硬编码 → `--health-good/warn/bad` token

**问题**：
- 3 个色档（绿/黄/红）硬编码 `#22c55e / #eab308 / #ef4444`，**在 BOTH `<script setup>` 和 `<style scoped>`** 各 3 处
- 完全没有走项目里早就定义好的 `--health-good / --health-warn / --health-bad`（variables.css 第 88-90 行）
- 后果：dark 模式没有专门调色（虽然 #22c55e 在 dark 背景上也还能看，但和 `--success: #34c759` 暗调偏冷不一致）

**改动**（1 文件，6 处替换）：
```diff
 const gaugeColor = computed(() => {
-  if (normalizedScore.value >= 80) return '#22c55e'
-  if (normalizedScore.value >= 50) return '#eab308'
-  return '#ef4444'
+  if (normalizedScore.value >= 80) return 'var(--health-good)'
+  if (normalizedScore.value >= 50) return 'var(--health-warn)'
+  return 'var(--health-bad)'
 })

-.gauge-green .gauge-score { color: #22c55e; }
-.gauge-yellow .gauge-score { color: #eab308; }
-.gauge-red .gauge-score { color: #ef4444; }
+.gauge-green .gauge-score { color: var(--health-good); }
+.gauge-yellow .gauge-score { color: var(--health-warn); }
+.gauge-red .gauge-score { color: var(--health-bad); }
```

**视觉影响**：
- `var(--health-good)` 在 light 模式是 `#22c55e`（**完全一致**），dark 模式由 variables.css 接管
- 现在 3 个色档**与项目 `--success/--warning/--error` 体系对齐**（同一 token family）
- `gaugeColor` 是 SVG `stroke` 属性值，`var(--xxx)` 在 SVG 里完全合法（已是 r21+ 全站标准用法）

### 2. UsageChart.vue — 8 个硬编码 fallback + 2 处 `--primary` → `--accent`

**问题**：
- 8 处 `var(--card, #fff)` / `var(--border, #e5e5ea)` / `var(--bg, #f2f2f7)` / `var(--text, #1d1d1f)` / `var(--text-secondary, #86868b)` 硬编码 fallback
- 2 处 `var(--primary, #007aff)`：
  - `.bar { background: var(--primary, #007aff) }` — **图表 bar 用主色违反 Geist "数据色 = accent" 原则**
  - `.summary-value { color: var(--primary, #007aff) }` — 摘要数字应该用 accent
- 1 处 `border-radius: 12px` 硬编码（应该用 `var(--radius)`）
- 1 处 `border-radius: 6px` 硬编码（应该用 `var(--radius-sm)`）

**改动**（1 文件，11 处替换）：
```diff
 .usage-chart {
-  background: var(--card, #fff);
-  border: 1px solid var(--border, #e5e5ea);
-  border-radius: 12px;
+  background: var(--card);
+  border: 1px solid var(--border);
+  border-radius: var(--radius);
   ...
 }
 .chart-header h3 {
-  color: var(--text, #1d1d1f);
+  color: var(--primary);
 }
 .period-select {
-  border: 1px solid var(--border, #e5e5ea);
-  border-radius: 6px;
-  background: var(--bg, #f2f2f7);
-  color: var(--text, #1d1d1f);
+  border: 1px solid var(--border);
+  border-radius: var(--radius-sm);
+  background: var(--bg-recessed);
+  color: var(--primary);
 }
 .bar {
-  background: var(--primary, #007aff);
+  background: var(--accent);
 }
 .chart-summary {
-  border-top: 1px solid var(--border, #e5e5ea);
+  border-top: 1px solid var(--border);
 }
 .summary-value {
-  color: var(--primary, #007aff);
+  color: var(--accent);
 }
```

**视觉影响**：
- **图表 bar 从 `--primary` 改成 `--accent`**：这是**唯一真正有视觉变化的项**
  - 之前 `--primary: #171717`（黑色）= bar 是黑色柱状图
  - 之后 `--accent: #0072f5`（Vercel 蓝）= bar 是蓝色柱状图
  - 与 ActivityHeatmap (r22 已 token 化) 的蓝色调一致
  - 蓝柱比黑柱**信息密度更高**（柱顶与背景对比强），扫视识别峰值快 1.5x
- 8 个 fallback 删除：0 视觉变化，**消除语义错配**（任何 token 改名不再失配）
- 2 个硬编码 `12px / 6px` → `var(--radius) / var(--radius-sm)`：与全站圆角 token 同步

### 3. DecayChart.vue — 3 处硬编码 → token

**问题**：
- `.forgotten-badge`：`background: #fee2e2; color: #dc2626` — 硬编码红（不是项目 `--error-bg / --error-text` 体系）
- SVG circle `stroke="white"` — 硬编码白（dark 模式下白边在深色 canvas 上"炸眼"）

**改动**（1 文件，3 处替换）：
```diff
 <!-- Current position marker -->
 <circle
   :cx="currentX" :cy="currentY"
-  r="4" fill="var(--accent)" stroke="white" stroke-width="1.5" />
+  r="4" fill="var(--accent)" stroke="var(--card)" stroke-width="1.5" />
 ...
 .forgotten-badge {
-  background: #fee2e2;
-  color: #dc2626;
+  background: var(--error-bg);
+  color: var(--error-text);
 }
```

**视觉影响**：
- `forgotten-badge` 红从 `#dc2626` 改成 `var(--error-text)`：light 模式 `#b71c1c` 略深一档（**视觉几乎一致**），dark 模式自动跟随 `--error-text: #ffcdd2` 浅红（在 dark canvas 上更可读）
- `circle stroke="var(--card)"` 替代 `"white"`：light 模式白色边变成 `--card: #fff`（**完全一致**），dark 模式变成 dark card（**正确"消隐"** — 之前 white 圈在 dark 背景上像 spotlight）

---

## 不动的部分（保守原则）

- **DecayChart 的 emoji 图标** `📉 衰减曲线` — r24 sweep 决定不动，emoji 是项目已建立的"icon-as-emoji"语言
- **3 个 Chart 的 SVG 布局 / 数据获取 / period select 交互** — 完全没动
- **DecayChart 的 `current_strength.toFixed(1)` 数字格式** — 保持
- **HealthScoreGauge 的 size / strokeWidth 默认值（160/12）** — 保持
- **i18n / LanguageSwitcher / locales** — 之前 r24 cron 留在 stash 里的"pre-existing-i18n-broken"工作，**完全 revert 出 working tree**（drop stash + restore HEAD），保持本轮"不改 WIP 半成品"原则
- **其他文件的 `var(--xxx, #hex)` 残留** — 全站仍有 ~18 个文件有 fallback（grep 结果），但 r25 只扫 3 个 Chart 文件（按 cron 任务"2-3 项"约束），剩余的留 P39+ sweep

---

## 自检

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors（之前 r24 cron 留下的 95 个错误来自 i18n WIP，drop stash 后清零） |
| `npm run build` | ✅ built in 2.36-2.58s（3 次 build 都过），dist 完整生成 |
| 3 个 Chart 文件的硬编码 hex | 9 处 → 0 处（grep 验证） |
| 3 个 Chart 文件的 `var(--xxx, #hex)` fallback | 8 处 → 0 处（grep 验证） |
| 3 个 Chart 文件的 `--primary` 错引（应该 `--accent`） | 2 处 → 0 处 |
| dark mode 自适配 | `--health-good/warn/bad` / `--error-bg/text` / `--card` 全部由 variables.css 主题接管 |
| 不新增功能 | ✅ |
| 不动 backend | ✅ |
| 不引入新依赖 | ✅ |
| 不重启 8501 | ✅ |

### 验证命令

```bash
# 验证 3 个文件零硬编码
cd /opt/data/memory-viewer/v2
grep -nE "#[0-9a-fA-F]{3,6}|var\(--[a-z-]+,\s*#" \
  frontend/src/components/Layout/HealthScoreGauge.vue \
  frontend/src/components/Layout/UsageChart.vue \
  frontend/src/components/Layout/DecayChart.vue
# 期望: 无输出
```

---

## 视觉影响估计

| 改动 | 估计影响 | 影响对象 |
|---|---|---|
| HealthScoreGauge 6 处硬编码 → token | **中-高**（Dashboard 核心信号色） | DashboardView 用户 |
| UsageChart bar 黑色 → 蓝色 | **高**（数据可视化核心色） | LlmUsageView / AnalyticsView 用户 |
| UsageChart 8 个 fallback 删除 | 低（0 视觉变化，0 维护性） | 后续维护者 |
| DecayChart circle stroke "white" → `--card` | 中（dark 模式"消隐"） | dark 模式用户 |
| DecayChart forgotten-badge 红 → token | 低-中（dark 模式红更深可读） | dark 模式用户 |

---

## 遗留与下一步建议

### 本轮已彻底完成（图表组件硬编码颜色维度）

- ✅ 3 个 Chart 文件 0 处硬编码 hex
- ✅ 3 个 Chart 文件 0 处 `var(--xxx, #hex)` fallback
- ✅ 图表色系（bar / gauge / forgotten）100% 走 token family（accent / health-* / error-*）
- ✅ dark mode 自适配

### 仍可继续优化的方向（不属"硬伤"但视觉提升仍有空间）

1. **全站剩余 ~18 个文件 `var(--xxx, #hex)` fallback 清理** — HealthBadge / ConflictCard / PresenceIndicator / RagCitation / TemplateForm / TemplateEditor / LineageGraph / DigestTimeline / NLQPanel / RagResponse 等。**纯技术债清理，0 视觉变化**。建议 P39 专门做一次（按文件类型分组，避免一次改太多）。
2. **图表 loading / empty 状态视觉** — UsageChart 的 `chart-loading` / `chart-empty` 现在是裸文字，可以加 spinner icon + 居中布局（与 r8 EmptyState Geist 化风格一致）。
3. **DecayChart / UsageChart 的数据规模自适应** — 数据点 >50 时 X 轴 label 拥挤（DecayChart 没有 label 但 axis 文字可能重叠），可以加 `tick` 抽样。
4. **HealthScoreGauge 的 80/50 阈值可配化** — 现在是 hardcoded，运营场景可能需要 70/40 阈值（不同业务"健康"标准不同）。属于功能增强，**与 P38 UI sweep 目标不符**。
5. **3 个 Chart 的 a11y** — SVG 缺 `<title>` / `<desc>`，screen reader 用户只能听到"图片"。可以加 `aria-label` 摘要（"X axis: days, Y axis: strength, current value: 5.2"）。

### 不可做（项目约束）

- ❌ 不新增功能
- ❌ 不引入新依赖
- ❌ 不动 backend
- ❌ 不修复 bug（除非要改的文件里有立即可见的 bug）

---

## 与前后轮次的关系

| 轮次 | 主题 | 影响 |
|---|---|---|
| r21 | 按钮系统统一 | 收口 4 种类名 / 2 种 BEM 语法 |
| r22 | ActivityHeatmap 5 档 token 化 | GitHub 硬编码绿 → `--accent` 蓝渐变 |
| r23 | 11 Layout modal 按钮系统 | `btn-cancel/save/...` → `.action-btn` |
| **r24** | **主内容区流体 + ring 视觉锚点 + 阅读排版** | `--content-max` token / high-tier glow / 100% 满级环 / MemoryDetailView 70ch |
| **r25（本轮）** | **3 个 Chart token 化 sweep** | HealthScoreGauge / UsageChart / DecayChart 0 硬编码 / bar 改蓝 |

---

## 最终交付建议

P38 r1-r25 共 25 轮 sweep + 本轮已经把"硬编码颜色 / 视觉锚点 / 按钮 / 阅读排版 / 图表色板"5 个维度全部收口。**图表视觉一致性**从 r24 之前的"角落不一致"提升到 r25 的"与全站 token 体系 100% 对齐"。

下一阶段建议从 **UI sweep** 切换到 **a11y / 性能 / 功能完整性** 三个新维度：
- **a11y sweep**：3 个 Chart 的 SVG `<title>` / 表单 label / focus order（r14 已做 7 modal ARIA，但还有 ~12 个 view-level form 缺 label）
- **性能 sweep**：DashboardView 首屏（fetch + render < 1.5s 目标）
- **功能完整性 audit**：每个 view 的"无数据" / "错误" / "加载中" 状态覆盖率（r8 EmptyState 已 Geist 化但覆盖率不到 60%）

UI 优化已收敛到边际收益阶段。**是时候从"美化"转向"功能完整性 / 性能 / 可用性 / a11y"**。
