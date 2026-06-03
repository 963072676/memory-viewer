# P38 UI 优化审计报告（第十一轮 — 收尾 sweep）

**日期**: 2026-06-04
**主题**: SettingsView tab active 强化 + `color: #fff`/`white` token 化收尾 + CompareView concept-tag 风格升级
**目标**: 终结 P44 收尾后剩余的 token 契约违例 + 补一个高频交互组件的 active 反馈
**约束**: 不新增功能、不动 backend、不引入新依赖、不重启 8501 server
**前置**: P37–P44 共 10 轮收敛（Geist 风格 / 按钮层级 / type chip / spacing scale / modal-backdrop / Geist mono / Dashboard type-bar / 暗色契约 / MemoryCard dark-mode / P44 close-btn + shadow token + chart-empty）

> **关于"第 11 轮"**：前 10 轮记录在 `P38_AUDIT_REPORT.md` 与 `_r6/_r8/_r9/_r10` 副文件。本报告为**第 11 轮 sweep**，延续同一编号；如再开新轮可继续追加。

---

## 改动清单

### 1. SettingsView `.settings-tab` active 状态强化 — 高频交互视觉升级

**问题**（P44 #2 leftover）:
- SettingsView 4 个 tab（数据源 / Webhook / 通知 / 关于）切换时，激活态只有一个 2px 蓝色 border-bottom + accent 文字，**视觉重量弱于**同站其他 active 态：
  - desktop sidebar nav-item: 3px left rail + `--accent-subtle` bg
  - mobile bottom tab: 3px top rail + `--accent-subtle` bg
  - mobile bottom sheet: filled accent bg + white text
  - TabBar (all/hermes/agentmemory): 白色 card shadow + 主色文字
- SettingsView tab 的"只改 border + color"在 4 个 tab 横向并列时缺少"被选中"的卡片感，用户需要盯着 border 才能确认激活
- `transition: all 0.2s` 是 anti-pattern（影响所有属性，未来加 box-shadow 会被无意识改变）

**改动** (`frontend/src/views/SettingsView.vue`, 1 个 CSS 块):
- `.settings-tab`：加 `position: relative`、`border-radius: 6px 6px 0 0`（顶部圆角，与下方 `.settings-tabs` 的 1px border-bottom 形成"内嵌"视觉而非"贴边"）
- `.settings-tab`：transition 改为显式 `color 0.15s, background 0.15s, border-color 0.15s`（Geist 风格逐项 transition）
- `.settings-tab.active`：加 `background: var(--accent-soft)`（5% accent 蓝底，与 sidebar nav-item 的 `--accent-subtle` 视觉同源）+ `font-weight: 600`（与 nav-item active 一致）

**统一后的规格**:
```css
.settings-tab.active {
  color: var(--accent);
  border-bottom-color: var(--accent);
  background: var(--accent-soft);   /* 5% accent bg — 新增 */
  font-weight: 600;                  /* 新增 */
}
```

**影响估计**:
- 4 个 SettingsView tab 的激活态视觉重量提升（从"只有下划线"到"有底色 + 加粗 + 下划线"三层）
- 与 desktop sidebar nav-item、移动端 bottom tab 的"accent-soft bg"语言完全一致
- `transition: all` → 显式三属性，0 性能开销，但避免未来新增属性时"被无意识动起来"
- 用户进入 SettingsView 后无需盯着 2px border 找激活 tab — 加粗字重 + 浅蓝底让 active tab"跳"出来
- 移动端 4 tab 横向滚动场景：active 状态在滚动时仍有清晰视觉锚点

---

### 2. 全站 `color: #fff` / `color: white` 硬编码 token 化收尾 — P44 漏网清单

**问题**（P44 sweep 漏掉的最后一波硬编码）:
- P44 只清理了 `SettingsView` 的 2 处 `color: white`，但**全站仍有 4 处同类硬编码**散布在 3 个文件
- 这些 button 全部处于"按钮底色 = accent/primary 饱和色 + 文字 = white"的标准场景，逻辑上与 P44 清理的 SettingsView 一致
- `color: #fff` 比 `color: white` 更刺眼（违反"项目统一用 var(--card) token"原则）

**改动** (4 处 1-token 替换):

