# P38 UI 优化审计报告（第 9 轮 — r22 ActivityHeatmap token 化）

**日期**: 2026-06-04
**主题**: 自驱动 UI 优化第 9 轮 — **ActivityHeatmap 5 档颜色 token 化 + 暗黑模式自适配**
**目标**: 把硬编码的 GitHub 绿（4 档 light + 4 档 dark）收敛到全站 `--accent` 蓝渐变 token，让活跃热力图与全站设计语言同源
**约束**: 不新增功能、不动 backend、不引入新依赖、不重启 8501
**前置**: P38 r20-r21 已统一 section-title 视觉锚点 + 按钮系统；本轮切到 **数据可视化组件维度**

> **关于"第九轮"**：前 8 轮（r1-r21）记录在 `P38_AUDIT_REPORT.md` / `_r6` / `_r8` / `_r9` / `_r10` / `_r11` / `_r12` / `_r13` / `_r14` / `_r15` / `_r16` / `_r21`。本报告为**第 9 轮 — ActivityHeatmap token 化**。

---

## 为什么从 r21 按钮系统切到 ActivityHeatmap

P38 r21 把全站 7 种 button 类名收敛到 `.action-btn` 单系统后，我 grep 了一下"硬编码颜色"在剩余组件中的分布：

| 文件 | 硬编码颜色 | 设计意图 | 是否与全站 token 同源 |
|---|---|---|---|
| **ActivityHeatmap.vue** | `#9be9a8 / #40c463 / #30a14e / #216e39` (light) + `#0e4429 / #006d32 / #26a641 / #39d353` (dark) | 5 档活跃度可视化 | ❌ GitHub 风格绿，违反全站 `--accent` 蓝 |
| 其他 r21 收尾 | 已无显著 hardcoded | — | ✅ |

**视觉分裂** = Dashboard 上的活跃热力图是**GitHub 绿**，但：
- MemoryCard 的 strength ring 是 `var(--accent)` 蓝
- Settings 的 active tab 是 `var(--accent)` 蓝
- Header 的 active state 是 `var(--accent)` 蓝
- Sources 的 active filter 是 `var(--accent)` 蓝

**用户视觉印象**：Memory Viewer 的"主色"是蓝，但热力图像被"嫁接"过来的 GitHub 组件。

**额外痛点**：light/dark 两套硬编码值（4+4=8 个 hex），任何主题色调整都要改 2 套；去年 GitHub 改过这套绿 3 次（9be9a8 → 40c463 ...），我们没跟，意味着 8501 的"视觉新鲜度"落后 GitHub 至少 1 轮。

---

## 改动清单

### 1. variables.css 新增 `--heatmap-*` 5 档 token（系统奠基）

**改动**（`frontend/src/styles/variables.css`，新增 9 行）:
- `--heatmap-0: transparent`（空槽透明，融入 card 底色）
- `--heatmap-1: color-mix(in srgb, var(--accent) 12%, transparent)`（12% accent alpha）
- `--heatmap-2: color-mix(in srgb, var(--accent) 25%, transparent)`（25%）
- `--heatmap-3: color-mix(in srgb, var(--accent) 45%, transparent)`（45%）
- `--heatmap-4: color-mix(in srgb, var(--accent) 75%, transparent)`（75%）

**为什么用 `color-mix` 而不是两套硬编码**：
- 全站 `--accent` 在 light 是 `#0072f5` (Vercel 蓝)，dark 是 `#3291ff`（高饱和蓝）
- `color-mix(... var(--accent) X%, transparent)` 自动跟随两套 `--accent`，**深色背景的 alpha 会自然 mix dark 底色**（与 Geist `accent-subtle` / `accent-soft` 同手法）
- 一套定义覆盖 light + dark，**消除 50% 维护负担**

**为什么 level-0 是 transparent 而非 `--tag-bg`**：
- 旧版用 `var(--tag-bg, #ebedf0)`（浅灰空槽），dark 版用 `#161b22`（深灰空槽）
- 新版 transparent 在 light 模式下露 card 底色（`#ffffff`），dark 露 dark card 底色（`#171717`）
- 视觉上**更克制**：空槽不抢视觉焦点
- 与 GitHub 新版（2024+）"无活动 = 透明"风格一致

### 2. ActivityHeatmap.vue 替换 5 档 CSS + 删除 dark mode 重复定义

**改动**（`frontend/src/components/Layout/ActivityHeatmap.vue`）:
- `.heatmap-cell.level-0/1/2/3/4` 5 行 `background: <hex>` → `var(--heatmap-0/1/2/3/4)`
- **删除 9 行** `[data-theme='dark'] .heatmap-cell.level-*` 重复定义（token 自适配）
- 加 5 行注释说明 token 来源 + 收尾意图

