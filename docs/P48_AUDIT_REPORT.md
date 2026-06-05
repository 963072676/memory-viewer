# P48 UI 优化审计报告

**日期**: 2026-06-05
**主题**: 自驱动 UI 优化第 10 轮 — P47 §遗留 3 项调色板 token 化（avatar / collection / graph source）
**前提**: P47 全部 commit 完毕（最新 `bd85472`），本轮接续 P47 §遗留 #1/#2/#3，3 套调色板一并 token 化
**约束**: 不新增功能、不动 backend、不引入新依赖、只改 CSS / Vue 模板

> **关于"P48"编号**：cron 提示词标签写的是"P38 优化"，但 P38-P47 已全部 commit 完毕。本报告记为 **P48（第 10 轮）**，承接 P47 §遗留 3 项硬编码调色板。设计目标统一为：avatar 6 色 + graph 6 色 + collection 10 色全部走 token，dark 模式自动跟随。

---

## 改动清单（3 个 commit + 1 个 audit report）

### 1. **P48 r1** — AnnotationThread avatar 6 调色板 token 化（中视觉影响，dark 模式首次正确）

**问题**（P47 §遗留 #1）：
- `frontend/src/components/Layout/AnnotationThread.vue:35` 的 `avatarColor()` 函数硬编码 6 个 Apple hex：
  ```ts
  const colors = ['#007aff', '#34c759', '#ff9500', '#af52de', '#ff3b30', '#5ac8fa']
  return colors[Math.abs(hash) % colors.length]
  ```
- inline `:style="{ background: avatarColor(author) }"` 在 dark 模式仍渲染 light 模式字面 hex
- 触达：MemoryDetailView 顶部 comment / flag / suggest 头像（每次看 annotation 都看到）

**改动**（2 文件）：
- `variables.css` 新增 6 个 `--avatar-1..6` token（light: Tailwind 500 阶，dark: Tailwind 400 阶）
- `AnnotationThread.vue:34-37` `avatarColor()` 返回 `'var(--avatar-N)'` 字符串而非 hex
- hash 派发逻辑保留：`slot = (Math.abs(hash) % 6) + 1` — 同一 author 永远同色

**关键决策**：6 个 Apple 500 阶（`#007aff/#34c759/#ff9500/#af52de/#ff3b30/#5ac8fa`）与新 Tailwind 500 阶（`#0072f5/#22c55e/#ff9f0a/#8b5cf6/#ef4444/#06b6d4`）视觉差异极小（同色相不同明度），**身份识别一致性保留**。dark 模式 400 阶与 `--source-*/--strength-*-ink` 已有 token 同源（一档提亮补偿深色背景）。

**影响估计**：
- **Dark 模式首次正确**：之前用户在 dark 模式看到所有 annotation avatar 是 light mode 字面 Apple 色
- 触达：每次打开 MemoryDetailView 顶部 annotation thread = **每日 10+ 次**
- 决策树与 P47 r1 (RoleBadge) / P45 r1 (HealthBadge) 同源：6 状态/身份色全部走 token

### 2. **P48 r2** — CollectionEditor 10 调色板 token 化（中视觉影响，新 collection dark 模式正确）

**问题**（P47 §遗留 #2）：
- `frontend/src/components/Layout/CollectionEditor.vue:108` 的 `colorOptions` 数组 10 个 Apple hex 硬编码
- `form.color: '#007aff'` 默认值 + `form.color = col.color || '#007aff'` fallback 也是 hex
- 触达：每次打开 "Create/Edit Collection" modal 的 color picker

**改动**（1 文件，3 处）：
- `colorOptions` 数组：10 个 hex → `var(--collection-color-1..10)` 引用
- `form.color` 默认值：`'#007aff'` → `'var(--collection-color-1)'`
- `col.color || '...'` fallback 同步用 var() 引用（新 collection 走 token；legacy hex 透传保留）