| 文件 | 行 | 上下文 | 旧 | 新 |
|---|---|---|---|---|
| `SearchBar.vue` | 191 | `.mode-toggle--semantic:hover` (semantic mode 切换按钮 hover) | `color: #fff` | `color: var(--card)` |
| `AgentMemoryView.vue` | 508 | `.filter-clear:hover` (FilterPanel 清空按钮 hover) | `color: white` | `color: var(--card)` |
| `CompareView.vue` | 135 | `.action-btn.primary` (对比页主操作按钮) | `color: white` | `color: var(--card)` |
| `CompareView.vue` | 166 | `.concept-tag`（见 item 3，整段重写） | `color: white` | `color: var(--accent)` |

**影响估计**:
- 全站 `color: white` / `color: #fff` 硬编码 → 0 处（与 P44 收尾时声明的"全站 0 处"目标完全对齐）
- 4 处 token 替换，0 视觉变化（语义保留，token 跟随主题）
- 与既有 P44 决策一致：`SearchBar` 之前用 `#fff`、其他文件用 `white`，现在全部统一为 `var(--card)`，未来如果项目决定"按钮文字色 = primary 而非 card"，4 处一起改即可

---

### 3. CompareView `.concept-tag` 风格升级 — 视觉语言对齐

**问题**（与 token 化同时发现的"坏代码"）:
- `.concept-tag` 旧实现：`background: var(--accent) + color: white + opacity: 0.8`
  - **问题 1**: `color: white` 硬编码（P44 漏网，本轮已修）
  - **问题 2**: `opacity: 0.8` 是**反模式** — 与父元素 `.item-card` 的 `background: var(--bg)` 发生 alpha 混合，结果色相偏灰、失去 accent 本色
  - **问题 3**: 圆角 `8px` + `font-size: 0.65rem` + `padding: 2px 6px` 视觉上"胖圆" — 与 MemoryCard `.card-type` (P39 type chip 体系) 的"瘦方"风格不统一

**改动** (`frontend/src/views/CompareView.vue`, 1 段 CSS 重写):
- 删 `opacity: 0.8`（改用 `color-mix()` 18% 模拟 Geist "1 级 border"）
- 删 `color: white` + `background: var(--accent)`，改用 `color: var(--accent) + background: var(--accent-soft)`
- 圆角 `8px` → `6px`（与 `.card-type` 保持一致）
- 加 `border: 1px solid color-mix(in srgb, var(--accent) 18%, transparent)`（与 P39 type chip 的"1 级 border"语言一致）

**统一后的规格**:
```css
.concept-tag {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 6px;
  background: var(--accent-soft);   /* 5% accent bg */
  color: var(--accent);              /* accent 文字 */
  border: 1px solid color-mix(in srgb, var(--accent) 18%, transparent);
}
```

**影响估计**:
- CompareView 三栏（left-only / common / right-only）item 卡片底部的 concept-tag 现在与全站 type chip 视觉同源（MemoryCard `.card-type`、HomeView `.source-badge`、P39 type chip 体系）
- 旧版 `opacity: 0.8` 导致的"色相偏灰"问题消除（accent 色在 bg 5% 上更纯净）
- `concept-tag` 不再是"加粗小圆色块"而是"细描边小方标签"，与右侧的 `.item-type` (灰色小方标签) 视觉权重对等
- 全站 `.concept-tag` 类用得不多（仅 CompareView），但视觉统一性提升对未来"在 AgentMemoryView 加 concept-tag"留下正确模板

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors |
| `npm run build` | ✅ built in 2.57s，dist 完整生成 |
| 全站 `color: white` / `color: #fff` 硬编码 | ✅ 0 处（注释除外） |
| SettingsView active 视觉 | ✅ accent-soft bg + 加粗 + 下划线 三层 |
| CompareView concept-tag | ✅ 改用 accent-soft + accent 文字 + 18% border，与 P39 type chip 体系一致 |
| 8501 服务进程 | 未触碰，仍在 serving `frontend/dist`（用户刷新即生效） |
| 后端 / 新依赖 | 无（仅使用既有 `--accent-soft` / `color-mix()` 工具） |
| 现有功能回归 | SettingsView 4 tab 切换逻辑不变；SearchBar mode toggle 行为不变；AgentMemoryView 筛选清空逻辑不变；CompareView 主按钮 / concept-tag 渲染不变 |

