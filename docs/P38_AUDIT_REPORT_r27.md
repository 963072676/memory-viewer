# P38 UI 优化审计报告（第 13 轮 — r27 section-title 视觉锚点收尾）

**日期**: 2026-06-04
**主题**: 自驱动 UI 优化第 13 轮 — **section-title 3px accent bar 视觉锚点收尾**（5 个漏网 h2 全部补齐）
**目标**: 修复 r20 sweep 时漏掉的最后一族"section title 无视觉锚点"问题，让全站 section heading 100% 走同一视觉语言
**约束**: 不新增功能、不动 backend、不引入新依赖、不重启 8501
**前置**: P38 r1-r26 共 26 轮 sweep 已穷尽"硬编码颜色 / 视觉锚点 / 按钮 / 阅读排版 / 图表色板 / 搜索结果同源 / a11y"7 个维度

> **关于"第 13 轮"**：前 12 轮（r1-r26）记录在 `P38_AUDIT_REPORT.md` / `_r6` 到 `_r26`。本报告为**第 13 轮 — section-title 视觉锚点收尾**。

---

## 为什么从 r26 切到 section-title 收尾

cron 任务给本轮的 6 候选里：

| # | 候选 | 评估 | 决策 |
|---|---|---|---|
| 1 | MemoryCard 视觉锚点（strength ring/颜色梯度）| r15 升 38→44px + 数字 + 渐变 + r24 high-tier glow + 100% 满级环 — **已深度做透** | ❌ skip |
| 2 | 侧栏 active 状态强化 | AppSidebar 已有 3 套（desktop 左 rail / mobile 顶 rail / sheet 填充）— **已完备** | ❌ skip |
| 3 | 按钮层级全局审计 | r21/r23 完成（.action-btn 系统 + 11 modal 收口）— **已完备** | ❌ skip |
| 4 | 主内容区 max-width + 居中 | r24 完成（--content-max token）— **已完备** | ❌ skip |
| 5 | 搜索框 input Geist 化 | SearchBar.vue 已有 recessed bg + accent focus glow + semantic mode — **已完备** | ❌ skip |
| 6 | Memory type 标签色块化 | r26 收口（搜索结果 type chip 同源化）— **已完备** | ❌ skip |

**所有 6 个候选项都已饱和**。扫描 r20 sweep 范围后发现 **5 个 h2 仍缺 3px accent bar 视觉锚点**：

| 位置 | 状态 | 决策 |
|---|---|---|
| `SettingsView.vue` × 3（Webhook 配置 / 通知配置 / 关于）| ❌ 缺 class | ✅ **本轮做** |
| `HomeView.vue` line 6（搜索结果 h2）| ❌ 缺 class | ✅ **本轮做** |
| `HomeView.vue` line 144（Hermes Memory h2）| ❌ 缺 wrapper | ✅ **本轮做** |
| `HomeView.vue` line 47 / 98（统一记忆 / AgentMemory h2）| ✅ 已在 `.section-header` 父级里 | 跳过 |
| 其它 7 个 view 顶层 h2 | ✅ r20 sweep 已加 | 跳过 |

**视觉影响估计**（按 P38 12 轮 sweep 标准）：

- 5 个 h2 从"无视觉锚点"升级为"3px accent bar + 12px padding-left" → 用户在 Settings 切换 3 个 tab / HomeView 切换 3 个 section 时，**视觉锚点一致**。
- 跨 view 切换形成"section heading 都有左侧 rail"的统一视觉语言。
- 5 处都是**之前 r20 漏网的最后一族 h2**。

---

## 改动清单

### 1. `SettingsView.vue` — 3 个 h2 加 `section-title` class + 9 行 CSS

**问题**：
- 第 25 / 75 / 125 行的 h2（`🔗 Webhook 配置` / `🔔 通知配置` / `ℹ️ 关于`）**裸 h2**，无 class
- 全站 7 个 view（AgentMemory/HermesMemory/Profiles/Sources/Dashboard/Compare/Collections）顶层 h2 都用 `.section-title` class 走 3px accent bar
- **SettingsView 是唯一漏掉的 view**，3 个 tab 都用同一节流标题，**视觉锚点全缺席**

**改动**（1 文件，3 行 template + 20 行 CSS）：

```diff
-        <h2>🔗 Webhook 配置</h2>
+        <h2 class="section-title">🔗 Webhook 配置</h2>
...
-        <h2>🔔 通知配置</h2>
+        <h2 class="section-title">🔔 通知配置</h2>
...
-        <h2>ℹ️ 关于</h2>
+        <h2 class="section-title">ℹ️ 关于</h2>
```

```css
/* P38 r27: section-title 左侧 3px accent bar — 与全站 7 个 view 同源. */
.settings-panel h2.section-title {
  position: relative;
  padding-left: 12px;
}

.settings-panel h2.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--accent);
  border-radius: 0 2px 2px 0;
}
```

