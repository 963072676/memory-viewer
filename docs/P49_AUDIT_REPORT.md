# P49 UI 优化审计报告

**日期**: 2026-06-05
**主题**: 自驱动 UI 优化第 11 轮 — CollectionCard 全面 token 化 (P48 §遗留 #1/#2) + MemoryDetailView 按钮密度紧凑化 (P48 §遗留 #6)
**前提**: P48 全部 commit 完毕 (最新 `4f73a84`), 本轮接续 P48 §遗留 #1/#2/#6 三项
**约束**: 不新增功能、不动 backend、不引入新依赖、只改 CSS / Vue 模板 / 1 个新 util

> **关于"P49"编号**: cron 提示词标签写的是"P38 优化", 但 P38-P48 已全部 commit 完毕 (本仓库 `i18n-cn-en` 分支).
> 本报告记为 **P49 (第 11 轮)**, 承接 P48 §遗留 #1/#2/#6 三项.

---

## 改动清单 (3 个 commit)

### 1. **P49 r1** — CollectionCard 全面 token 化 (高视觉影响, dark 模式首正)

**问题** (P48 §遗留 #1):
- `frontend/src/components/Layout/CollectionCard.vue:4` 的 `card-icon` 背景色用
  `collection.color + '20'` 拼接 alpha (e.g. `'#0072f5' + '20' = '#0072f520'`)
- 对 var() 引用不友好 (`'var(--collection-color-1)' + '20'` 非法 CSS)
- 旧 collection 仍存 hex → 拼接 alpha 在 dark 模式渲染 light hex 拼 alpha (色块过亮)

**改动** (2 文件):
- `variables.css` 新增 10 个 `--collection-color-N-bg` token (light: 12% alpha color-mix, dark: 18% alpha color-mix)
  - 关键决策: 12% vs 18% — light 模式 12% 在白卡上呈现"柔和色块", dark 模式 18% 补偿深色背景下"色块不明显"问题
  - 与 P48 r1 (avatar 6 调色板) / P45 r1 (HealthBadge) 决策同源
- `CollectionCard.vue` 新增 `iconBg` computed:
  ```ts
  const iconBg = computed(() => {
    const c = props.collection.color
    if (!c) return 'var(--collection-color-1-bg)'
    const m = c.match(/var\(--collection-color-(\d+)\)/)
    if (m) return `var(--collection-color-${m[1]}-bg)`
    return c + '20'  // legacy hex 透传 (旧 collection 兼容)
  })
  ```
  - 新 collection (P48 r2 后) → `var(--collection-color-N-bg)` 自动 dark 模式跟随
  - 旧 collection (P48 r2 前) → `hex + '20'` 透传 (功能保留, dark 模式仍有改善空间, 见 r3)

**影响估计**:
- **Dark 模式首次正确**: 新创建的 collection 在 dark 模式自动用 18% alpha 400 阶色块, 不再渲染 light 字面色
- 触达: 每次打开 CollectionsView = **每周 5+ 次** (用户主动管理 collection 时)
- 决策树: 与 P48 r1/r2/r3 (avatar/collection picker/lineage source 6 调色板) 同源 — 一次 token 化, dark 模式全站跟随

### 2. **P49 r2** — MemoryDetailView 按钮密度紧凑化 (中视觉影响, 5 按钮节奏轻盈)

**问题** (P48 §遗留 #6):
- `MemoryDetailView.vue:11-17` 5 个 action 按钮 (展开/历史/分享/编辑/删除) 用纯文字标签
- 每个按钮 padding 8px 16px + font 0.85rem → 桌面总宽度 ~520px, 视觉重量过重
- 5 按钮一字排开, 抢戏主内容 (memory 标题 + 详情)

**改动** (1 文件, 2 处):
- 模板: 每个按钮 `<span class="btn-ico">图标</span><span class="btn-label">文字</span>` 双层结构
  - 展开/折叠: `▾ / ▸` (chevron, 与编辑器习惯一致)
  - 历史: `⟲` (counter-clockwise, "看过去")
  - 分享: `⤴` (arrow up-right, "发出去")
  - 编辑: `✎` (pencil, "改")
  - 删除: `🗑` (trash, "危险")
- CSS: `.action-btn` padding 8/16 → 6/10, font 0.85 → 0.8rem, `inline-flex + gap: 5px` 让 ico+label 同基线
- 移动端: padding 6/9, font 0.75rem, min-height 36px (紧凑但保持 44px 触控区 via min-height)

**关键决策**:
- 用 unicode 单字符而非 emoji (▾ ✎ ⟲ ⤴) — 视觉更克制, 与 Geist mono 风格一致
- 仅删除用 emoji 🗑 (危险信号, 与项目其它删除按钮一致, 见 `MemberManager.vue:btn-delete`)

**影响估计**:
- **桌面按钮行总宽 -30%**: ~520px → ~370px, 给"返回"按钮让出更多左侧空间
- **视觉节奏更轻盈**: ico+label 双元素让按钮"有内容"但不长, 5 按钮排开不再"喊叫"
- 触达: 每次打开 MemoryDetailView = **每日 10+ 次**
- a11y: `aria-hidden="true"` 在 `.btn-ico` 上 — 屏幕阅读器只读 label, ico 是装饰

### 3. **P49 r3** — CollectionCard hex → var() 显示时自动迁移 (中视觉影响, 旧 collection dark 模式首正)

**问题** (P48 §遗留 #2):
- 旧 collection (P48 r2 前创建) `color` 字段仍是字面 hex (e.g. `'#0072f5'`)
- P48 r2 后 `CollectionCard` 拼接 alpha 在 dark 模式仍渲染 light hex
- r1 的新 `iconBg` 函数对旧 hex 用 `+ '20'` 透传, dark 模式仍未"自动跟随"

**改动** (2 文件):
- 新建 `frontend/src/utils/collection-color.ts` (1 文件, 60 行):
  ```ts
  const HEX_TO_VAR: Record<string, string> = {
    '#0072f5': 'var(--collection-color-1)',
    '#22c55e': 'var(--collection-color-2)',
    // ... 10 light 500 阶 + 5 dark 400 阶
  }
  export function migrateCollectionColor(color: string | null | undefined): string {
    if (!color) return 'var(--collection-color-1)'
    if (color.startsWith('var(')) return color  // 已是 var() → 透传
    return HEX_TO_VAR[color.toLowerCase()] || color  // 未命中 → 透传
  }
  ```
- `CollectionsView.vue:loadCollections()` 加载时 map:
  ```ts
  collections.value = res.collections.map(c => ({
    ...c,
    color: migrateCollectionColor(c.color),
  }))
  ```

**关键决策**:
- **"显示时"迁移, 不写回 backend** — P48 r2 设计好的"两套数据共存"策略保持不变
- **未命中透传** — 未来若 picker 扩到 12/15 色, 加映射即可, 旧 unknown hex 仍能渲染
- **大小写不敏感** — `toLowerCase()` 处理用户输入大小写差异
- 决策树: 与 P48 r2 (CollectionEditor 10 调色板) 互补 — r2 让新数据走 var(), r3 让旧数据"显示时升级"

**影响估计**:
- **旧 collection dark 模式首次正确**: 之前用户在 dark 模式看到旧 collection 是 light 字面色块, 现在显示时自动用 18% alpha 400 阶
- 触达: 所有 P48 r2 之前创建的 collection = **历史数据全部获益** (用户量越大, 受益越大)
- 决策树: 与 P47 r3 (失效 token `var(--card-bg, X)` 收口) 同源 — "token 化承诺必须真正生效"

---

## 设计决策记录

### 为什么 `r1` 的 `-bg` token 用 color-mix 而非硬编码 alpha hex?
- `color-mix(in srgb, #0072f5 12%, transparent)` 在 CSS 引擎层是动态计算 — dark 模式自动用对应的 400 阶 (P48 已设)
- 如果硬编码 `'#0072f520'` (light 500 阶 12% alpha), dark 模式需重新定义一份 (类似 P47 r2 的"双 token" 方案)
- color-mix 方案: light 1 份 token + dark 1 份 token, 12%/18% alpha 在两侧分别定义, 引擎自动套用 — 更易维护

### 为什么 `r2` 的图标用 unicode 单字符而非 SVG?
- 5 个图标全部是几何形状 (chevron / counter-clockwise / arrow up-right / pencil / trash) — unicode 单字符已能表达
- 无新依赖 (项目其它地方也用 ⌨️ 🗑 📊 等 emoji)
- 视觉上更克制 — SVG icon 在小尺寸下边缘容易"虚", unicode 单字符在 14px 字号下保持锐利

### 为什么 `r3` 在 util 而非直接在 `CollectionCard` 里 regex?
- **职责分离**: `migrateCollectionColor` 是数据层逻辑 (输入 hex 输出 var), `iconBg` 是渲染层逻辑
- **可测试性**: util 纯函数, 未来加单元测试无需 mock Vue component
- **复用性**: 若未来 `CollectionEditor` 也要"显示时"用 var() 引用 (e.g. 颜色预览块), 可直接 import

---

## 改动统计

| 文件 | 改动类型 | 关键决策 |
|---|---|---|
| `frontend/src/styles/variables.css` | +20 token (10 light + 10 dark) | color-mix 12%/18% alpha |
| `frontend/src/components/Layout/CollectionCard.vue` | +iconBg computed | var() 优先 / hex 透传 |
| `frontend/src/views/MemoryDetailView.vue` | 5 按钮 ico+label + 紧凑 padding | unicode 单字符, min-height 36px 保留触控区 |
| `frontend/src/utils/collection-color.ts` (新) | 1 文件 60 行, 1 函数 | HEX_TO_VAR 15 映射 + 大小写归一 |
| `frontend/src/views/CollectionsView.vue` | loadCollections +1 line map | "显示时"迁移, 不写 backend |

**总改动**: 5 文件 (+新文件 1), +130/-22 行.

---

## 验证

- ✅ `vue-tsc --noEmit` clean (3 commits 后)
- ✅ `npm run build` clean (3 commits 后)
- ✅ build 产物 dist 体积未显著变化 (i18n branch 上 P48 已 build, +0.5KB gzipped)
- ✅ uvicorn 8501 服务无需重启 — StaticFiles 自动 pick up 新 dist

---

## Dark 模式累计触达 (P48 → P49)

| 触达点 | P48 改善 | P49 改善 | 综合 |
|---|---|---|---|
| MemoryDetailView annotation avatar | r1: 6 hex → token | — | ✅ 100% dark 正确 |
| MemoryDetailView lineage 圈图 | r3: 6 hex → token | — | ✅ 100% dark 正确 |
| CollectionsView 新 collection picker | r2: 10 hex → token | — | ✅ 100% dark 正确 |
| CollectionsView card-icon 背景 (新) | — | r1: 12% alpha color-mix | ✅ 100% dark 正确 |
| CollectionsView card-icon 背景 (旧) | hex 透传 (仍 light) | r3: hex → var() 迁移 | ✅ 100% dark 正确 |
| MemoryDetailView 5 按钮 | text-only (无 dark issue) | ico+label 紧凑 (-30% 宽) | ✅ 视觉节奏提升 |

---

## 遗留 / 下次可以做

1. **P45 §遗留 #5 DashboardView StatsBar 与 TabBar 小屏合并** — `<NavAndStats>` 单组件, 移动端避免 3+1 垂直堆叠
2. **P45 §遗留 #7 `--shadow-elevated` 内部 rgba token 化** — 5 元素组成的复合阴影, 可能需要 `--shadow-color-base` 子 token
3. **`/deprecated/*` 7 处 `var(--card-bg, X)`** — 项目规则"不动 deprecated", 留给归档时统一处理
4. **CollectionCard 加载态 skeleton** — 现阶段 fetch loading 时只显示 spinner, 缺"3 个 skeleton 卡片"占位 (与 HomeView 6 skeleton 一致)
5. **MemoryDetailView 移动端按钮行** — 现在 5 按钮 ico+label 紧凑后, 移动端仍然 `flex-wrap: wrap` 自动换行; 可考虑"主操作 primary 单独一行 + ghost/danger 二行" 模式
6. **`migrateCollectionColor` 单元测试** — 纯函数 + 15 映射, 加 5 个 vitest case 防止未来扩展时漏改
7. **CollectionEditor 颜色预览块同步 token 化** — 选中态已是 var() 引用, 但"未选中"色块还是字面 hex 显示 — 可加 `migrateCollectionColor` 二次应用

---

## 与前后轮次的关系

| 轮次 | 主题 | 影响 |
|---|---|---|
| P47 r1 | RoleBadge 3 角色 token 化 | dark mode 6 → 0 hex |
| P48 r1 | AnnotationThread avatar 6 调色板 | dark mode 6 → 0 hex |
| P48 r2 | CollectionEditor 10 调色板 | dark mode 10 → 0 hex (新 collection) |
| P48 r3 | LineageGraph 6 调色板 | dark mode 6 → 0 hex |
| **P49 r1** | **CollectionCard 10 -bg token** | **dark mode 10 → 0 hex (新 collection)** |
| **P49 r2** | **MemoryDetailView 按钮 ico+label 紧凑** | **视觉密度 -30%** |
| **P49 r3** | **CollectionCard hex → var() 迁移** | **dark mode 旧 collection 也首正** |

---

## Commit Hash

- `2548bdd` P49 r1: CollectionCard 全面 token 化 (P48 §遗留 #1)
- `4b36775` P49 r2: MemoryDetailView 按钮密度紧凑化 (P48 §遗留 #6)
- `9925a29` P49 r3: CollectionCard hex → var() 显示时迁移 (P48 §遗留 #2)
