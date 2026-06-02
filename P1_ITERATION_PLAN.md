# Memory Viewer v2 — P1 迭代计划

> **版本**: 1.0
> **日期**: 2026-05-29
> **作者**: pm-orchestrator
> **基于**: PM_SPEC.md v2.2 + 当前代码审查

---

## 0. 迭代概述

P1 迭代聚焦**记忆管理闭环**（搜索→编辑→删除）和**数据可观测性**（统计仪表盘），同时保障数据新鲜度（缓存自动刷新）。

**目标**：让用户能完整地查询、修改、删除记忆，并通过统计面板理解记忆全貌。

**预计工期**：5-7 个工作日（单人全栈）

---

## 1. 当前状态评估

### 已完成
| 项目 | 状态 | 说明 |
|------|------|------|
| F-07 后端搜索参数扩展 | ✅ 已完成 | `search.py` 已支持 `strength_min/max`, `date_from/date_to` 参数 |
| Swagger 文档 (F-04) | ✅ 已完成 | `/api/docs` 可访问 |
| 分页+排序 API | ✅ 已完成 | `/api/agentmemory/paginated` 支持 sort/order/type |
| 记忆创建 API (POST) | ✅ 已完成 | P0 已实现 |
| 记忆导入/导出 API | ✅ 已完成 | P0 已实现 |

### 未完成
| 项目 | 说明 |
|------|------|
| F-07 高级搜索前端 | FilterPanel 组件未开发 |
| F-08 记忆编辑 | 前后端均未开始 |
| F-09 记忆删除 | 前后端均未开始 |
| F-10 统计仪表盘 | 前后端均未开始 |
| F-11 缓存自动刷新 | 后端未开始 |

---

## 2. 功能任务拆分

### 2.1 F-07 高级搜索面板

**描述**：可视化过滤器面板，支持类型多选、时间范围 picker、strength 滑块、数据源切换。

**现状**：后端 API 已支持全部过滤参数，仅需前端开发。

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F07-T1 | 创建 FilterPanel.vue 组件：类型多选 checkbox、时间范围 date picker、strength 范围滑块、数据源 radio | 前端 | `components/FilterPanel.vue` | 3h |
| F07-T2 | 扩展 Pinia search store：新增 filterState（types[], dateRange, strengthRange, source） | 前端 | `stores/search.ts` 或 `stores/ui.ts` | 1h |
| F07-T3 | 集成 FilterPanel 到 SearchBar 区域：展开/收起动画，与搜索联动 | 前端 | `views/HomeView.vue`, `components/SearchBar.vue` | 2h |
| F07-T4 | 搜索结果 URL 同步：filter 参数写入 query string，支持分享/刷新保留 | 前端 | `router/index.ts`, store | 1h |
| F07-T5 | 无关键词纯过滤模式：后端 search API 支持 `q` 为空时仅按条件过滤 | 后端 | `routers/search.py`, `services/search.py` | 1.5h |
| F07-T6 | 测试：FilterPanel 组件单测 + 集成测试 | 测试 | `tests/components/FilterPanel.spec.ts` | 1.5h |

**验收标准 (AC)**：
- **AC-F07-1**：面板展开后显示 4 类过滤器（类型多选、时间范围、strength 滑块、数据源切换），布局清晰不拥挤
- **AC-F07-2**：选择类型多选（如 pattern + fact）后，结果仅包含选中类型的记忆
- **AC-F07-3**：设置时间范围（如 2026-05-01 ~ 2026-05-28）后，结果仅包含该时间段的记忆
- **AC-F07-4**：拖动 strength 滑块到范围 [5, 10]，结果仅包含 strength 在该区间的记忆
- **AC-F07-5**：切换数据源（agentmemory / hermes / all），结果按数据源过滤
- **AC-F07-6**：过滤条件可通过 URL query params 保留，刷新页面后过滤状态不丢失
- **AC-F07-7**：纯过滤模式（无搜索关键词）正常返回结果

---

### 2.2 F-08 记忆编辑