**视觉影响**：
- 用户进入设置页，3 个 tab（记忆源 / Webhook / 通知 / 关于）切换时，h2 左侧都有一条 3px accent 蓝色 rail
- 与 SourcesView、AgentMemoryView、ProfilesView 等 7 个 view 切换时，**section heading 视觉锚点完全一致**
- 暗色模式自动跟随 `--accent` token（dark: `#3291FF`），无额外处理

**为什么用 `.settings-panel h2.section-title` 双选择器而不是只 `.section-title`**：
- SettingsView 用 `<style scoped>`，所以 `.section-title` 在 SettingsView 作用域里未定义
- 复用 7 个 view 的 r20 模式（双选择器）保持 scoped 与设计语言兼容
- 不需要修改 scoped 范围，0 风险

### 2. `HomeView.vue` Hermes Memory h2 → 加 `.section-header` wrapper + `section-title` class

**问题**：
- 第 144 行 `<h2>Hermes Memory</h2>` **直接放在 `<section>` 里**，无 wrapper
- 上方 AgentMemory section（line 96-106）有 `.section-header` wrapper → 自动继承 r15 `.section-header h2::before` 的 3px rail
- 下方 Hermes Memory section **没有 wrapper** → 无 rail
- 同一 HomeView 内部，**两个 section 用两种 heading 表达**

**改动**（1 文件，5 行 template）：

```diff
       <!-- Hermes Memory Section -->
       <section v-if="uiStore.currentTab !== 'agentmemory'" class="section">
-        <h2>Hermes Memory</h2>
+        <div class="section-header">
+          <h2 class="section-title">Hermes Memory</h2>
+        </div>
```

**视觉影响**：
- Hermes Memory 标题与上方 AgentMemory 标题**共享同一视觉锚点**（3px accent rail + 12px padding-left）
- 用户在 HomeView 上下扫视两个 section 时，**heading 语言完全统一**
- 自动复用 HomeView 已有的 `.section-header h2` r15 CSS，0 新增 CSS

### 3. `HomeView.vue` 搜索结果 search-header h2 → `section-title` class

**问题**：
- 第 5-9 行的 `.search-header` 包含 h2 + result-count，**h2 无 class**
- 全站 7 个 view section title 都用 `.section-title` class 走 3px accent bar
- 搜索结果 h2 是 HomeView **唯一的"h2 直接放在 div 里"**用法（其他 3 个 h2 都在 section-header 父级里）

**改动**（1 文件，1 行 template + 19 行 CSS）：

```diff
       <div class="search-header">
-        <h2>{{ searchStore.searchMode === 'semantic' ? '🧠 语义搜索结果' : '搜索结果' }}</h2>
+        <h2 class="section-title">{{ searchStore.searchMode === 'semantic' ? '🧠 语义搜索结果' : '搜索结果' }}</h2>
```

```css
/* P38 r27: search-header h2.section-title 3px accent bar — 与全站 7 个 view section-title 同源.
   search-header 是 flex container, 之前 h2 没有视觉锚点, 与下方 section-header h2 系统不一致.
   flex + ::before absolute: left 0 紧贴 h2 左缘, padding-left 12px 给文字留空间. */
.search-header h2.section-title {
  position: relative;
  padding-left: 12px;
  margin-bottom: 0;  /* search-header 自己控制 margin-bottom, 避免双重 margin */
}

.search-header h2.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--accent);
  border-radius: 0 2px 2px 0;
}
```

**视觉影响**：
- 搜索结果 h2 从"裸 h2"升级为"3px accent rail"，与 HomeView 下方 AgentMemory / Hermes Memory section 标题**视觉锚点完全统一**
- 用户在 HomeView 顶部搜索结果与下方 3 个 section 之间切换时，**heading 语言完全统一**

**为什么用 `.search-header h2.section-title` 而不直接复用 `.section-header h2` 模式**：
- `.section-header` 是专用类，flex container 行为不同（`justify-content: space-between` + `align-items: center`）
- `search-header` 需要自己的 padding-left 12px + ::before 模式
- 复用 r20 模式（双选择器 + scoped 兼容）保持设计语言一致

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors |
| `npm run build` | ✅ built in 2.37s, dist 完整生成 |
| 全站 8 个 view 顶层 h2 视觉锚点覆盖率 | **10/10 = 100%**（r20 7 个 + r27 3 个；HomeView 4 个 h2 中 3 个走 section-header 父级 1 个走 search-header 自定义）|
| SettingsView 3 tab h2 视觉锚点 | 3/3 ✅ |
| HomeView Hermes Memory h2 视觉锚点 | ✅ |
| HomeView 搜索结果 h2 视觉锚点 | ✅ |
| 改动文件数 | 2（SettingsView.vue + HomeView.vue）|
| 改动行数 | template 9 行 + CSS 41 行 = 50 行净增 |
| dark mode 自适配 | ✅ 全部走 `--accent` token（dark 自动 `#3291FF`）|
| 不新增功能 | ✅ |
| 不动 backend | ✅ |
| 不引入新依赖 | ✅ |
| 不重启 8501 | ✅（dist 已刷新，8501 serve dist 自动拾取） |

### 验证命令

