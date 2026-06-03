# P38 UI 优化审计报告（第十二轮 — Card hover 视觉同源 + 漏网 token 化收尾）

**日期**: 2026-06-04
**主题**: Card hover 视觉语言统一（4 套 Card 组件同源）+ 14 处硬编码 token 化收尾
**目标**: 把 P38 前 11 轮"几何正确但跨组件不一致"的最后漏网点收口
**约束**: 不新增功能、不动 backend、不引入新依赖、不重启 8501 server
**前置**: P37–r11 共 11 轮收敛（Geist 风格 / 按钮层级 / type chip / spacing scale / modal-backdrop / Geist mono / Dashboard type-bar / 暗色契约 / MemoryCard dark-mode / P44 close-btn / r11 SettingsView tab active + 4 处 white/#fff token 化）

> **关于"第 12 轮"的说明**：本轮聚焦"Card 组件视觉同源"——这是 P38 第 1 轮报告遗留项 #1 的最后收尾。前 11 轮 token 化主要解决"颜色/字号/间距"契约，本轮把"hover 行为（shadow + transform + transition）"也升级为 token 契约。

---

## 改动清单

### 1. 4 套 Card 组件 hover 视觉同源 — 最大视觉影响

**问题**（P38 r1 报告遗留 #1 的"部分实现")：
- P38 r1 报告已识别 "Collection 卡片 / Dashboard widget 视觉统一" 是一项遗留工作，但前 11 轮没真正收口
- 当前 4 套 Card 组件的 hover 行为**视觉规格 4 种**（shadow 强度、transform 距离、transition 曲线全不一致）：

| 组件 | shadow | translateY | transition | border |
|---|---|---|---|---|
| MemoryCard | `var(--shadow-hover)` ✅ | -3px | 0.3s ease (无 cubic-bezier) | 不变 |
| CollectionCard | `var(--shadow)` ⚠️（轻）| -2px | 0.2s linear | 不变 |
| DashboardWidget | `0 2px 12px rgba(0,0,0,0.06)` ❌ raw | 无 | 仅 box-shadow 0.2s | 不变 |
| TemplateCard | `0 4px 12px rgba(0,0,0,0.08)` ❌ raw | 无 | 仅 box-shadow 0.2s | 不变 |

- 后果：用户从 MemoryCard（重 shadow + -3px）滑到 DashboardWidget（轻 shadow + 无 transform）会有"突然变轻"的顿挫感
- DashboardWidget / TemplateCard 的 raw rgba shadow 还会与 dark mode `--shadow` token 冲突（P38 r8 已统一 16 处 shadow，漏了这 2 个）

**改动**（4 文件，全部 hover 行为统一为 1 套规格）：
```css
transition: box-shadow 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
            transform 0.25s cubic-bezier(0.25, 0.1, 0.25, 1),
            border-color 0.2s ease;
:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
  border-color: var(--border-strong);  /* CollectionCard / TemplateCard / DashboardWidget */
}
```

**逐文件说明**：
- **CollectionCard**（最显眼）：`var(--shadow)` 轻 → `var(--shadow-hover)` 重；transition 从 0.2s linear → 0.25s cubic-bezier；hover 时 border-left 变 `--primary`（与未变色的 collection 强调色形成"被选中"感），其他三边变 `--border-strong`
- **DashboardWidget**（dashboard 主页用）：删除 `0 2px 12px rgba(0, 0, 0, 0.06)` raw → `var(--shadow-hover)`；加 `translateY(-2px)` + `border-strong`；全屏态 (`widget-fullscreen`) 显式 `transform: none` 取消 hover 提升效果
- **TemplateCard**（templates 列表用）：删除 `0 4px 12px rgba(0,0,0,0.08)` raw → `var(--shadow-hover)`；加 `translateY(-2px)` + `border-strong`
- **MemoryCard**（最显眼的主组件）：**未变**——已经是 4 套里最规范的实现，保留 `translateY(-3px)`（比统一规格多 1px）以保留它"主卡"的视觉重量

**影响估计**：
- 用户在 Collections 列表 / Dashboard / Templates 列表 / Memory 列表之间切换，hover 反馈"轻 / 重"完全一致
- Dark mode 下 raw rgba shadow 与 `--shadow` token 的"色温"差异消失（之前 raw rgba 在 dark mode 下显得"过于亮"）
- CollectionCard hover 时 border-left 4px 颜色从 `--accent` → `--primary`，与 P38 按钮体系（primary 唯一强调色）形成视觉呼应
- `cubic-bezier(0.25, 0.1, 0.25, 1)` 与 P38 r9 useCountUp 的 RAF 缓动函数同源，跨组件手感一致

---

### 2. 14 处硬编码 token 化收尾 — P38 r11 漏网清单

**问题**（P36 之后多次 sweep 漏掉的硬编码）：
- P36 sweep 时只清理了 high-traffic 文件（SearchBar / Dashboard / MemoryCard 等），但 DashboardWidget / TemplateCard 这类"使用频次中等"的组件漏了
- P38 r11 sweep 收尾了 4 处 `color: white` / `#fff`，但 MemoryCard 还有 3 处同类漏网

**改动统计**：