**描述**：支持编辑已有 agentmemory 条目的 content、concepts、strength。

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F08-T1 | 新增 `PUT /api/agentmemory/{memory_id}` 端点 | 后端 | `routers/agentmemory.py` | 1h |
| F08-T2 | 实现 service 层：按 ID 查找 → 更新字段 → 原子写入 JSON | 后端 | `services/agentmemory.py` | 2h |
| F08-T3 | 定义 Pydantic 请求模型 `AgentMemoryUpdateRequest`（content, concepts, strength 可选） | 后端 | `models/agentmemory.py` | 0.5h |
| F08-T4 | 创建 EditMemoryModal.vue：表单预填当前值，支持修改 content/concepts/strength | 前端 | `components/EditMemoryModal.vue` | 3h |
| F08-T5 | MemoryCard 增加"编辑"按钮（图标），点击打开 EditModal | 前端 | `components/MemoryCard.vue` | 1h |
| F08-T6 | API client 封装 `updateMemory(id, data)` | 前端 | `api/agentmemory.ts` | 0.5h |
| F08-T7 | 编辑成功后自动刷新列表，Toast 提示 | 前端 | `stores/agentmemory.ts` | 0.5h |
| F08-T8 | 测试：PUT API 单测 + EditModal 组件测试 | 测试 | `tests/test_agentmemory.py`, `tests/components/` | 1.5h |

**验收标准 (AC)**：
- **AC-F08-1**：点击卡片"编辑"按钮，弹出模态框，表单预填当前 content、concepts、strength
- **AC-F08-2**：修改 content 后提交，列表中对应卡片内容更新
- **AC-F08-3**：修改 strength 值（如 5→8）后提交，卡片显示新 strength
- **AC-F08-4**：concepts 标签支持增删（输入框 + 回车添加，点击×删除）
- **AC-F08-5**：不修改任何字段直接提交，记忆数据不变（幂等）
- **AC-F08-6**：编辑失败（如网络错误）时显示错误提示，不丢失用户输入
- **AC-F08-7**：PUT API 返回更新后的完整记忆对象

---

### 2.3 F-09 记忆删除

**描述**：支持删除单条/批量删除 agentmemory 条目，含确认对话框和审计记录。

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F09-T1 | 新增 `DELETE /api/agentmemory/{memory_id}` 端点 | 后端 | `routers/agentmemory.py` | 1h |
| F09-T2 | 新增 `DELETE /api/agentmemory/batch` 端点（接收 ID 列表） | 后端 | `routers/agentmemory.py` | 1h |
| F09-T3 | 实现 service 层删除逻辑 + 审计日志（记录 who/when/what 到 `cache/audit.json`） | 后端 | `services/agentmemory.py` | 2h |
| F09-T4 | 创建 ConfirmDialog.vue 通用确认对话框组件 | 前端 | `components/ConfirmDialog.vue` | 1.5h |
| F09-T5 | MemoryCard 增加"删除"按钮，点击弹出确认框（显示记忆标题） | 前端 | `components/MemoryCard.vue` | 1h |
| F09-T6 | 批量删除：列表页增加 checkbox 多选 + 批量删除按钮 | 前端 | `views/HomeView.vue`, `components/CardGrid.vue` | 2h |
| F09-T7 | API client 封装 `deleteMemory(id)` 和 `deleteMemoriesBatch(ids)` | 前端 | `api/agentmemory.ts` | 0.5h |
| F09-T8 | 删除成功后 Toast 提示 + 列表自动刷新 | 前端 | `stores/agentmemory.ts` | 0.5h |
| F09-T9 | 测试：DELETE API 单测 + 审计日志验证 | 测试 | `tests/test_agentmemory.py` | 1.5h |

**验收标准 (AC)**：
- **AC-F09-1**：点击卡片"删除"按钮，弹出确认对话框，显示记忆标题
- **AC-F09-2**：确认删除后，记忆从列表消失，显示"已删除" Toast
- **AC-F09-3**：取消删除，记忆不受影响
- **AC-F09-4**：批量选择 3 条记忆 → 点击批量删除 → 确认 → 3 条全部移除
- **AC-F09-5**：删除操作写入审计日志（`cache/audit.json`），包含 memory_id、title、deleted_at 时间戳
- **AC-F09-6**：DELETE API 返回 `{ success: true, deleted_id: "xxx" }`
- **AC-F09-7**：删除不存在的 ID 返回 404

---

### 2.4 F-10 统计仪表盘