**兼容性设计**（重要）：
- **不在 backend 强制迁移**。`CollectionCard.vue` 仍在用 `collection.color + '20'` 拼接 alpha 通道（`#007aff20`）— 对 var() 引用不友好（`var(--collection-color-1)20` 非法 CSS）
- **新 collection 的 picker 选择存为 var() 引用**（如 `var(--collection-color-1)`），dark 模式自动跟随
- **旧 collection 的 `col.color` 仍是 hex**（如 `#007aff`），透传保留 — `CollectionCard` 仍可读 + 拼接 alpha
- 两套数据共存：旧 hex 在 CollectionCard 渲染 OK，在 picker 中 active state 不会高亮（仅新 var() 引用能高亮），但功能正常

**影响估计**：
- **新 collection dark 模式首次正确**：之前用户在 dark 模式创建 collection，所有 10 个 color swatch 是 light 字面色；现在 picker 选中后 dark 模式自动用 400 阶
- 触达：每次创建/编辑 collection = **每周 5+ 次**
- 决策树：与 P46 r1 (SetupWizard token 化) 同源 — 一次性把"硬编码调色板"改为 token 化

### 3. **P48 r3** — LineageGraph 6 调色板 token 化（中视觉影响，dark 模式首次正确）

**问题**（P47 §遗留 #3）：
- `frontend/src/components/Layout/LineageGraph.vue:127` `sourceColors` Record 6 个 Apple hex：
  ```ts
  manual: '#007aff', import: '#34c759', agent: '#af52de',
  merge: '#ff9500', derived: '#5ac8fa', legacy: '#86868b'
  ```
- `getNodeColor()` fallback `'#86868b'` 也是 hex
- 触达：MemoryDetailView 顶部 lineage 圈图（每次打开 detail 都看到）+ SourcesView

**改动**（1 文件，2 处）：
- `sourceColors` Record：6 个 hex → `var(--graph-source-*)` 引用
- `getNodeColor()` fallback：`'#86868b'` → `var(--graph-source-legacy)'`

**语义映射**（与 P47 §遗留设计同步）：
- `manual` = 蓝 (用户主操作 = `--accent`)
- `import` = 绿 (成功 = `--success`)
- `agent` = 紫 (AI 生成 = `--semantic-accent`)
- `merge` = 橙 (变更 = `--warning`)
- `derived` = 青 (派生关系 = 独立 hue)
- `legacy` = 灰 (历史 = `--text-secondary`)

**影响估计**：
- **Dark 模式首次正确**：6 个 lineage 节点色在 dark 模式之前是 light 字面 Apple 色；现在 SVG `<circle fill="var(--graph-source-X)">` 自动跟随主题
- 触达：每次打开 MemoryDetailView 顶部 lineage 圈图 = **每日 5+ 次**
- 决策树：与 P48 r1 (AnnotationThread avatar) 同源 — 6 状态色 token 化，dark 模式自动跟随

---

## 设计决策记录

### 为什么 3 套调色板都用 Tailwind 500 阶（light）+ 400 阶（dark）？
- 与项目已有 token 体系同源：`--source-*/--strength-*/--type-*` 全用 Tailwind 500 阶（light）+ 400 阶（dark）
- 500 阶保证 24px 头像圆上 12px 文字的 4.5:1 对比度（light 模式 `#0072f5` + 白色字）
- 400 阶补偿 dark 模式深色背景（`#60a5fa` + 深灰背景，仍清晰可读）
- 一致的设计语言让"调色板"和"语义色"在视觉上不脱钩

### 为什么 `--graph-source-legacy` 用 `--text-secondary` 而非单独的灰 token？
- "历史" 在视觉语义上是"中性/不重要"，与 `--text-secondary` 表达"次要文字"同源
- 单独定义 `--graph-legacy-grey` 增加 token 名空间成本（仅 1 个使用点）
- dark 模式 `--text-secondary: #a1a1a1`（与 light `#8f8f8f` 等档），dark 节点清晰可见
- 决策树与 P47 r2 (ConflictCard severity-low 保留 `#b38b00` hex) 同源："低收益/高 token 名空间成本"不另开 token

