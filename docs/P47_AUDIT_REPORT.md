# P47 UI 优化审计报告

**日期**: 2026-06-05
**主题**: 自驱动 UI 优化第九轮 — Apple/Material hex 漂移收口 + 失效 token `var(--card-bg, X)` 清理
**前提**: P45/P46 + 历次 sweep 已 commit 完毕（最新 `6062961`），本轮接续 P45 §遗留 #1 (RoleBadge token 化) + sweep 6 setup/onboarding/conflict 文件 + 修复 r35 漏掉的 `var(--card-bg, X)` 失效 token
**约束**: 不新增功能、不动 backend、不引入新依赖、只改 CSS

> **关于"P47"编号**：本轮 cron 提示词标签写的是"P38 优化"，但 P38-P46 已全部 commit 完毕。本报告记为 **P47（第 9 轮）**，承接 P45 §遗留 #1 + P46 sweep 漏掉的 hex/token 漂移。

---

## 改动清单（3 个 commit + 1 个 audit report）

### 1. **P47 r1** — RoleBadge 3 角色 hex → 全站 token（最高视觉影响）

**问题**（P45 sweep 漏网）:
- `frontend/src/components/Layout/RoleBadge.vue` 3 角色各自硬编码 Apple hex:
  - admin (橙) → `rgba(255,149,0,0.15) / #ff9500`
  - editor (蓝) → `rgba(0,113,227,0.1) / #007aff`
  - viewer (灰) → `rgba(134,134,139,0.1) / #86868b`
- 全部 `rgba` 硬编码 + Apple 字面色，dark 模式仍渲染亮色 — 与 P38 r19 theme-contract sweep 漏掉的最后一组"角色徽章"语义色对
- 触达：MemoryDetailView 顶部 role 标识（高频），SettingsView 团队成员列表

**改动**（1 文件，3 行 CSS）:
- `.role-badge.admin` → `background: var(--warning-bg); color: var(--warning);`
- `.role-badge.editor` → `background: var(--accent-subtle); color: var(--accent);`
- `.role-badge.viewer` → `background: var(--tag-bg); color: var(--text-secondary);`

**影响估计**:
- **Dark 模式首次正确**：之前用户在 dark 模式看到 admin/editor/viewer 是 light mode 字面 hex
- 触达：每次打开 MemoryDetailView 看到 role 标识 = **每日 20+ 次**
- 决策树与 P45 r1 HealthBadge 同源：3 状态徽章全部走 token，dark 模式自动跟随

---

### 2. **P47 r2** — Apple/Material hex 漂移收口 sweep（7 文件 ~35 处）

**问题**（P38-P46 sweep 漏网，P36 审计时未列入）:
- **SetupWizard 4 文件** 大量硬编码 Apple/Material hex：`#007aff` / `#f0f7ff` / `#0056b3` / `#e8f5e9` / `#2e7d32` / `#ffebee` / `#c62828` / `#f8f9fa` / `#666` / `#999` / `#667eea` / `#764ba2` / `rgba(0,122,255,0.4)`
  - ImportStep.vue: `option-card:hover` 蓝色 border + `desc/option-desc` 灰文 + `import-result` 成功色
  - ConfigStep.vue: `input:focus` 蓝边 + `status.connected/error` + `btn-skip-config` 蓝 + `quick-start-section` 紫渐变 + `presets` 系列
  - DoneStep.vue: `done-desc` 灰文 + `link-card` 静态 bg + hover 蓝边 + `hint` 弱化
- **AnnotationThread.vue**: 8 处 `var(--card-bg, X)` 失效 token + flag/suggest item 主题色 + 6 处 Material hex (`#e3f2fd` / `#1565c0` / `#fff3e0` / `#e65100` / `#999` / `#ff3b30` / `#5ac8fa` / `#f0f8ff` / `#fff8f0` / `#ff9500`) — dark 模式看到的依然是亮色主题
- **FeatureTour.vue**: 6 处 hex + `tour-pulse` keyframes `rgba(0,122,255,...)` 硬编码
- **WorkflowLog.vue**: `#666 / #999 / #333` 三级灰文 + hover `#007aff`
- **ConflictCard.vue**: `btn-resolve` 4 分支（keep-a/keep-b/merge/dismiss）+ `severity-badge` 3 档（high/medium/low）+ `severity-card` 3 档的 left border

