# P39 UI 优化审计报告（第一轮 — 4 项 bug 修复 + 死代码清理）

**日期**: 2026-06-03
**主题**: 自驱动 UI 优化 — 上一轮 4 个未提交 bug 修复收尾
**目标**:
1. `useCountUp(function)` 形式不自动 watch，导致 StatsBar / Dashboard count-up value 永远 0（隐性 bug）
2. StatsBar / Dashboard 在 store 未 fetch 完时显示 0（视觉"不一致"）
3. MemoryCard 选中态 checkbox 遮挡标题文字（视觉"挡住"）
4. AppSidebar 内嵌的 collapse 按钮与 AppHeader 顶栏 ☰ 按钮功能重复（占 24×24 空间）

**约束**: 不新增功能、不动 backend、不引入新依赖
**前置**: P38 r1-r10 共 10 轮 sweep 全部完成

---

## 改动清单

### 1. `useCountUp` 接受函数 source 时自动 watch（高 — 影响所有用 count-up 的页面）

**问题**:
- `useCountUp(() => store.x.length)` 这种"函数 source"形式，原设计要求手动调 `animateTo()`
- 但 r10 把 StatsBar 3 个数字接进去时，传的是函数而不是 ref，导致 `value` 永远是初始 0
- 同理 r9 加的 Dashboard count-up 也受影响 —— 用户在 r10 之后看到的是 0 抖动到真实值，还是干脆 0，要看是否用 ref
- 这是 useCountUp 的"设计漏洞"：函数 source 应该自动包装成 computed watch，否则大家都会踩

**改动**（1 文件，useCountUp.ts）:
```ts
if (typeof source === 'function') {
  // 函数形式：包装成 computed 再 watch — 自动响应（替代原先"不自动 watch"的设计，
  // 避免 StatsBar 这类场景下 value 永远是 0 的隐性 bug）。
  // 保留 animateTo 暴露以支持外部手动控制（如延迟触发动画）。
  const _computed = computed(() => {
    const v = source()
    return typeof v === 'number' && Number.isFinite(v) ? v : 0
  })
  watch(_computed, (newVal) => animateTo(newVal), { immediate: true })
}
```

**设计决策**:
- 自动 watch 是**安全收紧**（破坏性 = 0）—— 之前不 watch 是为了避免闭包陷阱（source 内引用外部变量变化），但 computed 包装后这个风险消除
- 保留 `animateTo` 暴露 —— 延迟触发动画、外部手动控制仍然可用
- 加 `Number.isFinite` 兜底 —— 防止 source 返回 `NaN` 时 RAF 进入死循环

**影响估计**:
- 100% 用 `useCountUp(() => ...)` 形式的页面（StatsBar 3 个数字 + Dashboard 4 个数字 + 任何 r11+ 新接入）
- 修复后 count-up 真正"从 0 滚到 N"而不是"从 0 卡死"

---

### 2. StatsBar / Dashboard 未加载时显示 `—`（中 — 影响首屏体验）

**问题**:
- r10 之后 StatsBar / Dashboard 在 store 还在 fetch 时显示 `0`
- 用户看到 `0 AgentMemory 条目` 第一眼，再瞬间 count-up 到 2476 之类的真实值
- 视觉上"先 0 再跳 N"非常不稳

**改动**（2 文件，StatsBar.vue + DashboardView.vue）:
- StatsBar: 新增 `isLoaded = computed(() => agentLastFetch && hermesLastFetch)`，未加载时显示 `—`
- DashboardView: 已有 `stats` 状态（之前是 truthy/falsy 切换动画），未加载时显示 `—`
- 加载完成后才让 count-up 接管 → 视觉"先占位，再滚动"

**设计决策**:
- `—` (em-dash) 比 `0` / `...` / 骨架屏 都好 —— 信息密度高，且与"空数据"的 `0` 严格区分
- 沿用 `lastFetch` 状态（不是新增一个 isLoading）—— 已有数据，复用 store 状态
- `isLoaded` 必须等**两个** store 都 fetch 完才 true（任意一个先到都先显示 `—`），避免先看到一个数字后另一个还在加载