**描述**：可视化图表展示记忆分布——按类型饼图、按时间折线图、按 profile 柱状图、strength 分布直方图。

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F10-T1 | 新增 `GET /api/stats` 端点，返回聚合统计数据 | 后端 | `routers/stats.py` (新文件) | 2h |
| F10-T2 | 实现统计 service：按类型/按时间/按 profile/strength 分桶聚合 | 后端 | `services/stats.py` (新文件) | 2h |
| F10-T3 | 注册 stats router 到 main.py | 后端 | `app/main.py` | 0.25h |
| F10-T4 | 前端安装图表库（推荐 Chart.js + vue-chartjs，轻量适配） | 前端 | `package.json` | 0.25h |
| F10-T5 | 创建 DashboardView.vue 页面 | 前端 | `views/DashboardView.vue` | 1h |
| F10-T6 | 实现 4 个图表组件：TypePieChart, TimeLineChart, ProfileBarChart, StrengthHistogram | 前端 | `components/charts/` 目录 | 4h |
| F10-T7 | Vue Router 新增 `/dashboard` 路由 + 导航入口 | 前端 | `router/index.ts`, `App.vue` | 0.5h |
| F10-T8 | 统计数据 store（Pinia）+ 自动加载 | 前端 | `stores/stats.ts` | 1h |
| F10-T9 | 测试：/api/stats API 单测 + 数据正确性验证 | 测试 | `tests/test_stats.py` | 1.5h |

**验收标准 (AC)**：
- **AC-F10-1**：访问 `/dashboard` 页面，4 个图表正确渲染
- **AC-F10-2**：饼图显示各类型（pattern/fact/preference/bug/workflow/architecture）的条数占比
- **AC-F10-3**：折线图显示按月/周的记忆创建趋势
- **AC-F10-4**：柱状图显示各 profile 的 hermes memory 条数
- **AC-F10-5**：直方图显示 strength 0-10 的分布（各区间条数）
- **AC-F10-6**：图表在数据为空时显示友好的空状态提示
- **AC-F10-7**：`GET /api/stats` 响应时间 < 500ms（~100 条数据）

---

### 2.5 F-11 缓存自动刷新

**描述**：后端定时任务，每 30 分钟自动执行 `fetch_agentmemory` 更新缓存。

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F11-T1 | 集成 APScheduler 到 FastAPI lifespan | 后端 | `app/main.py` | 1.5h |
| F11-T2 | 实现定时任务：调用 `fetch_agentmemory.py` + 重新加载缓存 | 后端 | `app/scheduler.py` (新文件) | 1.5h |
| F11-T3 | 可配置化：环境变量 `CACHE_REFRESH_INTERVAL`（默认 30 分钟） | 后端 | `app/config.py` | 0.5h |
| F11-T4 | `/api/health` 增加 `last_refresh_at` 和 `next_refresh_at` 字段 | 后端 | `routers/health.py` | 0.5h |
| F11-T5 | requirements.txt 添加 `apscheduler` 依赖 | 后端 | `requirements.txt` | 0.1h |
| F11-T6 | 测试：定时任务触发验证 + health 端点新字段 | 测试 | `tests/test_health.py` | 1h |

**验收标准 (AC)**：
- **AC-F11-1**：服务启动后，日志显示"scheduler started, refresh interval: 30min"
- **AC-F11-2**：手动调用 `/api/health`，返回 `last_refresh_at`（ISO 时间戳）
- **AC-F11-3**：`CACHE_REFRESH_INTERVAL` 环境变量可自定义间隔（单位：分钟）
- **AC-F11-4**：刷新过程中 API 服务不中断（旧缓存在刷新完成前继续服务）
- **AC-F11-5**：刷新失败时记录错误日志，不影响服务可用性

---

## 3. 任务依赖关系

```
F-07 高级搜索 ──────────────┐
F-08 记忆编辑 ──────────────┤
F-09 记忆删除 ──────────────┼── 可并行开发（互不依赖）
F-10 统计仪表盘 ────────────┤
F-11 缓存自动刷新 ──────────┘

内部依赖：
F-08-T4 (EditModal) 依赖 F-08-T1~T3 (PUT API 先完成)
F-09-T4 (ConfirmDialog) 可被 F-08 复用（通用组件）
F-10-T6 (图表组件) 依赖 F10-T4 (安装 Chart.js)

跨功能依赖：
F-07 的 FilterPanel 可复用 F-09 的 ConfirmDialog 设计风格
F-10 DashboardView 导航需与现有 Tab 协调
```

**推荐开发顺序**（单人串行）：

```
Phase 1 (Day 1-2): F-11 缓存自动刷新 → F-09 记忆删除
  理由：F-11 最简单（纯后端），F-09 次之（DELETE API + 简单 UI）
  产出：ConfirmDialog.vue 通用组件（后续复用）

Phase 2 (Day 3-4): F-08 记忆编辑
  理由：复用 Phase 1 的 ConfirmDialog 和 DELETE 的 API 模式
  产出：EditMemoryModal.vue

Phase 3 (Day 4-5): F-07 高级搜索面板
  理由：纯前端工作，后端已完成
  产出：FilterPanel.vue

Phase 4 (Day 5-7): F-10 统计仪表盘
  理由：最复杂的前端工作（4 个图表），放最后避免阻塞其他功能
  产出：DashboardView + 4 个图表组件
```

