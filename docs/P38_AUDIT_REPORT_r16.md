# P38 UI 优化审计报告（第七轮 — r16 MemoryDetailView 视觉锚点对齐）

**日期**: 2026-06-04
**主题**: r15 收尾"section title 视觉锚点"后，发现 **MemoryDetailView 的 strength 表达与 MemoryCard 不一致** — list 卡片是 44px ring，detail 页面还是 6px 线性进度条 + 文字。本轮专攻 list↔detail 同一指标的视觉锚点统一。
**目标**: 把 list 卡片和 detail 页面里"记忆强度"这个最高频指标收敛到**同一视觉语言**（44px ring + tier 颜色 + 中心数字），并顺手对齐 type chip / archived badge 的规格。
**约束**: 不新增功能、不动 backend、不引入新依赖、不重启 8501
**前置**: P38 r15 已切到"section title 左侧 3px accent bar"维度；本轮切回 **list↔detail 视觉锚点统一** 维度

> **关于"第七轮"的说明**：前 6 轮（r1-r15）记录在 `P38_AUDIT_REPORT.md` / `_r6.md` / `_r8.md` / `_r9.md` / `_r10.md` / `_r11.md` / `_r12.md` / `_r13.md` / `_r14.md` / `_r15.md`。本报告为**第 7 轮 — MemoryDetailView 视觉锚点对齐**。

---

## 为什么从 r15 a11y 切回视觉

r15 完成后，我自己回到应用里走了一遍"看一条记忆"的完整路径：
1. 首页 / AgentMemory section → 看到 N 张卡片，每张右上 44px 绿色 ring 标"70"
2. 点进一条记忆 → 进入 detail 页面，看到 6px 高的"灰色进度条 + Strength: 70% 文字"

**视觉跳变**：
- list 卡片里 strength 是 **44px ring**（圆 + 中心数字 + tier 颜色 + aria-label）
- detail 页面里 strength 是 **6px 横条 + 文字**（线性 + 单色 + 双表达）

两者表达**同一个数字**（strengthPercent），但视觉权重差距 ~7×。用户在两个视图之间切换时，"强度是 70"这个信息从"视觉锚点"降级成"文字脚注"。

更刺眼的是 type chip：
- list 卡片：uppercase "PATTERN" + 6px 圆点 prefix + 6px 圆角 + 1px 边框
- detail 页面：capitalize "pattern"（小写）+ 12px 圆角 + **无**圆点 + **无**边框

**同一信息，两套视觉语言** — 这是 r15 没覆盖的最后一处大不一致。

---

## 改动清单

### 1. MemoryDetailView strength bar → 44px ring（最高视觉影响）

**问题**（list↔detail 视觉跳变）:

| 元素 | list 卡片 (MemoryCard r15) | detail 页面 (旧) | 视觉权重差 |
|---|---|---|---|
| 表达形式 | 44px 圆形 SVG ring | 100×6 像素 横条 | ~7× |
| 数字呈现 | ring 中心 0.78rem/700 | 文字 "Strength: 70%" 0.85rem | 数字大小相近但 ring 更"图" |
| 颜色 | tier 3 档（green/amber/red） | `--accent` 单色 | ring 能传递"健康/弱化"信息 |
| a11y | `role="img"` + `aria-label` | 仅 title 属性 | ring 有 screen reader 锚点 |

**改动**（MemoryDetailView.vue，3 处）:

1. **Template 替换**（line 40-43 旧 → line 40-59 新）:
   - 删 `<span class="strength-bar">` + `<span class="strength-fill">` + `<span class="meta-text">`
   - 加 `<div class="strength-ring" :class="'strength-ring--' + strengthTier">` 完整 ring 结构（与 MemoryCard r15 字节级对齐）

2. **Script 加 2 个 computed**（`strengthPercent` + `strengthTier`）:
   - 复用 MemoryCard 的同一套算法：`strength * 10` 然后 clamp + Math.round
   - tier 分界: ≥70 high / ≥40 mid / <40 low
   - 注意：detail 页面的 memory 可能正在加载（`memory.value` 可能是 null），用 `memory.value?.strength` 安全取数

3. **CSS 替换**（5 个新规则）:
   - `.strength-ring`: 44×44 flex center
   - `.strength-ring__svg` / `__track` / `__fill`: stroke 3.5px + `transform: rotate(-90deg)` 让 dasharray 从 12 点钟方向开始
   - `.strength-ring--high/mid/low .__fill`: 3 档 tier 颜色（复用 `--strength-high-fill/mid-fill/low-fill`，与 MemoryCard 同源）
   - `.strength-ring__num`: 0.78rem/700 + tabular-nums + letter-spacing -0.02em（与 MemoryCard 数字风格一致）
   - `.strength-ring--high/mid/low .__num`: 3 档 ink 颜色（light 模式深、dark 模式亮，跟随 variables.css）