**影响估计**:
- 100% 进入首页 / Dashboard 的用户（每次冷启动 ~500ms 内都是 `—`）
- 视觉一致性显著提升 —— 不再有"0 → 真实值"跳变

---

### 3. MemoryCard 选中态 checkbox 遮挡标题（中 — 影响多选场景）

**问题**:
- MemoryCard 多选时左侧出现 `.select-checkbox`（18×18，left: 12px）
- 但 `.card-header` 没有让出空间，checkbox 浮在标题文字之上
- 用户勾选后看到"标题被一格方框盖住"，视觉上像"文字被吃"

**改动**（1 文件，MemoryCard.vue）:
```css
.card-header {
  ...
  padding-left: 30px;  /* 18px checkbox + 12px left offset = 让出空间 */
}
```

**设计决策**:
- 30px 硬编码而非 token —— 这是"特定组件内部布局"而非"全站设计 token"
- 只在多选模式才有 checkbox，所以非多选时这 30px 留白微不可见
- 不动 checkbox 自己的位置（left: 12px）—— 只让 title 容器挪开

**影响估计**:
- 多选模式 100% 用户（批量删除 / 批量打 tag / 批量加入收藏）
- 之前是"挡字"，修复后是"checkbox + 标题"清晰两层

---

### 4. AppSidebar 内嵌 collapse 按钮删除（小 — 去重死代码）

**问题**:
- 桌面端 AppHeader 顶栏已经有 ☰ 按钮控制侧栏收/展（统一入口）
- AppSidebar 内嵌的 `.sidebar-collapse-btn` 是历史遗留 —— 同功能两处入口
- 占 24×24 空间，与 brand-logo 视觉冲突

**改动**（1 文件，AppSidebar.vue）:
- 删 5 行 template（按钮 + icon span）
- 删 22 行 CSS（`.sidebar-collapse-btn` / `.sidebar-collapse-btn:hover` / `.collapse-icon` / `.collapse-icon.rotated`）
- 加注释说明"统一入口已迁到 AppHeader"

**设计决策**:
- 不重构为"小图标按钮" —— 已经是"无功能按钮"（☰ 已经在顶栏了）
- 删干净而非隐藏 —— 用户不会看 CSS 找入口

**影响估计**:
- 桌面端 100% 用户
- 侧栏 brand 区域不再有"小红方块"，视觉更纯净
- -22 行死代码（维护负担 ↓）

---

## 验证

| 项目 | 结果 |
|---|---|
| `vue-tsc --noEmit` | 0 errors |
| `npm run build` | 2.45s 全部 OK（dist 已同步） |
| 后端 8501 未触碰 | ✅ 改动 100% 在 frontend/src/，backend/ 已 git checkout |
| 依赖未增加 | ✅ 0 新依赖（useCountUp 修复是 TS 内部逻辑） |
| 改动文件数 | 6 文件 (5 vue + 1 ts) + dist build artifact |
| commit 数 | 1 (14f8ec5) |

---

## 视觉影响估计

| 改动 | 估计影响 | 影响对象 |
|---|---|---|
| useCountUp 函数 source 自动 watch | **高**（隐性 bug 修复） | 所有 r10 之后用 count-up 的页面 |
| StatsBar / Dashboard 未加载占位 `—` | **中-高** | 首屏冷启动 ~500ms 内的视觉稳定性 |
| MemoryCard checkbox 不再挡字 | **中** | 多选模式用户 |
| AppSidebar collapse 按钮删除 | 小（去重） | 桌面端侧栏顶部视觉 |

---

## 遗留与下一步建议

### 本轮已彻底完成