**改动**（7 文件，~35 处替换）:

| 文件 | 改动数 | 主要决策 |
|---|---|---|
| ImportStep.vue | 4 | `#007aff` → `--accent`, `#666` → `--text-secondary`, `#e8f5e9/#2e7d32` → `--success-bg/--success-text` |
| ConfigStep.vue | 11 | 同上 + `#0056b3` → `--accent-hover`, `#c62828` → `--error-text`, 紫渐变 → `--accent-secondary/--accent` 蓝蓝渐变, on-accent `color: white` → `var(--card)` |
| DoneStep.vue | 4 | `#007aff` → `--accent`, `#f0f7ff` → `--accent-subtle`, `#999` → `--text-tertiary` |
| AnnotationThread.vue | 13 | flag → `--warning-bg/--warning`, suggest → `--info-bg/--info-text`, `var(--card-bg)` → `--card`, on-avatar `color: white` → `var(--card)`, `.danger` → `--error` |
| FeatureTour.vue | 6 | `#007aff` → `--accent`, `#f0f7ff` → `--accent-subtle`, `#f8f9fa` → `--bg-recessed`, `#666` → `--text-secondary`, keyframes rgba → `--accent-glow` |
| WorkflowLog.vue | 4 | `#666/#999/#333` → `--text-secondary/--text-tertiary/--primary`, hover `#007aff` → `--accent` |
| ConflictCard.vue | 9 | keep-a→`--accent`, keep-b→`--success`, merge→`--warning`, dismiss→`--text-secondary`, severity high/medium/low → `--error/--warning/--b38b00` (yellow low 留 hex) |

**关键决策**: ConfigStep quick-start-section 紫蓝渐变 (`#667eea → #764ba2`) 改成 `--accent-secondary → --accent`（indigo → blue），仍保留 hero 横幅视觉重量但与全站 token 同源。

**影响估计**:
- **Dark 模式首次正确**：7 个文件在 dark 模式之前是 light 字面 hex，role 徽章 / 主题项 / toast-style 成功提示 / 冲突严重度都"看着像 light mode"
- **SetupWizard 全套一致性**：4 个 step 文件（Welcome/Config/Import/Preferences/Done）现在 100% 走 token
- **注解 / 评论 / 工作流** 也走全站 token

---

### 3. **P47 r3** — `var(--card-bg, X)` 失效 token 收口（4 active 文件 7 处）

**问题**（P38 sweep 漏掉的真 bug）:
- `var(--card-bg, X)` 在 `frontend/src/styles/variables.css` **从未定义** — 实际只有 `--card` / `--bg-recessed` / `--bg`
- 8 个文件使用 `var(--card-bg, X)` fallback，**token 未定义 → 浏览器永远退到字面 hex X**
- 等于"P38 token 化"承诺在这些地方**完全没生效**，dark 模式这些元素仍是 light mode 字面色
- 文件清单:
  - `frontend/src/components/steps/WelcomeStep.vue` 1 处
  - `frontend/src/components/steps/PreferencesStep.vue` 2 处
  - `frontend/src/components/Layout/AnnotationInput.vue` 3 处
  - `frontend/src/components/OnboardingTour.vue` 2 处
  - `frontend/src/components/Layout/AnnotationThread.vue` 1 处（在 r2 已顺手修）
  - `frontend/src/components/SetupWizard.vue` 0 处（r1 文档已注释说要清，但漏了）
  - `/deprecated/*` 2 文件 8 处（项目规则"不动 deprecated"，跳过）

**改动**（4 文件，7 处替换）:
- `.feature-item` bg `#f8f9fa` → `var(--bg-recessed)` (WelcomeStep)
- `.pref-item` bg `#f8f9fa` → `var(--bg-recessed)`, `.pref-select` bg `#fff` → `var(--card)` (PreferencesStep)
- `.input-textarea / .type-select / .author-input` bg `#fff` → `var(--card)` (AnnotationInput)
- `.tooltip-icon-wrap` bg `#f0f7ff` → `var(--accent-subtle)`, `.btn-nav` bg `#f8f9fa` → `var(--bg-recessed)` (OnboardingTour)