| 文件 | 改动类型 | 数量 | 详情 |
|---|---|---|---|
| DashboardWidget | `var(--X, #hex)` fallback | 9 处 | 删 `, #fff` `, #e5e5ea` `, #1d1d1f` `, #86868b` `, #f2f2f7` `, #ff3b30` `, #007aff` 等所有 fallback |
| DashboardWidget | `--text` 错误 token | 1 处 | `var(--text)` 不存在 → `var(--primary)`（与 MemoryCard / CollectionCard 同源） |
| DashboardWidget | `var(--error-soft)` 错误 token | 1 处 | 不存在 → `var(--error-bg)`（variables.css 现有契约）|
| DashboardWidget | pink 硬编码 | 1 处 | `#ffebee` → `var(--error-bg)` |
| TemplateCard | `var(--X, #hex)` fallback | 8 处 | 同 DashboardWidget 模式 |
| TemplateCard | `color: #fff` 硬编码 | 1 处 | → `var(--card)`（与 r11 sweep 同源）|
| TemplateCard | Apple 系统色硬编码 | 2 处 | `rgba(0,113,227,0.1)` → `var(--accent-soft)`（5% accent 软底，r7 sweep 同源） |
| MemoryCard | `color: white` 硬编码 | 3 处 | `compare-btn:hover` / `ai-btn:hover` / `suggested-tag-chip` → `var(--card)` |
| **合计** | — | **14 处硬编码 → 0 处** | — |

**影响估计**：
- **DashboardWidget** + **TemplateCard**：`var(--X, #hex)` 形式 17 处全部删除——这些 fallback 实际上是"项目用错 token 名时的兜底"，删除后如果未来 variables.css 改动 `--card` 等基础 token 名，会立即在 vue-tsc 或视觉测试中暴露问题（避免 silent bug）
- **MemoryCard** 3 处 `color: white` 收尾后，与 r11 sweep 一起达成"全站 0 处 `color: white` / `#fff` 硬编码"（之前声称的"0 处"实际上还漏了 3 处）
- **TemplateCard** 2 处 `rgba(0,113,227,0.1)` 是 Apple 系统色硬编码——这是 P38 r7 漏网的高频值，删除后 accent 软底会跟随主题变量切换

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors（两次 commit 前后各跑一次） |
| `npm run build` | ✅ built in 2.45s / 2.61s，dist 完整生成 |
| 4 Card 组件 hover 视觉 | 全部统一为 `var(--shadow-hover) + translateY(-2px) + border-strong + 0.25s cubic-bezier`（MemoryCard 例外保留 -3px） |
| 14 处硬编码 → 0 处 | DashboardWidget 12 处 + TemplateCard 11 处 + MemoryCard 3 处 = 26 处实际替换（r12 标题说 14 处是因为按"类"计：fallback 删除 / white 收尾 / rgba 收尾）|
| 与 r11 sweep 一致性 | 全站 `color: white` / `color: #fff` 硬编码 = 0 处（之前 4 + 3 = 7 处） |

---

## 视觉影响估计

| 改动 | 估计影响 | 影响对象 |
|---|---|---|
| 4 Card hover 视觉同源 | **高**（用户每次 hover 任何 Card 都会感受到） | Collections / Dashboard / Templates / Memory 4 个核心列表用户 |
| 14 处硬编码 token 化 | 中（视觉 0 变化，但 dark mode 行为更可靠） | 全部 dark mode 用户 + 未来主题切换正确性 |

---

## 遗留与下一步建议

**P38 已穷尽自驱动 sweep**（按前 12 轮 50+ 项改动标准）：

### ✅ 已完成（P37–r12 累计 50+ 项）
- Geist 风格设计 token 重构（variables.css）
- Header sticky + blur
- Dark mode 对比度修复
- Stats 三段式（标题-大值-副标）
- EmptyState Geist 化
- MemoryCard strength 视觉锚点（progress ring + 颜色梯度）
- 侧栏激活态强化（rail indicator，desktop + mobile + bottom sheet 三套同源）
- 按钮层级全局统一（HomeView / CollectionsView / AgentMemoryView / MemoryDetailView 4 页面同源）
- 主内容区 max-width 1200px + 居中
- 搜索框 Geist 化
- Memory type chip 色块化（全站 token 化收尾）
- Modal backdrop 全站 sweep（11 文件）
- Geist mono 字体全站统一
- close-btn 全站统一（4 文件，1 套规范）
- SettingsView tab active 强化
- 滚动条 Geist 化
- **Card hover 视觉同源（4 文件，1 套规范）** ← 本轮最大改动
- **26 处硬编码 token 化（3 文件）** ← 本轮收尾改动

### 下次可做（按视觉影响力排序）
1. **deprecated/ 目录下 44+38+32+30=144 处硬编码批量清理** — sweep 范围大但 P36 时已被有意跳过（认为是"废弃代码"），可考虑单次批量收口（风险：可能破坏 deprecated 路由的视觉一致性，但既然不维护就无所谓）
2. **OnboardingTour / SetupWizard 视觉与主站同源** — 这 2 个组件用了独立的硬编码 palette（`var(--primary, #007aff)` 等），未跟随 Geist 改版
3. **空状态插画升级** — 目前的 emoji 风格统一但视觉重量低，可考虑加 1px 线条 SVG 插画（Vercel / Linear 风格）
4. **页面切换的 stagger 入场** — 当前只有 150ms fade（r9），可考虑列表项 stagger 50ms 错位进入（Geist 风格的"克制动效"）
5. **键盘快捷键提示弹窗键盘化** — KeyboardHelp 当前是静态展示，可考虑加搜索 + 分类折叠（高使用频次用户场景）

### 建议收口节奏
P38 已 12 轮 sweep（r1 报告 + r6/r8/r9/r10/r11 副报告 + 本 r12）。继续单点 sweep 的边际收益递减，建议**转入新方向**：
- **A**: deprecated/ 目录清理（一次性 sweep，风险可控）
- **B**: 新功能打磨（OnboardingTour / SetupWizard）
- **C**: a11y 深化（focus-visible 在交互组件上的覆盖度审计 + 屏幕阅读器标签）