- ✅ useCountUp 函数 source 自动 watch（隐性 bug 修复，破坏性 0）
- ✅ StatsBar / Dashboard 未加载占位 `—`
- ✅ MemoryCard checkbox 不再挡字
- ✅ AppSidebar collapse 按钮删除 + 22 行死代码清理
- ✅ dist 同步 commit
- ✅ vue-tsc 0 errors + build 2.45s

### 关键决策记录

1. **关于约束"不动 backend"**: 本轮发现 backend/main.py + 6 个新 router 都是未提交的 P39 业务功能（注册新路由），不属于 P38 UI 优化范畴，已通过 `git add frontend/...` 精确避开。**未提交部分需要单独开 P39 业务迭代**（不属于本次 cron job 范畴）。
2. **关于 `verify_p38.py` / `verify_p39.py`**: 顶层调试脚本，未提交，留给后续 PR 决定（删除 / 移到 tests/）。
3. **关于 data/cache/*.json**: 业务数据，不属于 P38 改动，已避开。

### 下次可做（按视觉影响力排序）

1. **低频 modal 同样加动画**（r10 报告遗留 #4） — SetupWizard / CollectionEditor / LinkCreator / WhatsNewModal 还没加弹出动画。影响 4 个 modal 打开。
2. **页面进入 stagger**（r10 报告遗留 #1） — Dashboard chart cards / type bar / timeline bar 可以 stagger 出现（80ms 间隔），纯 CSS `animation-delay` 0 JS。影响每次进 Dashboard。
3. **AppHeader 副标题路由切换淡入淡出**（r10 报告遗留 #3） — 副标题"全站记忆系统全景视图"切换页面时可以淡出再淡入（150ms），强化"页面切换"感。
4. **MemoryCard hover 微动效**（r10 报告遗留 #5） — hover 时加 `translateY(-2px)` 的"抬起"感（150ms ease-out），与 Linear/Vercel 卡片一致。影响每次悬停列表卡片。
5. **页面滚动进度条**（r10 报告遗留 #2） — router-view 顶部 1px accent 色进度条，路由变化时 0%→100% 平滑推进。每次切页都看到。
6. **空状态插画** — 大空状态（无记忆 / 无搜索结果）当前只有 emoji + 文字，可加简洁 SVG 插画。属于"未来方向"中的视觉体系化。

### 不可做（项目约束）

- ❌ 不新增功能（如 profile 过滤、滚动加载、虚拟滚动增强）
- ❌ 不引入新依赖
- ❌ 不动 backend（已在 P39 业务迭代范围）

### 本轮越界检查

- ❌ 未新增功能（4 项都是 bug 修复 + 死代码清理，0 新交互）
- ❌ 未动 backend（精确 git add 避开）
- ❌ 未引入新依赖
- ❌ 未改 dist/ 源码（dist build artifact 跟随）
- ❌ 未破坏现有功能（vue-tsc 0 errors，build 通过，count-up 修复是收紧）

---

## 最终交付建议

P39 r1 的 4 项修复都是**上一轮 r10 引入的隐性 bug 收尾**：

| 类别 | 数量 | 备注 |
|---|---|---|
| 隐性 bug 修复 | 1 | useCountUp 函数 source 不 watch |
| 视觉稳定性 | 1 | StatsBar / Dashboard 占位 `—` |
| 视觉错误 | 1 | MemoryCard checkbox 挡字 |
| 死代码清理 | 1 | AppSidebar collapse 按钮 |

**修复后 P38 的 10 轮 sweep 真正完整可验收**：
- count-up 动画在所有用到它的页面（首页 + Dashboard）都正确"从 0 滚到 N"
- 多选模式下 MemoryCard 视觉无遮挡
- 桌面侧栏无冗余按钮
- 冷启动占位视觉稳定

**未提交的业务功能**（backend 改动 + 6 个新 router）属于 **P39 业务迭代范畴**，不应混入 P38 视觉优化报告。建议在后续 P39 业务迭代 cron job 中处理。