**a11y 收益**:
- 旧版 `.meta-text "Strength: 70%"` 是**视觉文本**，screen reader 也会读
- 新版 ring 是 `role="img" + aria-label="记忆强度 70%"` — 屏幕阅读器现在获得**结构化语义**（是"图"不是"普通文字"）
- 这与 MemoryCard r15 的 a11y 处理**完全一致**，list↔detail 切换时 screen reader 体验也统一

**视觉影响估计**:
- 6px 横条 + 文字 → 44px 圆环 + 中心数字：视觉权重 +7×（面积比）
- 用户从 list 点进 detail，第一眼就能识别"这是同一指标"（之前是"换了一种表达"）
- dark 模式自动跟随 variables.css 的 `--strength-*-ink` token（与 MemoryCard 同源）

---

### 2. MemoryDetailView type chip 对齐 MemoryCard 规格（中等视觉影响）

**问题**（list↔detail type chip 不一致）:

| 维度 | MemoryCard 卡片 chip | MemoryDetailView 旧 chip | 差异 |
|---|---|---|---|
| 字号 | 0.6875rem | 0.75rem | +9% |
| 圆角 | 6px | 12px | 2× |
| 大小写 | uppercase | capitalize | 大小写不一致 |
| 圆点 prefix | ✅ `::before` 6px 圆点 | ❌ 无 | 视觉锚点缺失 |
| 1px 边框 | ✅ color-mix 18% | ❌ 无 | 边界"糊" |

**改动**（MemoryDetailView.vue line 456-481 旧 → line 457-505 新）:

1. `.memory-type` 6 个属性重写：font-size / padding / radius / transform / border / 升级为 `display: inline-flex; gap: 6px`
2. 新增 `.memory-type::before` 6px 圆点（与 MemoryCard 字节级同源，opacity 0.85）
3. `.type-pattern/workflow/fact/preference/bug/architecture` 加 `border-color: color-mix(in srgb, var(--type-*-text) 18%, transparent)`
4. `.archived-badge` 同步重写：display:inline-flex + gap + 6px 圆角 + uppercase + `::before` 圆点

**视觉影响估计**:
- type chip 与 list 卡片**完全同款**（圆点 + uppercase + 6px 圆角 + 1px 边框）
- 用户在 list 看到 "● PATTERN"（绿底），点进 detail 看到 "● PATTERN"（同色同款）— **同一种语言**
- archived badge 同步升级到"dot + uppercase + 6px 圆角"，与 type chip 节奏一致
- 1px 边框（color-mix 18% 透明度）让 chip 在 `--tag-bg` 卡片背景上有"边界感"，不再"糊"

**为什么 archived-badge 也改**:
- 之前 `.archived-badge` 是 4px 圆角 + 0.7rem + 无 dot + 灰色背景 — 与 type chip 完全两套
- 现在 archived badge 与 type chip 同一节奏（dot + uppercase + 6px 圆角），只是颜色用 `var(--text-secondary)` 区分语义
- 一个 view 里所有"小色块标签"用同一语言，扫视时眼睛能快速识别"这是一个 badge"而不是"这是别的什么"

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors（仅 deprecation warning，与本次无关） |
| `npm run build` | ✅ built in 2.37s，dist 完整生成 |
| 浏览器视觉验证 (vision tool) | ✅ type chip "● WORKFLOW" 大写 + 圆点 + 1px 边框清晰显示 |
| 浏览器视觉验证 (vision tool) | ✅ strength ring 44px 圆环 + 中心 "70" 数字 + tier 颜色 |
| list↔detail 视觉对比 | ✅ 同一指标（strength / type）现在用同一视觉语言 |

---

## 视觉影响估计

| 改动 | 估计影响 | 影响对象 |
|---|---|---|
| strength bar → ring | 高（核心指标，list↔detail 必看） | MemoryDetailView 所有用户 |
| type chip 规格统一 | 中（一致性收益，但单项不刺眼） | MemoryDetailView 所有用户 |
| archived badge 同步 | 低-中（小细节，但与 type chip 形成"badge 节奏"） | 归档记忆的查看者 |

---

## 遗留与下一步建议

**视觉优化已基本穷尽**（P37–r16 累计 8 轮 sweep）。

### 可能的下一轮方向

1. **HermesMemoryView 视觉收尾**（如果它有 detail 页面） — Hermes Memory 列表卡用的是 `.hermes-card`（不是 MemoryCard），strength / type 表达可能不一致
2. **跨设备/浏览器实测** — Geist 字体在不同 OS 上 fallback 路径可能撞色（已用 `font-family: var(--font)` 保护，但需要真机视觉验证）
3. **响应式断点细化** — 当前断点只有 `767/768/1024` 三档，iPad Pro 1024-1366 区间体验可以更精细
4. **动效一致性审计** — 全站 transition 时长有 0.1s / 0.15s / 0.2s / 0.25s / 0.3s / 0.5s 多种，Apple HIG 建议收敛到 2-3 档（如 0.15s 快捷 / 0.3s 常规）
5. **真实 dark mode 视觉走查** — 所有改动都在 light mode 验证，dark mode 需要真实走一遍
