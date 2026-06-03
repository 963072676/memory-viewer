# P43 UI 优化审计报告

**日期**: 2026-06-03
**主题**: 自驱动 UI 优化第四轮（按 P42 遗留）
**目标**: 模态 backdrop 全站 sweep + Geist mono 字体全站统一
**约束**: 不新增功能、不动 backend、不引入新依赖、只改 CSS/Vue 模板

> **关于"P38 循环"的说明**：本轮 cron 提示词标签写的是"P38 优化"，但 P38 / P39 / P40 / P41 / P42 在本次运行前都已 commit 完毕（最新为 `a58a831 P42`）。P42 报告中点名 6 项遗留，其中 2 项属于"token 化收尾"——影响范围广、可机械 sweep、与之前 P38-P42 的 Geist 体系一脉相承。本报告记为 P43（第 6 轮），承接 P42 收尾。

---

## 改动清单

### 1. 模态 backdrop 全站 sweep（最大视觉影响 — 暗色模式）

**问题**（P42 报告 #1 明确点名）:
- `--modal-backdrop` token 已在 P42 加入 variables.css（亮色 0.5 / Dark 0.7）
- 但 11 个 active 文件仍硬编码 `rgba(0, 0, 0, 0.5)`，导致 **Dark 模式下所有 modal/dialog/bottom-sheet 的背景遮罩没有自动变深**
- 唯一例外是 CommandPalette（P42 报告时已修）
- OnboardingTour 的"探照灯"用 `box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5)`，同病同药

**改动**（11 个文件，11 处替换）:

| 文件 | 选择器 |
|---|---|
| `AppSidebar.vue` | `.bottom-sheet-overlay` |
| `CollectionEditor.vue` | `.modal-overlay` |
| `ConfirmDialog.vue` | `.confirm-overlay` |
| `CreateMemoryModal.vue` | `.create-modal-overlay` |
| `EditMemoryModal.vue` | `.edit-modal-overlay` |
| `ImportModal.vue` | `.import-modal-overlay` |
| `KeyboardHelp.vue` | `.keyboard-help-overlay` |
| `LinkCreator.vue` | `.modal-overlay` |
| `PIIIndicator.vue` | `.pii-confirm-overlay` |
| `WhatsNewModal.vue` | `.modal-overlay` |
| `OnboardingTour.vue` | `.tour-spotlight`（box-shadow 用例） |

所有 11 处 `rgba(0, 0, 0, 0.5)` → `var(--modal-backdrop)`。

**影响估计**:
- **Dark 模式首次正确** — 之前用户切换 Dark 主题后，遮罩还是 0.5 半透明黑，与 P42 设定的"Dark 模式 0.7"不一致。修复后 Dark 模式遮罩自动加深 ~20%，与 CardList/MemoryCard 的暗色调和谐
- 触达所有 modal/bottom-sheet/spotlight/dialog 入口（创建记忆、编辑、导入、分享、链接、PII 确认、键盘帮助、What's New、Collection 编辑、移动端 BottomSheet、Onboarding 引导）
- 颜色决策中心化：未来要"全部遮罩再深一点"只需改 token 一处

---

### 2. Geist mono 字体全站统一（kbd / code 元素）

**问题**（P42 报告 #6 明确点名）:
- 7 个 active 文件仍用 `font-family: monospace`（generic，会回退到系统字体 Times/Courier）
- 与 P40 建立的 `--font-mono` Geist mono 体系脱节
- 3 个 kbd/submit-hint 元素的 `font-weight` 未统一（kbd 系应有 `font-weight: 500`）

**改动**（7 个文件，9 处替换 + 3 处加 font-weight）:

| 文件 | 选择器 | 加 font-weight |
|---|---|---|
| `MemoryDetailView.vue` | `.memory-id` | — |
| `ShareModal.vue` (×2) | `.result-url` / `.share-item-id` | — |
| `KeyboardHelp.vue` | `.shortcut-item kbd` | ✅ +500 |
| `ImportModal.vue` | `.submit-hint` | ✅ +500 |
| `NLQPanel.vue` | `.parsed-textarea` | — |
| `PIIIndicator.vue` | `.pii-indicator` | — |
| `CreateMemoryModal.vue` | `.submit-hint` | ✅ +500 |

所有 9 处 `font-family: monospace` → `var(--font-mono)`。3 个 kbd 关联元素补 `font-weight: 500`（与 SearchBar.hint-search / TabBar.tab-key / CommandPalette.palette-kbd 一致）。

**影响估计**:
- ID 字段（如 `mem_a1b2c3`）/ 分享 URL / NLQ 解析文本框 / 脱敏 PII 字符，全部从系统 Times/Courier → Geist mono，视觉与品牌一致
- kbd 字符渲染权重从默认 400 → 500，与既有 kbd 体系对齐（用户看不到具体差异，但视觉重量统一了）
- 验证：`grep -rn "font-family: monospace" frontend/src` 在 active 区域返回 0 结果

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors |
| `npm run build` | ✅ 2.56s，dist 完整生成 |
| `grep rgba(0,0,0,0.5) frontend/src` （排除 deprecated 与 token 定义） | ✅ 0 结果 |
| `grep font-family: monospace frontend/src` （排除 deprecated） | ✅ 0 结果 |
| 8501 服务进程 | 未触碰，仍在 serving `frontend/dist`（用户刷新即生效） |
| 后端 / 新依赖 | 无 |
| 现有功能回归 | 模态遮罩 / kbd 字符 / 字体渲染行为不变，只是颜色和字体的源从硬编码变 token |

---

## 遗留 / 下次可以做

1. **deprecated/ 目录的 monospace / rgba 收尾** — `views/deprecated/*` 还有 13 处 `font-family: monospace`，但因为是 deprecated（路由不引用），暂不动
2. **SettingsView 表单保存按钮颜色** — P41 #4 指出 `--primary` vs `--accent` 的设计决策仍未做
3. **DashboardView chart-empty 三处视觉统一** — P42 #2 仍待定
4. **unified 卡片整体升级** — P39 指出 P16 时期的设计
5. **`--shadow-elevated` 内部仍用 `rgba(0, 0, 0, 0.5)`** — 这是 token 定义本身（5 元素组成的复合阴影），暂不算"硬编码"，但如果未来要做"统一调暗阴影"决策，需拆分子 token（`--shadow-color-base`）

---

**Commit**: P43
**Files changed**:
- `frontend/src/components/Layout/AppSidebar.vue`（+1 -1）
- `frontend/src/components/Layout/CollectionEditor.vue`（+1 -1）
- `frontend/src/components/Layout/ConfirmDialog.vue`（+1 -1）
- `frontend/src/components/Layout/CreateMemoryModal.vue`（+3 -2）
- `frontend/src/components/Layout/EditMemoryModal.vue`（+1 -1）
- `frontend/src/components/Layout/ImportModal.vue`（+3 -2）
- `frontend/src/components/Layout/KeyboardHelp.vue`（+3 -2）
- `frontend/src/components/Layout/LinkCreator.vue`（+1 -1）
- `frontend/src/components/Layout/NLQPanel.vue`（+1 -1）
- `frontend/src/components/Layout/PIIIndicator.vue`（+2 -2）
- `frontend/src/components/Layout/ShareModal.vue`（+2 -2）
- `frontend/src/components/Layout/WhatsNewModal.vue`（+1 -1）
- `frontend/src/components/OnboardingTour.vue`（+1 -1）
- `frontend/src/views/MemoryDetailView.vue`（+1 -1）
- `frontend/dist/index.html` + 1 个 dist css 清理（build 产物）
