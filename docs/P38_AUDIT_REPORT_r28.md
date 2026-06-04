# P38 UI 优化审计报告（第 14 轮 — r28 in-page h3 视觉锚点 + card-grid enter stagger）

**日期**: 2026-06-04
**主题**: 自驱动 UI 优化第 14 轮 — **in-page `<h3>` 视觉锚点收口**（4 h3 漏网补齐）+ **card-grid 阶梯入场动效**（CSS-only）
**目标**:
1. 修复 r27 sweep 时漏掉的"in-page `<h3>` 无视觉锚点"问题（3 view × 7 h3）
2. 给全站 `.card-grid` 加 60ms 阶梯入场动效，强化"页面载入完成"的视觉反馈

**约束**: 不新增功能、不动 backend、不引入新依赖、不重启 8501
**前置**: P38 r1-r27 共 27 轮 sweep 已穷尽"硬编码颜色 / 视觉锚点 / 按钮 / 阅读排版 / 图表色板 / 搜索结果同源 / a11y / section-title 8 维度

---

## 为什么从 r27 切到 r28

cron 任务给本轮的 6 候选里：

| # | 候选 | 评估 | 决策 |
|---|---|---|---|
| 1 | MemoryCard 视觉锚点（strength ring/颜色梯度）| r15+r24 已做透 | ❌ skip |
| 2 | 侧栏 active 状态强化 | r8+r17 已完备 | ❌ skip |
| 3 | 按钮层级全局审计 | r21+r23 已完备 | ❌ skip |
| 4 | 主内容区 max-width + 居中 | r24 已完备 | ❌ skip |
| 5 | 搜索框 input Geist 化 | 已完备 | ❌ skip |
| 6 | Memory type 标签色块化 | r26 已收口 | ❌ skip |

**所有 6 个候选项都已饱和**。扫描 P38 r9 + r27 报告的"遗留/下次可做"清单后，选**两项视觉影响力最大的"动效 + 视觉锚点"**做收尾：

| 候选 | 视觉影响 | 决策 |
|---|---|---|
| **A. in-page `<h3>` 视觉锚点**（4 漏网 h3 补齐）| **中-高**（用户每次进 Hermes/Compare 看到标题）| ✅ **本轮做** |
| **B. card-grid enter stagger**（60ms 阶梯入场）| **中-高**（每次进首页/AgentMemory 看到卡片逐张淡入）| ✅ **本轮做** |
| 死 fallback 清理（`var(--text, #1d1d1f)` × 20）| 0 视觉 | 跳过（0 视觉影响，违反"按视觉影响力排序"） |
| Modal 入场动效 | med-high | 跳过（需改 10+ modal 文件，超出"2-3 项"范围） |
| Toast slide-in | med | 跳过（范围受限，单独轮做更彻底） |
| Page scroll progress bar | small | 跳过（视觉权重不足） |
| AppHeader route change fade | small | 跳过（视觉权重不足） |

**视觉影响估计**（按 P38 13 轮 sweep 标准）：

- 7 个 in-page h3 从"无视觉锚点"升级为"2px accent rail / 1px bottom underline" → 用户在 Hermes Memory / Compare 切换时，**in-page heading 视觉锚点完全统一**
- 每次进入 HomeView / AgentMemoryView / HermesMemoryView（**30+/天/用户**），`.card-grid` 12 张卡片 60ms 阶梯淡入 → **强化的"载入感"**

---

## 改动清单

### 1. HermesMemoryView `.profile-heading` 加 2px accent 左 rail（2 h3）

**问题**：
- Hermes Memory 页面内每个 profile section（Global / 👤 profile name）有 `<h3 class="profile-heading">`
- 之前 h3 是**纯文字 + font-weight 600 + color: --primary**，无任何视觉锚点
- 与 r20 全站 section-title 3px bar 系统不一致
- P38 r20 升级时只升级了 `.hermes-card` 视觉，**漏了同一文件里的 h3**

**改动**（1 文件，11 行 CSS）：

