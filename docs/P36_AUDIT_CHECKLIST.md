# P36 — Memory Viewer UI 差异对比清单

> **方法**：对照 P35 调研报告与当前 8501 实测截图，识别偏离 / 改进点
> **截图来源**：`/tmp/zfsv3/nvme14/18845560182/data/Code/memory-viewer-design-iter/screenshots/`
> **时间**：2026-06-03

---

## 8 大确认的视觉问题（来自截屏 + vision 评审）

| # | 问题 | 严重度 | 影响范围 |
|---|---|---|---|
| 1 | **Header 与 body 完全无视觉分割**（同色 + 无 border） | 🔴 高 | 全站 |
| 2 | **Dark mode 卡片/header/背景差异仅 1-5 像素** | 🔴 高 | dark 模式全站 |
| 3 | **Light mode 整体饱和度 ≈ 0**（除侧栏 0.22） | 🟡 中 | 视觉无锚点 |
| 4 | **首屏上半空洞**（30% 空间浪费） | 🟡 中 | HomeView |
| 5 | **Card 缺视觉锚点**（strength 44 孤立，type 标签扁平） | 🟡 中 | MemoryCard |
| 6 | **首次访问 3 个 modal 叠加**（z=2000/9998/9999） | 🔴 高 | Onboarding |
| 7 | **19 张卡片垂直堆叠 7.4 屏**（无虚拟滚动/分页提示） | 🟡 中 | HomeView |
| 8 | **无图表 / 无 Dashboard 数据可视化** | 🟡 中 | Dashboard 概念空 |

---

## 对照 P35 模式的偏离点

### ✅ 已合规（无需改）
- Apple SF Pro 字体已配置
- Type 标签已有语义色（pattern/workflow/fact/preference/bug/architecture）
- 圆角统一为 `--radius: 12px`
- Dark mode 存在

### ❌ 严重偏离（需优先修）
| 模式 | 现状 | 应做 |
|---|---|---|
| **Header 边界** | 与 body 同色无 border | 底边 1px border + sticky blur |
| **Card 层次** | 466×176 信息密度低 | 增加 visual hierarchy (icon + meta strip + footer) |
| **Dark 对比度** | 卡片 vs 背景差 4px | 卡片 `#1c1c1e` vs bg `#000` |
| **按钮层级** | 多按钮并存无主次 | primary 唯一 + secondary outline + ghost |
| **空状态** | "暂无记忆数据"一行 | EmptyState 组件 + 插画/CTA |

### ⚠️ 部分合规（渐进修）
| 模式 | 现状 | 优先级 |
|---|---|---|
| **8pt 间距** | 多数合规但有 `p-3` `gap-3` 等 12px（合规）| P38 |
| **tabular-nums** | stats 数字未对齐 | P38 |
| **Title Case 按钮** | "创建" "导入" 偏动词 | 暂不强制（中文） |
| **StatusDot ≤10px** | 当前为 ring + percent | 接受 |

---

## P37 优化目标（第一轮）

**聚焦最有视觉冲击的 4 项**（只动 CSS/布局，不新增功能）：

### 优化 1: Header 视觉边界
- 加 `border-bottom: 1px solid var(--border)` 
- 加 `backdrop-filter: blur(20px) saturate(180%)`
- 提升 `--header-bg` 半透明
- 改 `position: sticky; top: 0; z-index: 100`

### 优化 2: Dark mode 对比度修复
- dark bg: `#1d1d1f` → `#0a0a0a`（接近纯黑）
- dark card: `#282829` → `#1c1c1e`（提升层次）
- dark border: `#3a3a3c` → `#2c2c2e`（半透明感）
- light bg: `#f5f5f7` → `#fafafa`（Geist 风格）

### 优化 3: Stats 卡三段式
- 重构顶部 19/40/5 数字显示
- 改用"标题-大值-副标"三行
- 数字用 `tabular-nums` + `font-mono`
- 加 hover 反馈

### 优化 4: 空状态组件化
- 创建 `<EmptyState>` 组件（已有 EmptyState.vue）
- 加 icon + 描述 + 可选 CTA
- 替换 "暂无记忆数据" 单行

---

## 验收标准

- [ ] 8501 视觉上不再有"上半空洞"
- [ ] Header 在 light/dark 都有清晰边界
- [ ] Dark mode 卡片与背景对比度 ≥ 4.5:1
- [ ] 至少 5 个区域使用三段式 stats 卡
- [ ] 空状态不再单行显示
- [ ] 截屏对比 light + dark 双套图
- [ ] 不新增任何功能
- [ ] vue-tsc 0 errors
- [ ] vite build 成功
- [ ] git commit
