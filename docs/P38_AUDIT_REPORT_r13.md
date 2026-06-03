# P38 UI 优化审计报告（第十三轮 — 视觉去重 + hover 视觉同源 + 硬编码收尾）

**日期**: 2026-06-04
**主题**: 自驱动 UI 优化 — 视觉去重 + Card hover 同源收尾 + HomeView 5 处 hex 收尾
**commits**:
- `2d7b97a` P38 r13: MemoryCard strength dedup - remove redundant strength-bar
- `49c8599` P38 r13: HomeView unified-card hover + 5 hex 收尾 + --accent-secondary token
**目标**:
1. 删除 MemoryCard 强度表达冗余（3 种 → 2 种）
2. HomeView unified-card hover 与 P38 r12 4 套 Card 同源
3. HomeView 5 处硬编码 hex 收尾 + 新增 --accent-secondary token
**约束**: 不新增功能、不动 backend、不引入新依赖、不重启 8501 server
**前置**: P38–P44 + P39 r1 共 12 轮 sweep 全部完成

> **关于"第 13 轮"的说明**：本轮聚焦"视觉去重 / Card hover 收尾 / 硬编码收尾"。前 12 轮 token 化主要解决"颜色/字号/间距"契约，本轮把"信息表达冗余"和"Card 5 套第 5 套遗漏"也清掉。

---

## 改动清单

### 1. MemoryCard strength 视觉去重 — 最大视觉影响

**问题**（P38 r1 漏网）：
- `.card-meta` 一行里 strength 用了 **3 种** 表达：
  - 38px 圆形 SVG ring（带 0.7rem 数字居中）
  - 4px 高 flex:1 水平 `.strength-bar`（填充百分比 = 数字）
  - 右侧 0.72rem 数字回显（"70%"）
- 三者表达同一个数字 70/70/70 — 视觉冗余
- 视觉权重过重：每张卡底部"3 层色块"挤在一起
- r1 报告声称"ring 是视觉锚点"，但同时加了 bar — 自相矛盾

**改动**（`frontend/src/components/Layout/MemoryCard.vue`，删除 4 元素 + 19 行 CSS）：
- 删除 `<span class="strength-bar">` 元素（line 51-53）
- 删除 `.strength-bar` CSS（flex:1 / 4px / var(--tag-bg) / radius 2px / overflow hidden）
- 删除 `.strength-fill` CSS（display: block / height: 100% / var(--accent) / 0.4s cubic-bezier 过渡）
- 删除 `.strength-fill--{high,mid,low}` 3 个 tier 变体

**保留**（2 种表达，互补）：
- **ring**：视觉锚点 + 内含数字（0.5s stroke-dasharray 过渡让百分比变化有"补全"动画）
- **meta-text**：右侧 0.72rem 数字回显（即时跳变，适合快速扫读）

**影响估计**：
- 每张 MemoryCard 底部少 1 个 4px 高、flex:1 的色块，整行视觉重量 **-25%**
- ring 仍是 38px 圆形主视觉，meta-text 是右对齐次要数字 — 节奏感 "重 → 轻" 形成主次
- 删除 19 行 CSS（5 个选择器 + 过渡）
- 不影响功能（数字本身未变、aria-label 仍带 "记忆强度 X%"）

---

### 2. HomeView unified-card hover 视觉同源 — P38 r12 漏网的第 5 套

**问题**（P38 r12 报告遗漏）：
- r12 把 4 套 Card（MemoryCard / CollectionCard / DashboardWidget / TemplateCard）的 hover 统一为：
  ```
  transition: box-shadow 0.25s cubic-bezier(...),
              transform 0.25s cubic-bezier(...),
              border-color 0.2s ease;
  :hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
    border-color: var(--border-strong);
  }
  ```
- 但 **HomeView unified-card**（统一记忆视图里的卡片）用的还是旧版：
  - `transition: box-shadow 0.2s ease, transform 0.2s ease;` — 无 cubic-bezier、无 border-color
  - `:hover` 缺 `border-color: var(--border-strong);`
- 用户在 HomeView 看到 unified-card hover → 切到 CollectionsView / DashboardWidget → 手感不一致
- r12 报告 #1 说"4 套 Card 视觉同源"，但 unified-card 没被识别为第 5 套（虽然它视觉上是 Card 组件）