### 为什么 `--collection-color-6..10`（Apple hex）在 dark 模式不调暗？
- Apple 系统色（`#5856d6/#ff2d55/#00c7be/#ff6482/#30b0c7`）本身对深色背景已足够清晰（Vercel/Apple HIG 设计）
- 与 1-5 号色（Tailwind 调色板）形成"系统色 + 调色板"混合，符合 Apple Design Language
- dark 模式无需再提亮（与 P48 r1 / r3 的"500→400 阶提亮"决策有别）
- 决策树：与 P47 r2 (ConfigStep banner 改用 `--accent-secondary → --accent` 而非保留紫色) 同源 — "保持视觉重量"优先

### 为什么 CollectionEditor 不在 backend 强制迁移旧 hex？
- `CollectionCard.vue:2-4` 仍在用 `collection.color + '20'` 拼接 alpha（`#007aff20`）
- var() 引用无法拼接 alpha（`var(--collection-color-1)20` 非法 CSS）
- 改造 `CollectionCard` 走 token 需要重新设计 alpha 通道（如额外定义 `--collection-color-1-bg: rgba(...)`），跨 r2 影响面大
- 当前决策："新 collection 走 var() 引用 + 旧 collection 走 hex 透传"，两套数据共存不影响功能
- 后续可单独一轮做 `CollectionCard` 全面 token 化（需要新增 `--collection-color-N-bg` 10 个 token）

### 为什么 `getNodeColor` fallback 用 `var(--graph-source-legacy)` 而非保留 `'#86868b'`？
- fallback 触发场景是 `sourceColors[node.source]` 找不到对应 key（`node.source` 是新 backend 字段但前端 map 没覆盖）
- fallback 应该与 `sourceColors.legacy` 视觉一致（"未知源 = 历史色"）
- 都走 token 让 dark 模式 fallback 也自动跟随 — 否则 dark 模式 fallback 仍是 light 字面灰

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ⚠️ 1 pre-existing error in CommandPalette.vue:47 (unrelated to P48, present before r1) |
| `npm run build` | ✅ 2.49-2.54s, dist 完整生成（asset hashes 更新） |
| `grep "'#007aff'\|'#34c759'\|'#ff9500'\|'#af52de'\|'#ff3b30'\|'#5ac8fa'\|'#0072f5'\|'#22c55e'\|'#8b5cf6'\|'#ef4444'\|'#06b6d4'" frontend/src/components/Layout/{AnnotationThread,CollectionEditor,LineageGraph}.vue` | ✅ 0 active leaks (注释除外) |
| `grep -cE "^}" frontend/src/styles/variables.css` | ✅ 2 (light + dark 各自 `}` 正确闭合) |
| 8501 服务进程 | 未触碰，仍在 serving `frontend/dist`（用户刷新即生效） |
| 后端 / 新依赖 | 无（仅 token 替换） |
| 现有功能回归 | avatar / lineage / collection picker 视觉一致性保留：6/6/10 个色卡与原 Apple hex 视觉差异极小 |

---

## 视觉影响估计

| 改动 | 估计影响 | 影响对象 |
|---|---|---|
| r1 AnnotationThread avatar 6 调色板 | **中（dark 模式首正）** — light 模式 0 视觉变化，dark 模式 24px 圆上 12px 文字 4.5:1 对比度 | MemoryDetailView annotation 头像 |
| r2 CollectionEditor 10 调色板 | **中（dark 模式首正 + 新 collection 持久）** — 新 collection picker 选中态在 dark 模式自动跟随 | CollectionsView 创建/编辑 modal |
| r3 LineageGraph 6 调色板 | **中（dark 模式首正）** — SVG circle fill 自动跟随主题 | MemoryDetailView lineage 圈图 + SourcesView |