---

## 4. 工作量汇总

| 功能 | 后端 | 前端 | 测试 | 合计 | 复杂度 |
|------|------|------|------|------|--------|
| F-07 高级搜索面板 | 1.5h | 7h | 1.5h | **10h** | 🟡 中 |
| F-08 记忆编辑 | 3.5h | 5h | 1.5h | **10h** | 🟡 中 |
| F-09 记忆删除 | 4h | 5h | 1.5h | **10.5h** | 🟡 中 |
| F-10 统计仪表盘 | 4h | 6.75h | 1.5h | **12.25h** | 🟡 中 |
| F-11 缓存自动刷新 | 4h | 0 | 1h | **5h** | 🟢 低 |
| **合计** | **17h** | **23.75h** | **7h** | **47.75h** | — |

> 约 **6 个工作日**（按 8h/天计算）

---

## 5. 风险评估

| # | 风险 | 影响 | 概率 | 缓解措施 |
|---|------|------|------|---------|
| R1 | **JSON 文件并发写入冲突** | 编辑/删除/自动刷新同时写入 `agentmemory.json` 可能导致数据损坏 | 🟡 中 | 使用文件锁（`fcntl.flock`）+ 原子写入（tmp + rename）；写入前备份 |
| R2 | **Chart.js 包体积过大** | 影响首次加载速度 | 🟢 低 | 使用 tree-shaking；按需引入图表类型；或改用更轻量的 `uPlot` |
| R3 | **自动刷新与用户操作冲突** | 用户正在编辑时缓存被刷新，编辑的数据可能被覆盖 | 🟡 中 | 刷新前检查是否有进行中的写操作；或刷新仅更新 hermes-memory，agentmemory 以本地修改为准 |
| R4 | **审计日志文件增长** | `audit.json` 长期运行后文件过大 | 🟢 低 | P1 先不做日志轮转；P2 考虑按日期分文件或 SQLite |
| R5 | **搜索纯过滤模式性能** | 无关键词时后端需全量扫描 + 过滤 | 🟢 低 | 当前 ~100 条数据无性能问题；后续可加索引 |

---

## 6. 技术决策记录

| 决策 | 选项 | 选择 | 理由 |
|------|------|------|------|
| 图表库 | Chart.js / ECharts / D3.js | **Chart.js + vue-chartjs** | 轻量（~60KB gzipped）；Vue 3 官方集成；满足当前 4 种图表需求 |
| 定时任务方案 | APScheduler / asyncio / cron | **APScheduler** | 与 FastAPI 集成成熟；支持 lifespan 管理；配置灵活 |
| 审计日志存储 | JSON 文件 / SQLite / 日志文件 | **JSON 文件** (`cache/audit.json`) | 与现有数据存储一致；读写简单；当前操作量不需要数据库 |
| 编辑字段范围 | 全字段可编辑 / 仅 content+strength | **content, concepts, strength** | title 一般由 Agent 自动生成，不建议手动修改；type 变更罕见且影响分类一致性 |

---

## 7. 验收检查清单（Sprint Review 用）

- [ ] F-07：FilterPanel 展开/收起正常，4 类过滤器独立工作且可组合
- [ ] F-07：URL 携带 filter 参数时页面自动应用过滤
- [ ] F-08：编辑 → 保存 → 列表刷新 → 卡片显示新内容（端到端闭环）
- [ ] F-08：concepts 标签输入体验流畅（添加/删除/去重）
- [ ] F-09：单条删除 + 批量删除均正常
- [ ] F-09：确认对话框显示记忆标题，取消不删除
- [ ] F-09：`cache/audit.json` 有正确的审计记录
- [ ] F-10：4 个图表在 `/dashboard` 正确渲染
- [ ] F-10：图表数据与实际记忆数据一致
- [ ] F-11：服务启动日志显示定时任务注册
- [ ] F-11：`/api/health` 包含 `last_refresh_at` 字段
- [ ] 所有新增 API 端点出现在 `/api/docs` Swagger 文档中
- [ ] 前端构建无 TypeScript 错误（`npm run build` 成功）
- [ ] 后端测试全部通过（`pytest` 成功）