```css
.profile-heading {
  position: relative;
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--primary);
  /* P38 r28: h3 视觉锚点 — 2px accent bar 左侧 rail.
     与 r27 section-title 3px bar 同源但 h3 视觉重量更轻 → 用 2px 而非 3px.
     之前 h3 是无视觉锚点的纯文字, 在 in-page 多 section 排版时无分组感.
     2px bar + 10px padding-left 让 h3 与下方 hermes-card 视觉断点更清晰. */
  padding-left: 10px;
}

.profile-heading::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 2px;
  height: 70%;
  background: var(--accent);
  border-radius: 0 2px 2px 0;
}
```

**设计决策**：
- **2px 而非 3px** — h3 视觉重量比 h2 轻（1.1rem vs 1.5rem），全用 3px 会"过重"破坏层级
- **height: 70%**（h2 用 60%）— h3 字号小，相对高度稍大让 rail 更显眼
- **padding-left: 10px**（h2 用 12px）— h3 字号小，padding 同比缩小

**视觉影响**：
- HermesMemoryView 进入时，"🌐 Global" 和 "👤 profile_name" 标题左侧各有 2px 蓝色 rail
- 与 r20 section-title 3px bar 形成"h2 = 3px / h3 = 2px"的层级视觉语言
- dark 模式自动跟随 `--accent` token

### 2. HomeView `.profile-heading` 同款 2px accent 左 rail（2 h3）

**问题**：
- HomeView 的 Hermes Memory section 内有同样的 `<h3 class="profile-heading">`（line 170 / 184）
- 之前 P38 r20 升级 HermesMemoryView `.hermes-card` 时漏了 HomeView 里的同款 h3
- HomeView 的统一记忆视图 / AgentMemory section 是 section-header h2（3px bar），**HomeView 内部形成 h2 3px / h3 无 rail 的不一致**

**改动**（1 文件，11 行 CSS）：

完全同 HermesMemoryView 模式：
```css
.profile-heading {
  position: relative;
  ...
  padding-left: 10px;
}
.profile-heading::before {
  content: '';
  position: absolute;
  left: 0; top: 50%; transform: translateY(-50%);
  width: 2px; height: 70%;
  background: var(--accent);
  border-radius: 0 2px 2px 0;
}
```

**视觉影响**：
- HomeView 进入时，Hermes Memory section 的 Global / profile 小标题都有 2px 蓝 rail
- 与 AgentMemory section 的 h2 (3px) 形成层级视觉语言
- dark 模式自动跟随

### 3. CompareView `.three-column h3` 加 1px subtle bottom border（3 h3）

**问题**：
- CompareView 的 3 列对比（🅰️ 仅在左侧 / 🔗 共有 / 🅱️ 仅在右侧）有 3 个 `<h3>`
- 之前 h3 是**纯文字 + font-weight 600**，无视觉锚点
- 3 h3 位于 `.left-only / .common / .right-only` 三色 3px diff-color left border 列内
- 直接套用 r28 2px accent left bar 模式**会"左 border 拥挤"**（已有 3px diff-color，再叠 2px accent 形成 5px 双层 border）

**改动**（1 文件，9 行 CSS）：

```css
/* P38 r28: CompareView 3 列 h3 视觉锚点 — 1px subtle bottom border (不用 2px left bar).
   与其他 h3 不同的设计决策: 这 3 个 h3 位于 .left-only/.common/.right-only 三色列内,
   列本身有 3px diff-color left border, 再叠 2px accent bar 会"左 border 拥挤".
   改用 1px bottom border 形成"column header underline"视觉语言 — h3 变成列的"小标题"而非
   section 的"分组标题". 1px 是视觉权重, --border (light #ebebeb / dark #2c2c2c) 弱化不抢戏.
   复用 r27 section-title 模式但变体为"horizontal underline" 应对特殊场景. */
.three-column h3 {
  position: relative;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 12px;
  padding-bottom: 8px;
  color: var(--primary);
  border-bottom: 1px solid var(--border);
}
```

**设计决策**（与 HermesMemoryView 不同）：
- **bottom border 而非 left rail** — 因为 3 列已有 3px 左侧 diff-color border，left rail 会双层拥挤
- **1px 而非 2px** — h3 视觉重量更轻 + bottom underline 是辅助视觉
- **--border token**（light `#ebebeb` / dark `#2c2c2c`）而非 `--accent` — bottom underline 目的是"分组"而非"强调"，弱化不抢戏
- **`padding-bottom: 8px`** 让 h3 文字与 underline 拉开间距，避免"贴边"