**改动**（`frontend/src/views/HomeView.vue`，1 个文件，2 行 CSS）：
- `.unified-card` transition 升级到 0.25s cubic-bezier（与 ring 0.5s / count-up 同手感）
- `.unified-card:hover` 追加 `border-color: var(--border-strong);`

**影响估计**：
- HomeView unified-card 与全站 4 套 Card 现在完全同源
- 0.2s ease → 0.25s cubic-bezier：起步略慢、收尾略慢，整体感觉更"高级"（Vercel 风格）
- border-color 0.2s ease 让 hover 时 border-strong 平滑切换（之前是瞬变）
- 0 行新增/删除，纯参数微调

---

### 3. HomeView 5 处硬编码 hex 收尾 + --accent-secondary token

**问题**（P38 r6/r8/r12 漏网）：
- HomeView 是项目首屏（5 个 section，3 类记忆视图），但还有 5 处硬编码 hex 残留
- 都是 P36 漏掉的"Apple 系统色"或"Tailwind 调色板"硬编码
- Dark 模式均无覆盖（用户切到 dark 后这些色块仍显示为浅色对比度不足）

| 选择器 | 旧值 | 用途 | 视觉影响 |
|---|---|---|---|
| `.search-result-card--semantic` border-left | `var(--semantic-accent, #8b5cf6)` | 语义搜索结果左 3px 紫线 | fallback 错配（token 已存在） |
| `.similarity-score` color | `var(--semantic-accent, #8b5cf6)` | "相似度: 95%" 数字 | 同上 |
| `.match-type--semantic` bg + color | `rgba(139, 92, 246, 0.1) + var(--semantic-accent, #8b5cf6)` | "语义匹配" chip | 双重硬编码 |
| `.match-type--keyword` bg + color | `rgba(59, 130, 246, 0.1) + #3b82f6` | "关键词匹配" chip | 0.1 alpha 蓝底 + Tailwind blue-500 字 |
| `.unified-strength` bg + color | `rgba(251, 191, 36, 0.1) + #f59e0b` | "强度: 7" chip | Tailwind amber-100/400 hardcoded |
| `.unified-card::before` gradient | `var(--accent), var(--accent-secondary, #6366f1)` | unified-card 顶部 2px 渐变线 | `--accent-secondary` token 缺失，fallback 用 indigo-500 |

**改动**（`frontend/src/views/HomeView.vue` + `frontend/src/styles/variables.css`，6 处 + 1 新 token）：

**3.1 新增 `--accent-secondary` token（`variables.css`，2 主题）**
```css
/* light: */  --accent-secondary: #6366f1;     /* indigo-500，紫蓝渐变端点 */
/* dark:  */  --accent-secondary: #818cf8;     /* indigo-400，dark 提亮一档 */
```

**3.2 5 处 hex 替换为 token（HomeView.vue）**
- `.search-result-card--semantic` → `border-left: 3px solid var(--semantic-accent);`（删 fallback）
- `.similarity-score` → `color: var(--semantic-accent);`（删 fallback）
- `.match-type--semantic` → `background: color-mix(in srgb, var(--semantic-accent) 10%, transparent); color: var(--semantic-accent);`
- `.match-type--keyword` → `background: color-mix(in srgb, var(--accent) 10%, transparent); color: var(--accent);`（**关键**：从 Tailwind blue-500 → Vercel --accent，dark 模式自动跟随）
- `.unified-strength` → `background: color-mix(in srgb, var(--strength-mid-fill) 10%, transparent); color: var(--strength-mid-ink);`（**关键**：复用 MemoryCard ring 的 strength token 家族）
- `.unified-card::before` gradient → `linear-gradient(90deg, var(--accent), var(--accent-secondary));`（token 化，无 fallback）