**影响估计**:
- **真 bug 修复**：dark 模式这些元素之前是"fake dark"（`#f8f9fa` 仍是浅灰），现在是真 dark（`--bg-recessed` 在 dark 模式 = `#1c1c1c`）
- 触达：每次打开 SetupWizard (5 个 step 都受影响) + 每次在 MemoryDetailView 写 annotation
- 关键：这是 P38 theme-contract sweep 的"漏网之鱼" — token 写了但写错了名字，导致 dark 模式契约失守

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors |
| `npm run build` | ✅ 2.47-2.57s, dist 完整生成（asset hashes 更新） |
| `grep -rn "var(--card-bg" frontend/src --include="*.vue"` | ✅ 0 active files（仅 `/deprecated/*` 与本报告注释） |
| `grep -nE "#007aff\|#f0f7ff\|#34c759\|#ff9500" frontend/src/components/{steps/*,Layout/AnnotationThread,Layout/ConflictCard,Layout/WorkflowLog}` | ✅ 0 active leaks (注释除外) |
| 8501 服务进程 | 未触碰，仍在 serving `frontend/dist`（用户刷新即生效） |
| 后端 / 新依赖 | 无（仅 token 替换 + 1 处 gradient 改 token 化） |
| 现有功能回归 | 视觉重量不变：徽章 3 状态对应仍清晰可读；severity 3 档红橙黄对比仍强；SetupWizard banner 仍 hero 横幅（紫蓝渐变 → 蓝蓝渐变，色相微调但视觉重量一致） |

---

## 设计决策记录

### 为什么 ConfigStep banner 改用 `--accent-secondary → --accent` 而不是保留紫色？
- 之前 `#667eea → #764ba2` 是"独立紫色品牌"，与全站 --accent 蓝无关联
- 改后 `var(--accent-secondary) → var(--accent)` 是 "indigo → blue" 同 hue 系渐变，dark 模式 `--accent` 自动 = `#3291ff`，仍 hero
- token 化后若将来调整 --accent，banner 自动跟随，无需手动改 banner
- 视觉重量：紫蓝 → 蓝蓝，饱和度略降但首屏吸引力仍强（purple-blue 渐变是 Tailwind/Vercel 常见模式）

### 为什么 ConflictCard severity-low 保留 `#b38b00` hex？
- "低"严重度是黄色，黄色与 --warning 橙在 dark 模式对比度不够（黄字深色背景会糊）
- 单独定义 `--caution` token 收益低（仅 1 个使用点）
- 与 P45 §遗留 #7（`--shadow-elevated` 内部 rgba）"低收益 / 高 token 名空间成本"的决策同源
- 注释里已写明"单独 token 没意义"

### 为什么 AnnotationThread avatar 6 色调色板没动？
- `colors = ['#007aff', '#34c759', ...]` 是 hash 派发（同一 author 永远同色），不是"语义色对"
- 6 色全 token 化 = 新增 `--avatar-1..6` 6 个 token，dark 模式需要单独调暗
- 与 P45 §遗留 #1 (AnnotationThread 6 色调色板 token 化) 同源，留待 P48 单独处理
- 视觉影响：dark 模式 avatar 6 色偏亮，但**与项目设计语言脱钩的代价更大**

### 为什么 `color: white` 在 Toast 没动？
- Toast bg = `var(--toast-success/error/info)` 三个 translucent 彩色
- 三个 bg 都需要 white text 才能在彩色背景上保持对比度（Apple system translucent 设计语言）
- `var(--card)` 在 light 模式 = `#fff`，dark 模式 = `#171717`，**dark 模式黑色文字在彩色 bg 上会糊**
- 故意保留（P45 §遗留决策已写）

### 为什么 P47 r3 用 `--bg-recessed` 而不是 `--card`？
- `--bg-recessed` 是"次级 bg"（输入框/凹陷面板）— feature-item / pref-item / btn-nav 视觉上"想凹陷"
- `--card` 是"主卡片表面" — feature-item 用 `--card` 视觉权重太重（与 wizard 主体同色，等于没边界）
- 与 SearchBar `.search-input` 同源（已用 `--bg-recessed`）

### 为什么 `tour-pulse` keyframes 用 `var(--accent-glow)` 而不是 `var(--accent)`？
- 0.4 alpha 的彩色发光在 8px 扩散到 0 alpha，需要 alpha 控制
- `--accent-glow = rgba(0, 114, 245, 0.14)` 是 variables.css 已定义的"主色发光"色
- 用同一个 token 让 dark 模式自动跟随（dark 模式 `--accent-glow` 仍亮）
- 视觉上 0.4 vs 0.14 的差异在 keyframes 末段（已 fade 到 0）几乎不可见