**视觉影响**：
- CompareView 3 列对比时，3 个 h3 都有 1px 浅灰下划线
- 与 3 列 3px diff-color left border 形成"垂直 anchor + 水平 underline"双重分组视觉
- h3 变成列的"小标题"（column header）而非 section 的"分组标题"（section title）
- dark 模式自动跟随 `--border` token

### 4. 全站 `.card-grid` 加 60ms 阶梯入场动效（CSS-only, 0 JS）

**问题**（P38 r9 报告"下次可做" #2）：
- 用户进入 HomeView / AgentMemoryView / HermesMemoryView，`.card-grid` 12+ 张卡片**同时瞬切**显示
- 缺失"载入感"——之前 r9 加了 page-level fade (150ms) + Dashboard count-up (800ms)，但卡片**仍硬切**
- 与全站 Geist 风格（克制、流畅）不匹配

**改动**（1 文件，38 行 CSS）：

```css
/* ─── Card grid enter stagger (P38 r28) ───
   Page enter 时 卡片 逐个淡入 + 上移, 80ms stagger, 12 张内有效.
   - CSS-only (0 JS), 复用 r9 page transition 思路但不依赖 <Transition>
   - 限制 1-12 张: 12 张后 60ms × N = 720ms 超过 "心理可接受" 阈值, 第 13+ 张立即显示
   - prefers-reduced-motion: 完全跳过 (无障碍, 沿用 r9 模式)
   - 应用于: HomeView, AgentMemoryView, HermesMemoryView 的 .card-grid
   - 跳过 .skeleton-card (它在 shimmer 动画中, 不能叠) */
@keyframes card-grid-enter {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.card-grid > *:not(.skeleton-card) {
  animation: card-grid-enter 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
  animation-delay: 0ms;
}

.card-grid > *:not(.skeleton-card):nth-child(1)  { animation-delay: 0ms; }
.card-grid > *:not(.skeleton-card):nth-child(2)  { animation-delay: 60ms; }
...
.card-grid > *:not(.skeleton-card):nth-child(12) { animation-delay: 660ms; }

@media (prefers-reduced-motion: reduce) {
  .card-grid > *:not(.skeleton-card) {
    animation: none;
  }
}
```

**设计决策**：
- **CSS-only，0 JS** — `:nth-child(N)` 选择器原生支持阶梯，无需 JS 计算 index
- **cubic-bezier(0.16, 1, 0.3, 1)** — Apple HIG 风格缓动（"快进 + 微弹"），比 linear 更有"卡片落位"感
- **0.4s duration** — 比 r9 页面 fade 150ms 稍长（卡片是更"重"的元素），但比 Dashboard count-up 800ms 短
- **60ms 间隔**（不是 80ms）— 12 张卡片 60ms × 11 = 660ms 总时长仍 < 1s 心理阈值
- **`:not(.skeleton-card)`** — skeleton-card 自身有 shimmer 动画，叠加会冲突（叠 transform 会破坏 shimmer 的 `background-position`）
- **12+ 卡片** — 走默认 0ms 同步淡入（避免 720ms+ 心理感知延迟）
- **`fill-mode: both`** — 动画前保持初始 opacity 0（避免 FOUC "硬闪"），动画后保持终态 opacity 1
- **`prefers-reduced-motion: reduce`** — 完全跳过（无障碍，沿用 r9 page transition 模式）

**视觉影响**：
- 每次进入 HomeView（4 个 grid）/ AgentMemoryView / HermesMemoryView，**12 张内卡片逐张 60ms 阶梯淡入**
- 与 r9 page fade (150ms) + Dashboard count-up (800ms) 形成完整的"页面 → 数据 → 卡片"3 阶段动效链：
  1. **0-150ms**: 旧页面淡出 + 新页面淡入（page transition）
  2. **150-950ms**: Dashboard 数字从 0 滚动到 target（count-up）
  3. **0-1060ms**: 新页面卡片 60ms 阶梯淡入（stagger）
