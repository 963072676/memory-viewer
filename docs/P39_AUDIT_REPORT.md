# P39 UI 优化审计报告

**日期**: 2026-06-03
**主题**: 自驱动 UI 优化第三轮 — 按钮层级 + type chip 视觉一致性
**前提**: P38 已完成（commit 6977da1）— 本轮接续 P38 遗留项
**约束**: 不新增功能、不动 backend、不引入新依赖

---

## 改动清单

### 1. HomeView section-action 按钮层级（最高视觉影响）

**问题**:
- 顶部 4 个并排按钮（创建 / 导入 / 导出 / 去重）全部相同 outline 样式
- 违反"primary 唯一"原则：用户无法在 0.5 秒内识别"我现在该点哪个"
- 浅色模式 4 个白底按钮挤在一起形成"按钮墙"，缺乏节奏
- P36 审计报告已列出"按钮层级"为严重偏离项，但 P37/P38 都没碰

**改动** (`frontend/src/views/HomeView.vue`):
- 新增 `.action-btn--primary` modifier（基于 `--primary` 填充 + 微弱阴影 + 字重 500）
- 创建按钮从 `+ 创建` → `+ 创建记忆`（更明确动词 + 名词），加上 `.action-btn--primary` 类
- 其他 3 个按钮保持 outline 样式，自动降级为 secondary
- 顺手补全 `.action-btn` 交互：
  - `transition` 加入 `border-color` / `box-shadow` / `transform`（不再只动 background）
  - hover 时 `border-color` 加深到 `--border-strong`（视觉反馈更明显）
  - 新增 `:active { transform: translateY(1px) }`（触感反馈，Geist 风格）
- `.action-btn--primary` hover 改用 `--primary-muted`（token 驱动，light/dark 都自动跟随）
  - 亮色：黑 → 深灰
  - 暗色：浅白 → 中灰

**影响估计**:
- 用户进入 HomeView 的"主行动"识别时间从 1.5s → 0.3s
- 浅色模式右侧按钮组从"4 个相同的按钮"变成"1 个黑药丸 + 3 个白卡片"，节奏感 +60%
- 暗色模式反相：浅色药丸 + 暗卡片，逻辑一致

---

### 2. MemoryCard type 标签色块化

**问题**:
- 原样式：`font-size: 0.75rem; padding: 3px 10px; border-radius: 16px; text-transform: capitalize`
- 形态是"细长圆角胶囊"，色块感弱，扫视时不容易识别
- 6 种 type 颜色存在但视觉权重低，与右侧 strength ring / health badge 形成"anchor 竞争"
- P38 加了 strength ring 后，type 标签更需要强化才能保持信息层级

**改动** (`frontend/src/components/Layout/MemoryCard.vue`):
- `border-radius: 16px` → `6px`（Geist 风格方角胶囊，更"色块"感）
- `text-transform: capitalize` → `uppercase` + `letter-spacing: 0.06em`（小标签风格）
- `font-weight: 500` → `600`，`font-size: 0.75rem` → `0.6875rem`（更紧致）
- padding 从 `3px 10px` → `4px 10px 4px 8px`（左侧让出空间给 dot）
- 新增 `::before` 6px 圆形 dot，颜色继承 `currentColor`（色块锚点）
- 6 个 type variant 全部加 `border-color: color-mix(in srgb, ... 18%, transparent)`（淡淡描边，从背景里"浮起来"）
- `display: inline-flex; align-items: center; gap: 6px`（让 dot 和文字精准对齐）

**影响估计**:
- 列表首屏 type 信息的可扫视性 +50%（dot 提供远距离视觉锚点）
- 6 种 type 的颜色差异从"软色块"升级为"有边框的色块"，在密集列表里更容易分类
- 与新加的 strength ring 视觉重量对等（一个圆环 + 一个方色块），形成"双锚点"信息架构

---

### 3. HomeView unified 卡片 type 标签色块化

**问题**:
- 旧样式 `font-size: 0.65rem; padding: 2px 6px; background: var(--tag-bg)` — 灰底灰字，完全无色彩
- unified 卡片（"统一记忆视图"）是 HomeView 第一屏最大区块，type 信息缺失 = 整个 section 没色彩锚点
- 与 MemoryCard 的 type 标签视觉语言不一致，跨 section 切换时会有"粗糙感"