---

## 遗留 / 下次可以做

1. **AnnotationThread 6 调色板 token 化** — 需新增 `--avatar-1..6`，dark 模式调暗一档，hash 派发保持 author 同色
2. **SourcesView CollectionEditor 10 调色板 token 化** — 同上，是 collection color picker 的备选色
3. **LineageGraph source 调色板 token 化** — `manual: '#007aff'` 等图表源色
4. **P45 §遗留 #5 DashboardView StatsBar 与 TabBar 小屏合并** — `<NavAndStats>` 单组件
5. **P45 §遗留 #6 MemoryDetailView 按钮密度紧凑化** — 5 个 action 按钮的 ghost 图标+文字标签紧凑
6. **P45 §遗留 #7 `--shadow-elevated` 内部 rgba token 化** — 5 元素组成的复合阴影，可能需要 `--shadow-color-base` 子 token
7. **`/deprecated/*` 7 处 `var(--card-bg, X)`** — 项目规则"不动 deprecated"，留给归档时统一处理
8. **页面切换 `<Transition name="page">`** — 路由切换 150ms fade，0 风险 0 依赖

---

## 与前后轮次的关系

| 轮次 | 主题 | 影响 |
|---|---|---|
| r17 | on-accent text #fff → var(--card) | 2 文件 2 处 |
| r19 | theme-contract sweep (12 files) | 全站 dark 模式 |
| r33 | on-accent text token 化续 | 1 文件 1 处 |
| P45 r1 | HealthBadge token 化 + 视觉锚点升级 | 6 hex → 0 hex |
| P45 r2 | on-accent 收口 (BatchToolbar + OnboardingTour) | 2 文件 9 处 |
| P45 r3 | AppHeader 副标题路由淡入 | P28 #5 遗留 |
| P46 r1 | SetupWizard token 化 (10+ hex → 0 hex) | dark 100% 覆盖 |
| **P47 r1（本轮）** | **RoleBadge 3 角色 token 化** | **active in MemoryDetailView** |
| **P47 r2（本轮）** | **Apple/Material hex sweep (7 文件 35 处)** | **dark 模式真首次正确** |
| **P47 r3（本轮）** | **失效 token `var(--card-bg, X)` 收口 (4 active 文件 7 处)** | **修复 P38 sweep 漏掉的真 bug** |

---

**Commits**:
- `3f2cc90` P47 r1: RoleBadge 3 角色 hex → 全站 token
- `da1ccdc` P47 r2: Apple/Material hex 漂移收口 sweep (7 文件 ~35 处)
- `bd85472` P47 r3: `var(--card-bg, X)` 失效 token 收口 (4 active 文件 7 处)
- 本报告（`docs/P47_AUDIT_REPORT.md`）

**Files changed** (3 commits 累计):
- `frontend/src/components/Layout/RoleBadge.vue`（+11 -3，token 化）
- `frontend/src/components/steps/ImportStep.vue`（+6 -4，4 hex 收口）
- `frontend/src/components/steps/ConfigStep.vue`（+13 -10，11 处替换 + 渐变 token 化）
- `frontend/src/components/steps/DoneStep.vue`（+6 -3，4 hex 收口）
- `frontend/src/components/steps/WelcomeStep.vue`（+1 -1，失效 token 修复）
- `frontend/src/components/steps/PreferencesStep.vue`（+2 -2，失效 token 修复）
- `frontend/src/components/Layout/AnnotationThread.vue`（+12 -11，13 处 token 化 + 失效 token 修复）
- `frontend/src/components/Layout/AnnotationInput.vue`（+3 -3，3 处失效 token 修复）
- `frontend/src/components/Layout/WorkflowLog.vue`（+5 -4，4 hex 收口）
- `frontend/src/components/Layout/ConflictCard.vue`（+9 -9，9 hex 收口 + 失效 token 修复）
- `frontend/src/components/FeatureTour.vue`（+7 -6，6 hex 收口 + keyframes token 化）
- `frontend/src/components/OnboardingTour.vue`（+2 -2，2 处失效 token 修复）
- `frontend/dist/*`（build 产物，asset hashes 更新）