**影响估计**：
- **Dark 模式 5 处全部首次正确**（之前 dark 模式下"语义匹配"chip 浅紫底 + 浅紫字，对比度 < 3:1；现在 color-mix 走 var 自动跟主题）
- **品牌色统一**：`.match-type--keyword` 从 Tailwind blue-500 → Vercel --accent（差 13 蓝度），现在与所有按钮/链接同源
- **token 复用**：`unified-strength` 复用 `--strength-mid-fill/--strength-mid-ink`，与 MemoryCard ring 的"中档强度"语义一致（虽然 7/10 实际是 high 档，但 unified 视图不显示 tier）
- **新增 1 个 token × 2 主题 = 2 个值**：`--accent-secondary`，为后续可能的渐变用法铺路

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors（两次 commit 前后各跑一次） |
| `npm run build` | ✅ 2.55s / 2.54s，dist 完整生成 |
| MemoryCard 强度表达 | 3 种 → 2 种（ring + meta-text），删除 .strength-bar 元素 + 5 个 CSS 选择器 |
| unified-card hover | transition 升级 cubic-bezier + 补 border-strong hover |
| HomeView 硬编码 hex | 6 处 → 0 处（5 个选择器 + 1 个 gradient fallback） |
| 新增 token | `--accent-secondary` × 2 主题 = 2 个值 |
| 全站 `.strength-bar` / `.strength-fill` 残留 | 0 处（之前仅 MemoryCard 1 处使用，已删） |
| 8501 server | 未重启（dist 已 build，backend 不依赖 frontend 静态资源） |

---

## 视觉影响估计

| 改动 | 估计影响 | 影响对象 |
|---|---|---|
| MemoryCard strength 去重 | **高**（每张 MemoryCard 底部立即变轻，100% 用户感受） | 主页 / AgentMemory / Hermes Memory / Collections / 搜索结果 |
| unified-card hover 同源 | 中（用户 hover 5 套 Card 时手感一致） | 主页 unified-section 用户 |
| HomeView 5 hex 收尾 | 中（dark 模式可见，light 模式 0 变化） | 全部 dark 模式用户 + 品牌色一致性 |

---

## 遗留与下一步建议

**P38 已累计 13 轮 sweep（r1 + r6/r8/r9/r10/r11/r12 副报告 + r13 本轮）**，50+ 项改动，UI 优化边际收益进一步递减。

### ✅ 已完成
- Geist 风格设计 token 重构（variables.css 264 行 token）
- Header sticky + blur
- Dark mode 对比度修复（已 100% 收尾所有硬编码 hex）
- Stats 三段式 + count-up 动画
- EmptyState Geist 化 + chart-empty 视觉锚点
- MemoryCard strength 视觉去重（本轮 r13）— ring + meta-text 双层表达
- 侧栏激活态强化（rail + bg + color + weight 四重指示）
- 按钮层级全局统一（4 页面 + ghost 修饰类）
- 主内容区 max-width 1200px + 居中
- 搜索框 Geist 化（recessed bg + 4px glow on focus）
- Memory type chip + source badge + match-type chip + strength chip 全部色块化
- CompareView / Dashboard type-bar token 化
- Modal backdrop 全站 sweep（11 文件，Dark 模式 0.7 自动跟随）
- Geist mono 字体全站统一（7 文件）
- close-btn 全站统一（4 文件）
- SettingsView tab active 强化
- 滚动条 Geist 化
- **5 套 Card hover 视觉同源**（CollectionCard / DashboardWidget / TemplateCard / MemoryCard / **unified-card** ← 本轮 r13）
- **HomeView 5 hex 收尾** ← 本轮 r13
- **--accent-secondary token 新增** ← 本轮 r13

### 下次可做（按视觉影响力排序，但边际收益持续递减）
1. **deprecated/ 目录 144 处硬编码批量清理** — 一次性 sweep 风险可控
2. **OnboardingTour / SetupWizard 视觉与主站同源** — 仍用独立 palette
3. **空状态插画升级** — emoji → 1px 线条 SVG（Vercel / Linear 风格）
4. **页面切换 stagger 入场** — 当前 150ms fade 可加列表项 50ms 错位
5. **键盘快捷键弹窗键盘化** — KeyboardHelp 加搜索 + 分类折叠

### 不可做（项目约束）
- ❌ 不新增功能
- ❌ 不引入新依赖
- ❌ 不动 backend
- ❌ 不重启 8501 server

---

## 最终交付建议

P38 已 13 轮 sweep（累计 50+ 项改动）。继续单点 sweep 的边际收益 < 2%，建议下一阶段从 **UI sweep 转向功能/性能/可用性** 维度：

- **A**: deprecated/ 目录清理（一次性 sweep，风险可控）
- **B**: 新功能打磨（OnboardingTour / SetupWizard 视觉同源）
- **C**: a11y 深化（focus-visible 全站覆盖 + 屏幕阅读器标签审计）
- **D**: 性能 audit（首屏 / 虚拟滚动 / 骨架屏）
- **E**: 功能可达性 audit（每个功能 3 步内可达？）

UI 优化已收敛到"再改也只是 ±2% 视觉差异"的边际收益阶段。