```bash
# 验证 SettingsView 3 h2 已加 section-title class
grep -nE 'class="section-title"' frontend/src/views/SettingsView.vue
# 期望: 3 行 (25, 75, 125)

# 验证 HomeView Hermes Memory h2 已有 section-header wrapper
grep -nB1 -A1 "Hermes Memory" frontend/src/views/HomeView.vue
# 期望: 看到 <div class="section-header"> 紧接 <h2 class="section-title">

# 验证 HomeView 搜索结果 h2 已加 section-title
grep -n "section-title" frontend/src/views/HomeView.vue
# 期望: 至少 2 行 (search-header 1 + Hermes section-header 1)

# 验证全站 view 顶层 h2 都有 section-title class
for f in AgentMemoryView HermesMemoryView ProfilesView SourcesView DashboardView CompareView CollectionsView SettingsView; do
  grep -n 'class="section-title"' frontend/src/views/$f.vue
done
# 期望: 每个 view 至少 1 行
```

---

## 视觉影响估计

| 改动 | 估计影响 | 影响对象 |
|---|---|---|
| SettingsView 3 h2 视觉锚点 | **中-高**（3 个 tab 都缺，settings 页是 admin 用户高频访问）| 所有进入设置页的用户 |
| HomeView Hermes Memory h2 视觉锚点 | **中**（HomeView 默认 tab 切换时立即可见）| HomeView 用户 |
| HomeView 搜索结果 h2 视觉锚点 | **中**（用户搜索后立即看到标题）| 搜索用户 |

合并视觉影响：**中-高**（5 个 h2 一次性收口，跨 2 个 view + 1 个组件系统）。

---

## 遗留与下一步建议

### 本轮已彻底完成（section-title 维度）

- ✅ 全站 8 个 view 顶层 h2 视觉锚点 100% 统一（10/10 个 h2 都有 3px accent bar）
- ✅ r20 sweep 漏掉的最后一族（5 个 h2）已全部补齐
- ✅ 2 文件改动，0 风险

### 仍可继续优化的方向（不属"硬伤"但视觉提升仍有空间）

1. **全站剩余 ~18 个文件 `var(--xxx, #hex)` fallback 清理**（r25 报告 §遗留 #1）— 纯技术债清理，0 视觉变化。建议 P39 专门做一次。
2. **3 个 Chart 的 SVG `<title>` / `<desc>` a11y**（r25 报告 §遗留 #5）— screen reader 用户感知图表语义。
3. **MemoryCard 在窄屏(<600px) 的 strength ring 缩小到 38px**（r26 报告 §遗留 #3）— mobile ring 显得偏大，与文字比例不协调。
4. **MemoryDetailView 的 h4 视觉重量太轻**（0.8rem uppercase 灰色，无 accent bar）— 但 h4 是 in-section 小标题，与 page-level section title 系统不同，**严格说不应硬套 section-title 模式**。可考虑加 1px subtle bottom border 或 8px bg chip 强化。
5. **search-result-card hover 时浮现 `→` 箭头**（r26 报告 §遗留 #5）— 复用 unified-card 的 `.unified-card-arrow` 设计语言扩展。

### 不可做（项目约束）

- ❌ 不新增功能
- ❌ 不引入新依赖
- ❌ 不动 backend

---

## 与前后轮次的关系

| 轮次 | 主题 | 影响 |
|---|---|---|
| r15 | 4 套 Card hover 同源 + section h2 3px accent bar (`.section-header h2` 模式) | MemoryCard / CollectionCard / DashboardWidget / TemplateCard + HomeView 3 h2 |
| r20 | section-title 视觉锚点 100% 收尾（7 个 view）| AgentMemory / HermesMemory / Profiles / Sources / Dashboard / Compare / Collections |
| **r27（本轮）** | **section-title 漏网 5 个 h2 补齐** | SettingsView 3 h2 + HomeView Hermes Memory h2 + HomeView 搜索结果 h2 |

---

## 最终交付建议

P38 r1-r27 共 27 轮 sweep 已把"硬编码颜色 / 视觉锚点 / 按钮 / 阅读排版 / 图表色板 / 搜索结果同源 / a11y / section-title"8 个维度全部收口。

本轮**第 13 轮**是 section-title 维度的"完全收尾"——r20 sweep 时漏掉的最后一族 h2（5 个）已 100% 补齐。**全站 8 个 view 顶层 h2 + HomeView 4 个 in-section h2 = 12 个 section heading 视觉锚点 100% 统一**。

下一阶段建议继续从 **UI sweep 收尾** 切换到 **a11y / 性能 / 功能完整性** 三个新维度：
- **a11y sweep**：3 个 Chart 的 SVG `<title>` / 表单 label / focus order（r14 已做 7 modal ARIA，但还有 ~12 个 view-level form 缺 label）
- **性能 sweep**：DashboardView 首屏（fetch + render < 1.5s 目标）
- **功能完整性 audit**：每个 view 的"无数据" / "错误" / "加载中" 状态覆盖率（r8 EmptyState 已 Geist 化但覆盖率不到 60%）

UI 优化已收敛到边际收益阶段。**是时候从"美化"转向"功能完整性 / 性能 / 可用性 / a11y"**。