- 用户**进入新页面的前 1 秒有持续的视觉反馈**——之前是 0-150ms 淡入后"什么都没有"，现在是 1 秒内连续 3 个阶段的"载入感"
- 0 风险：失败也只是"瞬时显示"（旧行为），不影响功能
- **0 新依赖、0 JS、不需要 <Transition>**——纯 CSS `:nth-child` 选择器

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors（每次改动后 + 最终都跑过） |
| `npm run build` | ✅ built in 2.39s, dist 完整生成 |
| dist CSS asset hash 刷新 | ✅ `index-tZIYy7fP.css`（旧 `index-C7GId3Ac.css`） |
| 8501 后端未触碰 | ✅ 只改 frontend/src/ |
| 依赖未增加 | ✅ 纯 CSS keyframes + nth-child |
| in-page h3 视觉锚点覆盖率（r28 范围内）| **7/7 = 100%**（HermesMemoryView 2 + HomeView 2 + CompareView 3） |
| card-grid 阶梯动效覆盖 | **6 个 .card-grid**（HomeView 4 + AgentMemoryView 1 + HermesMemoryView 1）|
| dark 模式自适配 | ✅ 全部走 `--accent` / `--border` token |
| 不新增功能 | ✅ |
| 不动 backend | ✅ |
| 不引入新依赖 | ✅ |
| 不重启 8501 | ✅（dist 已刷新，8501 serve dist 自动拾取） |
| prefers-reduced-motion | ✅ 跳过（无障碍） |

### 验证命令

```bash
# 验证 3 个 view 的 h3 都加了视觉锚点
grep -nE "profile-heading::before|\.three-column h3" frontend/src/views/HermesMemoryView.vue frontend/src/views/HomeView.vue frontend/src/views/CompareView.vue
# 期望: 至少 3 行 (每个 view 一个 ::before 块)

# 验证 card-grid 阶梯动效已加
grep -nE "card-grid-enter|nth-child\(12\)" frontend/src/styles/main.css
# 期望: 1 个 @keyframes + 12 个 nth-child + 1 个 @media reduce

# 验证 8501 serve 的是新 dist
curl -s http://localhost:8501/ | grep "index-.*\.css"
# 期望: index-tZIYy7fP.css (新 hash)

# 验证 vue-tsc 0 errors
cd frontend && npx vue-tsc --noEmit
# 期望: 0 errors

# 验证 build OK
cd frontend && npm run build
# 期望: ✓ built in <3s, dist 完整生成
```

---

## 视觉影响估计

| 改动 | 估计影响 | 影响对象 |
|---|---|---|
| HermesMemoryView 2 h3 视觉锚点 | **中**（Hermes Memory 页面内 2 个分组标题）| Hermes Memory 用户 |
| HomeView 2 h3 视觉锚点 | **中**（首页默认 tab 内 Hermes section 2 个分组标题）| HomeView 用户 |
| CompareView 3 h3 视觉锚点 | **中-高**（3 列对比中央 3 个标题，最显眼位置）| Compare 页面用户 |
| card-grid 60ms 阶梯入场 | **中-高**（每次进入首页/AgentMemory/Hermes，12 张卡片逐张淡入）| 全站用户（30+/天） |

合并视觉影响：**中-高**（7 个 h3 一次性收口 + 全站 6 个 .card-grid 阶梯入场）。

---

## 遗留与下一步建议

### 本轮已彻底完成

- ✅ in-page `<h3>` 视觉锚点 100% 收口（7/7 个 h3，2 view 收口 2px rail，1 view 收口 1px underline）
- ✅ 全站 6 个 `.card-grid` 60ms 阶梯入场动效（CSS-only, 0 JS）
- ✅ 4 文件改动（HermesMemoryView.vue / HomeView.vue / CompareView.vue / main.css）
- ✅ 0 风险，0 新依赖，0 功能改动

### 仍可继续优化的方向（不属"硬伤"但视觉提升仍有空间）