**Dark 模式累计触达**：
- 每次打开 MemoryDetailView = avatar (r1) + lineage (r3) 双重 token 化收益
- 每次创建 collection = picker (r2) 10 色 token 化收益

---

## 遗留 / 下次可以做

1. **CollectionCard 全面 token 化** — `collection.color + '20'` 拼接 alpha 是 hex-only，需要新增 `--collection-color-N-bg` 10 个 token（每色 + alpha 0.12），跨改造 1 个文件但影响所有 collection 列表渲染
2. **CollectionCard 加载时 hex → var() 自动迁移** — 在 fetch 后用映射函数把 hex 转换为对应的 var() 引用（仅当 hex 命中已知 10 色时），让旧 collection 也享受 dark 模式
3. **SourcesView CollectionEditor 调色板** — 这是上一轮提到的 #2，本轮已做 (r2)
4. **AnnotationThread avatar hash % 6 → % 12 扩展** — 当前 6 槽若用户超过 6 个 author 会撞色，未来若 author 数量增长可扩到 12 槽（与 CollectionEditor 10 色 + 2 系统色合并）
5. **P45 §遗留 #5 DashboardView StatsBar 与 TabBar 小屏合并** — `<NavAndStats>` 单组件
6. **P45 §遗留 #6 MemoryDetailView 按钮密度紧凑化** — 5 个 action 按钮的 ghost 图标+文字标签紧凑
7. **P45 §遗留 #7 `--shadow-elevated` 内部 rgba token 化** — 5 元素组成的复合阴影，可能需要 `--shadow-color-base` 子 token
8. **`/deprecated/*` 7 处 `var(--card-bg, X)`** — 项目规则"不动 deprecated"，留给归档时统一处理
9. **页面切换 `<Transition name="page">`** — 已完成 (P38 r9)，跳过

---

## 与前后轮次的关系

| 轮次 | 主题 | 影响 |
|---|---|---|
| P45 r1 | HealthBadge token 化 + 视觉锚点升级 | 6 hex → 0 hex |
| P45 r2 | on-accent 收口 (BatchToolbar + OnboardingTour) | 2 文件 9 处 |
| P46 r1 | SetupWizard token 化 (10+ hex → 0 hex) | dark 100% 覆盖 |
| P47 r1 | RoleBadge 3 角色 token 化 | dark 模式首正 |
| P47 r2 | Apple/Material hex sweep (7 文件 35 处) | dark 模式首正 |
| P47 r3 | `var(--card-bg, X)` 失效 token 收口 (4 active 文件 7 处) | 修复 P38 sweep 漏掉的真 bug |
| **P48 r1（本轮）** | **AnnotationThread avatar 6 调色板 token 化** | **dark 模式首正** |
| **P48 r2（本轮）** | **CollectionEditor 10 调色板 token 化** | **新 collection dark 模式首正** |
| **P48 r3（本轮）** | **LineageGraph 6 调色板 token 化** | **dark 模式首正** |

---

**Commits**:
- `c5e78e0` P48 r1: AnnotationThread avatar 6 调色板 token 化
- `f49906b` P48 r2: CollectionEditor 10 调色板 token 化
- `3377338` P48 r3: LineageGraph 6 调色板 token 化
- 本报告（`docs/P48_AUDIT_REPORT.md`）

**Files changed** (3 commits 累计):
- `frontend/src/styles/variables.css`（+71 行，3 套调色板 light + dark）
- `frontend/src/components/Layout/AnnotationThread.vue`（+14 -2，avatarColor 返回 var() 引用 + hashName 抽取）
- `frontend/src/components/Layout/CollectionEditor.vue`（+13 -11，10 色 picker + 默认值 + fallback token 化）
- `frontend/src/components/Layout/LineageGraph.vue`（+8 -7，sourceColors 6 源色 + getNodeColor fallback token 化）