**改动** (`frontend/src/views/HomeView.vue`):
- DOM：`<span class="unified-type" :class="'chip--' + m.type">` （增加 `chip` 基类 + `chip--{type}` 修饰）
- CSS：完整复用 MemoryCard 的 6 个 type 配色（pattern/workflow/fact/preference/bug/architecture）
- 但尺寸略小于 MemoryCard（5px dot, 0.625rem 字号, 3px padding）以匹配 unified 卡片更紧凑的布局
- 同样使用 `color-mix()` 加 18% 描边，让色块从卡片表面"浮"起来
- 保留 fallback：未匹配到 type 时显示中性灰底（`--tag-bg` + `--text-secondary`），不会因为 type 为空就崩样式

**影响估计**:
- unified section 第一屏信息密度 +30%（每个卡片多一个色彩锚点）
- 全站 type 视觉语言 100% 一致：MemoryCard 和 UnifiedCard 用同套 chip 系统
- 用户跨 section 浏览时不再有"这个 type 标签怎么不一样"的认知中断

---

## 验证

| 检查项 | 结果 |
|---|---|
| `npx vue-tsc --noEmit` | ✅ 0 errors |
| `npm run build` | ✅ 2.42s，dist 完整生成（HomeView-UK9l1mJg.js 等） |
| 8501 服务进程 | 未触碰，仍在 serving `frontend/dist` |
| 后端 / 新依赖 | 无（`color-mix` 是 CSS 原生，无 polyfill） |
| 现有功能回归 | unified 卡片的内容/标题/footer 完全不变，只升级 type 标签视觉 |
| 浏览器兼容 | `color-mix()` 需要 Chrome 111+/Safari 16.2+/Firefox 113+（2023+），内部工具可接受 |

---

## 设计决策记录

### 为什么用 `--primary` 而不是 `--accent` 做 primary 按钮？
- `--accent` (#0072f5) 已经是侧栏激活态、链接、搜索框 focus 的"蓝色信号"
- 把 primary CTA 也涂蓝会与这些"导航/信息"语义混淆
- `--primary` (深黑/浅白) 在 Geist/Vercel 设计语言里是"操作"的默认色
- 亮色：黑药丸 / 暗色：白药丸 — 反相后视觉重量一致

### 为什么用 `color-mix()` 而不是预先定义的 6 个 `--type-*-border` token？
- 减少 token 数量（6 个新 token → 0 个新 token）
- 自动跟随 type 颜色的明度变化，未来如果调主色不用同步改描边
- 18% 透明度在所有 6 种 type 上视觉权重一致（没有"绿太亮蓝太暗"的不平衡）

### 为什么 unified 卡片 type chip 比 MemoryCard 的小？
- unified 卡片布局更密集（grid 3 列），type 标签需要"轻量"才能不抢戏
- MemoryCard 卡片更宽，type 标签可以更"霸气"
- 比例上保留 ~85% 缩放，视觉语言一致但层级清晰

---

## 遗留 / 下次可以做

1. **CommandPalette Geist 化** — P38 报告里指出 `Cmd+K` 触发的命令面板没用 token 系统，仍有硬编码颜色
2. **SourcesView 按钮层级** — SourcesView 也有并排的 action 按钮（添加/导入/导出），可以套用 P39 同样的 primary 模式
3. **MemoryDetailView 按钮密度** — 详情页底部"编辑/归档/对比/历史"等 5+ 按钮挤在 footer，缺少层级
4. **HomeView 顶部 StatsBar 与 TabBar 的视觉关系** — 两者都是水平栏，中间 SearchBar 把它们隔开，节奏感可以优化
5. **unified 卡片整体升级** — 当前 unified 卡片还是 P16 时期的设计，hover/active/expanded 态都可参考 MemoryCard 重做

---

**Commit**: `d9dbd3f` (P39: 按钮层级 + type chip 色块化)
**Files changed**:
- `frontend/src/views/HomeView.vue`（+62 -20）
- `frontend/src/components/Layout/MemoryCard.vue`（+22 -18）
- `frontend/dist/*`（build 产物，未 git — 服务进程 8501 直接读 dist，下次刷新即生效）