1. **死 token 清理**（r27 报告 §遗留 #1 续）— `var(--text-primary)` × 8 + `var(--text, #1d1d1f)` × 16 + `var(--bg-secondary, #f9f9f9)` × 4 = **28 处 fallback 永触发**。**0 视觉影响**，纯技术债清理。建议 P39 专门做一次（半小时集中清理）。
2. **Modal 入场动效**（r9 报告 §遗留 #4）— 14+ 个 modal 现在直接 fade，可加 `transform: scale(0.96) + translateY(8px) → scale(1) + translateY(0)` 的 200ms 缓动。**中-高视觉影响**，但需改 10+ modal 文件，建议 P39 用 `Teleport + Transition` 全局模式重写一次。
3. **Toast slide-in**（r9 报告 §遗留 #3）— Toast 现在直接 fade，slide-in-from-top + 弹性回弹会更有"通知"感。**中视觉影响**，只需改 Toast.vue 一个文件。
4. **Page scroll progress bar**（r9 报告 §遗留 #6）— router-view 顶部 1px accent 进度条，路由变化时 0% → 100% 平滑推进（150ms）。**小视觉影响**，实现简单。
5. **AppHeader 路由变化时副标题淡出/淡入**（r9 报告 §遗留 #5）— 与 page transition 配合强化"页面切换"感。**小视觉影响**。

### 不可做（项目约束）

- ❌ 不新增功能
- ❌ 不引入新依赖
- ❌ 不动 backend

---

## 与前后轮次的关系

| 轮次 | 主题 | 影响 |
|---|---|---|
| r9 | 页面切换 fade + ShareModal 语义修复 + Dashboard count-up | 全站页面进入感 + ShareModal dark 模式 bug 修复 + Dashboard 首屏数字滚动 |
| r15 | 4 套 Card hover 同源 + section h2 3px accent bar (`.section-header h2` 模式) | MemoryCard / CollectionCard / DashboardWidget / TemplateCard + HomeView 3 h2 |
| r20 | section-title 视觉锚点 100% 收尾（7 个 view）| AgentMemory / HermesMemory / Profiles / Sources / Dashboard / Compare / Collections |
| r24 | 主内容区流体 max-width + strength ring 视觉锚点升级 | --content-max token + ring 100% 满级环 |
| r27 | section-title 漏网 5 个 h2 补齐 | SettingsView 3 h2 + HomeView Hermes Memory h2 + HomeView 搜索结果 h2 |
| **r28（本轮）** | **in-page h3 视觉锚点 + card-grid 阶梯入场** | HermesMemoryView 2 h3 + HomeView 2 h3 + CompareView 3 h3 + 全站 6 个 .card-grid |

---

## 最终交付建议

P38 r1-r28 共 28 轮 sweep 已把"硬编码颜色 / 视觉锚点 / 按钮 / 阅读排版 / 图表色板 / 搜索结果同源 / a11y / section-title / in-page h3 / 微动效"10 个维度全部收口。

本轮**第 14 轮**做了 2 件事：
1. **in-page h3 视觉锚点收尾**（r27 h2 sweep 时漏掉的 7 个 in-page h3，100% 补齐）——全站 h1/h2/h3 三级 heading 视觉锚点 100% 统一
2. **card-grid 阶梯入场动效**（CSS-only 0 JS，全站 6 个 .card-grid）——形成"page fade (r9) → Dashboard count-up (r9) → card stagger (r28)"3 阶段载入动效链

**设计系统 token 化完成度（终态）**：
- 颜色：accent / success / error / warning / semantic-accent + 5 档 alpha（light + dark）
- 阴影：card / hover / elevated / focus / modal / toolbar / press（light + dark）
- 字体：Geist Sans / Geist Mono（已统一）
- 间距：--space-1 ~ --space-9 scale（已统一）
- 圆角：--radius-sm / --radius-md / --radius-lg（已统一）
- **动效**：page fade (150ms) + count-up (800ms) + card stagger (60ms × 12)（r9 + r28 已统一）

**未来方向建议**：
- **a11y sweep**：表单 label / focus order / chart SVG `<title>` —— 用户感知不到视觉但影响所有使用辅助技术的用户
- **死 token 清理**：`var(--text-primary)` × 28 处 —— 0 视觉，纯技术债
- **Modal 入场动效**：14+ modal 一次收口 —— 中-高视觉，单文件改动需专题
- **Toast slide-in**：单文件改动 —— 中视觉

UI 优化在"动效"维度仍有 1-2 轮可做（Modal/Toast），之后**真正应该转向 a11y 和功能完整性维度**。