---

## 视觉影响估计

| 改动 | 估计影响 | 影响对象 |
|---|---|---|
| SettingsView tab active 强化 | 中（用户每次进入 Settings 都会看到） | 4 个 SettingsView tab 切换用户 |
| `color: #fff`/`white` token 化 | 低（视觉无变化，纯契约统一） | 代码可维护性提升 |
| CompareView concept-tag 风格升级 | 中（CompareView 三栏底部 tag 从"色块"变"标签"） | 对比页用户、概念浏览用户 |

---

## 遗留与下一步建议

**P38 自驱动循环（11 轮）已完成** — 6 个 P38 起点目标（MemoryCard 视觉锚点 / 侧栏 active / 按钮层级 / max-width / 搜索框 Geist 化 / type 标签色块化）从 P37 启动到 P44 收尾已基本闭合。

### 本轮未触及的 P44 leftovers（可作为下一轮起点）

1. **DashboardView `StatsBar` 与 `TabBar` 在小屏的合并** — 移动端两个独立组件横/竖向切换造成"折叠"逻辑复杂
2. **CollectionsView / SourcesView 顶部缺少 StatsBar 类的"信息行"** — 与 HomeView 视觉不一致，跨页面切换有"少一块"的感觉
3. **deprecated/ 目录 monospace 收尾** — 13 处 `font-family: monospace`（P43 #1），属于死代码清理
4. **统一所有 view 的"首屏顶部"组件布局** — HomeView 有 SearchBar/QuickAccessBar/StatsBar/TabBar 四件套，但其他 view 直接进内容

### 本轮收尾的"硬编码"问题（已 100% 解决）

- ✅ `color: white` / `color: #fff` → 0 处
- ✅ `transition: all` → 0 处（显式三属性 transition）
- ✅ `background: white` / `background: #fff` 硬编码 → 0 处（之前 P41/P42 已清理，本轮未发现新增）
- ✅ Apple 系统色硬编码 (`#007AFF` 等) → 0 处（P38 r7 已清理）

---

## 设计决策记录

### 为什么 SettingsView tab 不改用 sidebar 风格的"left rail"？
- SettingsView 是 **水平 4 tab**（横向排列 + overflow-x scroll），不是 sidebar 风格的"垂直列表"
- 强行套用 3px left rail 在水平 tab 上不自然（左 rail 会与 tab 边距重叠）
- 选择"accent-soft bg + 圆角 + 加粗"是"水平 tab 选中态"的标准模式（vs vertical "left rail" 模式）
- 两种模式共存的逻辑：维度 = 排布方向

### 为什么 `concept-tag` 改用 `color-mix()` 18% border 而不是定义新 token？
- 与 P39 type chip 体系保持一致（`type-pattern` / `type-workflow` 等 6 个 chip 都用 `color-mix(in srgb, var(--type-X-text) 18%, transparent)`）
- 不新增 token = 零认知负担，未来 chip 体系扩展时直接复用同一模式
- 18% 是个"刚好能看见"的 border 强度（< 10% 几乎隐形，> 25% 显得脏）

### 为什么 `transition: all` 要改显式三属性？
- `all` 影响所有可动画属性（color / background / border-color / box-shadow / transform / opacity...）
- 未来如果加 `box-shadow` 给 active tab 一个"上浮"效果，开发者可能意识不到"box-shadow 也会动"
- 显式列三属性 = 强制开发者"逐项决定要不要动"，符合"显式优于隐式"
- 0 性能开销（CSS 引擎处理相同）

---

**Commit**: P38 r11 (`e39354b`)
**Files changed**:
- `frontend/src/views/SettingsView.vue`（+5 -1，1 个 CSS 块，2 行新增样式）
- `frontend/src/components/Layout/SearchBar.vue`（+1 -1，1-token 替换）
- `frontend/src/views/AgentMemoryView.vue`（+1 -1，1-token 替换）
- `frontend/src/views/CompareView.vue`（+14 -2，1-token 替换 + 1 段 CSS 重写）
- `frontend/dist/*`（build 产物，asset hashes 更新）