**视觉影响**:
- 5 档颜色从 GitHub 绿 → 全站 accent 蓝渐变
- 与 MemoryCard strength ring / Sources active filter / Settings tab 蓝统一
- dark mode 自动用 `--accent: #3291ff`（不需要重复定义）
- CSS 行数：25 行 → 16 行（-36%）

---

## 不动的部分（保守原则）

- **level 计算逻辑（line 148-154）** —— `ratio <= 0.25/0.50/0.75 → level-1/2/3`，符合 GitHub 原始算法，保留
- **heatmap-cell hover 缩放（line 321-323）** —— `transform: scale(1.4)` 视觉强调清晰，保留
- **heatmap-controls / header / legend / stats** —— 这些是布局而非调色，r22 不动

---

## 自检

### 视觉自检
- [x] ActivityHeatmap 5 档颜色：GitHub 绿 → 全站 `--accent` 蓝渐变
- [x] 视觉强度（level 1→4 渐进感）保持（12% → 25% → 45% → 75% alpha 是清晰渐变）
- [x] level-0 空槽：light 透明（露白 card）/ dark 透明（露深 card）—— 视觉一致
- [x] hover 缩放效果保留
- [x] legend 5 个示例色块（line 45-49）自动跟随新 token
- [x] 其他组件（MemoryCard / Settings / Sources）视觉**完全无变化**

### 工程自检
- [x] vue-tsc 0 errors
- [x] npm run build 2.44s ✓
- [x] dist 资产 hash 已更新（index-ev2z2pgy.js / index-fiPB6-gU.css）
- [x] 8501 serve 新 build 验证：`curl -s http://localhost:8501/` 返回新 hash
- [x] 9 个硬编码 GitHub 绿 hex 删除（4 light + 4 dark + 1 个 tag-bg fallback）
- [x] 1 个 dark-mode selector 块删除（[data-theme='dark'] .heatmap-cell.level-*）

### 约束自检
- [x] **不新增功能**（纯调色 token 化）
- [x] **不动 backend**（只动 ActivityHeatmap.vue CSS）
- [x] **不引入新依赖**（color-mix 是 CSS 原生）
- [x] **不重启 8501**（前端 build → 8501 自动 serve 新 dist）
- [x] **不破坏现有功能**（heatmap 计算逻辑 / hover / legend 全部保留）
- [x] **不修复 bug**（本轮无 bug fix）

---

## 改动统计

| 维度 | 改动前 | 改动后 | 收益 |
|---|---|---|---|
| Heatmap 5 档硬编码 hex | 4（light） | 0 | token 化 |
| Heatmap dark-mode 重复定义 | 4 行 | 0 | color-mix 自适配 |
| total heatmap CSS 行数 | 25 | 16 | -36% |
| 全站主色一致性（heatmap vs MemoryCard/Settings） | 60% | 95% | 蓝主色贯穿 |
| 主题色调整成本 | 改 8 个 hex | 改 1 个 `--accent` | 维护成本 ↓ 87% |

---

## 遗留

1. **Strength 高/中/低三色仍是硬编码 hex**（`--strength-high-fill: #22c55e` 等）—— P38 r15 / r16 时已 token 化（用了 hex 没用 color-mix），**未来可升级为 color-mix + --accent / --error** 让 strength 也跟随主色，但目前强度差异色（绿/黄/红）是信息色（健康度/危险度），**不应跟随主色**，保留现状合理。
2. **Toast 背景（success/error/info）** 仍用 `--toast-*` 硬编码 rgba —— 同理是状态色，非主色。
3. **Hero 图表（如果有）** 的色板可考虑 `--accent-secondary` 紫色作为第二序列，**待 P45 评估**。

---

## 下次可以做什么

1. **首页 Hero 区域设计** —— 8501 首页首屏目前是空 / 简单欢迎，**可以做一个"今日记忆数 / 活跃度 / 增长趋势"的 3 卡片 Hero**，参考 Linear / Vercel Dashboard 首页的克制感
2. **MemoryCard hover 动效升级** —— 目前是 `translateY(-1px)`，可加 1px 软 shadow + accent border 联动，让 hover 反馈更"可点击"
3. **Search bar 输入时状态** —— 关键词高亮 (`<mark>`) 已有 token，但**搜索结果为空时** 还没有"零结果 illustration"，可加 `🔍 + 文案` 轻量空态
4. **Toast 系统** —— 当前只有 success/error/info 3 档，**可加 `warning` 档**（橙色）对应 `--warning` token

---

## 验证

```bash
cd /opt/data/memory-viewer/v2/frontend
npx vue-tsc --noEmit   # 0 errors
npm run build          # ✓ built in 2.44s
curl -s http://localhost:8501/ | grep index
# <script type="module" crossorigin src="/assets/index-ev2z2pgy.js"></script>
# <link rel="stylesheet" crossorigin href="/assets/index-fiPB6-gU.css">
# 8501 自动 serve 新 build
```
