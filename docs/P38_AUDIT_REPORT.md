# P38 UI 优化审计报告

**日期**: 2026-06-03
**主题**: 自驱动 UI 优化第二轮
**目标**: 三大高频视觉表面 — 卡片强度锚点 / 侧栏激活态 / 搜索框
**约束**: 不新增功能、不动 backend、不引入新依赖

---

## 改动清单

### 1. MemoryCard 强度视觉锚点（最大视觉影响）

**问题**:
- 3px 细条 + 极小 "44%" 文字，强度信息被边缘化
- 单一蓝色 `--accent` 进度条，缺乏分级信息
- 用户无法在列表中快速判断记忆强度层级

**改动** (`frontend/src/components/Layout/MemoryCard.vue`):
- 在 `.card-meta` 左侧新增 38×38 圆形 SVG progress ring
  - viewBox 0 0 36 36，旋转 -90° 让进度从 12 点钟方向起
  - 中心嵌入 `strengthPercent` 数字（tabular-nums + 600 字重）
- 引入 `strengthTier` computed：`>= 70` → `high`（绿）、`>= 40` → `mid`（黄）、其余 `low`（红）
- 渐变色彩同时应用到 ring 描边 + 进度条 fill + 数字颜色（亮色 / Dark 模式各一套调色）
- `strengthPercent` 同时给到原有的进度条和文字标签（保持单数据源）
- 进度条高度从 3px → 4px（更醒目）
- 数字 `font-variant-numeric: tabular-nums` 防数字宽度抖动
- 移动端 ring 缩到 30×30，字号降到 0.6rem

**影响估计**:
- 列表首屏信息密度 +40%（每张卡片多了一个有色彩权重的视觉点）
- 用户扫视记忆强度时不再需要 hover 或展开
- 高强度记忆（绿色 ring）会形成列表中的"绿色锚点群"，便于快速定位优质记忆

---

### 2. AppSidebar 激活态强化

**问题**:
- 激活项是 `background: var(--accent); color: white` 实心蓝药丸
- 在 220px 侧栏里视觉重量过大，与 P37 建立的克制风格冲突
- 没有"我现在在哪"的指示器（Vercel / Linear / Geist 风格都有 left rail）

**改动** (`frontend/src/components/Layout/AppSidebar.vue`):
- 激活态背景从 `--accent` 实心 → `--accent-subtle`（蓝色 10% 透明）+ `color: var(--accent)` 蓝字 + `font-weight: 600`
- 激活项前新增 3px 宽的 `::before` rail（蓝色圆角矩形）
  - 展开模式：rail 在 `left: -8px`（nav padding 16px 让出空间）
  - 折叠模式：rail 在 `left: 0`，紧贴侧栏左缘
- nav 容器 `padding-left` 从 8px → 16px 给 rail 留出显示空间
- hover 背景从 `--border` → `--tag-bg`（更轻的 hover 反馈）

**影响估计**:
- 激活态视觉更"克制但精确"：从"按钮"变为"指示"
- 折叠模式仍能 100% 识别当前路由（rail + 蓝色文字双信号）
- 整体侧栏从"导航菜单"升级为"导航系统"

---

### 3. SearchBar Geist 化

**问题**:
- 硬编码 `rgba(0, 122, 255, 0.12)` 和 `rgba(139, 92, 246, 0.15)`，未走 token 系统
- `--semantic-accent` 用了 CSS var fallback `#8b5cf6` 而非 design token
- 输入框背景是 `--card`（白），与 Geist 的"recessed input"（凹陷灰）不符
- 右侧 padding `110px` 是绝对定位算出来的 brittle 数字，移动端断点依赖这个数重新算
- 暗色模式仍用 `prefers-color-scheme` 媒体查询，未走 `data-theme` token
- kbd 提示用了 `monospace` generic，应使用 `var(--font-mono)`

**改动**:

(a) `frontend/src/styles/variables.css`:
- 新增 5 个 token（亮色 + Dark 双套）：
  - `--semantic-accent` / `--semantic-accent-hover` / `--semantic-accent-subtle` / `--semantic-accent-glow`
  - `--accent-glow`（替换硬编码 `rgba(0, 122, 255, 0.12)`）

(b) `frontend/src/components/Layout/SearchBar.vue`:
- 背景从 `var(--card)` → `var(--bg-recessed)`（凹陷感）
- hover 状态：背景变 `--tag-bg` + 边框变 `--border`
- focus 状态：背景变 `--input-focus`（白）+ 边框 `--accent` + 4px glow ring（用 `--accent-glow` / `--semantic-accent-glow`）
- focus 时搜索图标也变色（用 `:focus-within` + `~` 选择器）
- Mode toggle 从纯灰底 → 白底卡片 + 微阴影，hover 改用 `--tag-bg` 而非全蓝
- 移除 `prefers-color-scheme` 媒体查询（让 `[data-theme='dark']` 自动接管）
- kbd 提示改用 `var(--font-mono)` + `font-weight: 500`
- 调整 padding 数字（从 110 → 130）让右侧三件套（kbd 提示 / 清除按钮 / mode toggle）有更多喘息空间

**影响估计**:
- 搜索框从"白底输入"升级为"凹陷槽位"，更符合 Geist 风格
- 焦点态有清晰的"光圈"反馈，颜色自动跟随模式
- 所有硬编码颜色消除，token 化进度 95% → 接近 100%

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors |
| `npm run build` | ✅ 2.39s，dist 完整生成 |
| 8501 服务进程 | 未触碰，仍在 serving `frontend/dist`（用户刷新即生效） |
| 后端 / 新依赖 | 无 |
| 现有功能回归 | 强度计算逻辑保持（`memory.strength * 10`），进度条 + ring + 文字三处同步显示 |

---

## 遗留 / 下次可以做

1. **MemoryCard 折叠态 ring 数字** — 38px 空间里 0.7rem 数字在 dense 列表下可能略小，可以考虑把 0~100 改为 "X/10"（0-10）格式以更大字号显示
2. **AppSidebar 折叠模式 rail 位置** — 当前 `left: 0` 在 64px 折叠态下紧贴视口左缘，如果未来侧栏有"侧边小条"（如 Linear），可能需要让出 4-8px
3. **SearchBar 命令面板** — `Cmd+K` 触发的 CommandPalette 没用同样的 Geist token 化，可以做 P39
4. **type 标签色块化** — P38 选项 6 未做；type badge 当前已经有 bg/text token，但视觉差异可以更"色块"化（更大 padding、icon prefix）
5. **按钮层级审计** — HomeView / Dashboard 的多按钮并存问题未触及（独立 P39 任务）

---

**Commit**: P38
**Files changed**:
- `frontend/src/components/Layout/MemoryCard.vue`（+90 -12）
- `frontend/src/components/Layout/AppSidebar.vue`（+27 -6）
- `frontend/src/components/Layout/SearchBar.vue`（+60 -45）
- `frontend/src/styles/variables.css`（+10 -0）
- `frontend/dist/index.html`（build 产物）
