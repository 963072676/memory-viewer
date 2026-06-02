# Memory Viewer v2 — P2 迭代计划

> **版本**: 1.0
> **日期**: 2026-05-29
> **作者**: pm-orchestrator
> **基于**: PM_SPEC.md v2.2 + P1 迭代完成状态

---

## 0. 迭代概述

P2 迭代聚焦**用户体验增强**（暗色模式、版本更新说明、时间线视图）和**数据治理**（记忆归档、虚拟列表性能保障），同时引入**团队协作通知**（飞书 webhook）。

**目标**：提升视觉体验、大数据量性能保障、记忆生命周期管理。

**预计工期**：5-6 个工作日（单人全栈）

---

## 1. 当前状态评估

### 已完成（P0+P1）
| 项目 | 状态 | 说明 |
|------|------|------|
| P0 全部 9 项功能 | ✅ 已完成 | 排序、展开折叠、Swagger、高亮、快捷键、创建、导入、导出 |
| P1 全部 5 项功能 | ✅ 已完成 | 高级搜索、编辑、删除、统计仪表盘、缓存自动刷新 |
| 后端测试 | ✅ 41/41 通过 | 覆盖全部 P0+P1 后端 API |
| 服务运行 | ✅ 192.168.5.55:8501 | 正常提供服务 |

### 未完成（P2）
| 项目 | 说明 |
|------|------|
| F-12 版本更新说明 | 前后端均未开始 |
| F-13 暗色模式 | 前端未开始 |
| F-14 时间线视图 | 前端未开始 |
| F-15 记忆归档 | 前后端均未开始 |
| F-16 虚拟列表 | 前端未开始 |
| F-17 记忆变更通知 | 后端未开始 |

---

## 2. 功能任务拆分

### 2.1 F-12 版本更新说明

**描述**：后端提供 changelog 数据，前端 What's New Modal 在首次访问或版本更新后自动弹出，支持 markdown 渲染，localStorage 记录已读版本。

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F12-T1 | 创建 `CHANGELOG.json` 数据文件，结构：`[{version, date, changes: [{title, description, type: "feature"|"fix"|"improvement"}]}]` | 后端 | `backend/CHANGELOG.json` | 1h |
| F12-T2 | 新增 `GET /api/changelog` 端点，返回版本列表（按版本号降序） | 后端 | `routers/changelog.py` (新文件) | 1h |
| F12-T3 | 注册 changelog router 到 main.py | 后端 | `app/main.py` | 0.25h |
| F12-T4 | 创建 `WhatNewModal.vue` 组件：markdown 渲染、版本列表、关闭按钮 | 前端 | `components/WhatNewModal.vue` | 3h |
| F12-T5 | 实现版本比对逻辑：读取 localStorage `lastReadVersion`，与当前版本比较，首次或有更新时自动弹出 | 前端 | `composables/useChangelog.ts` | 1.5h |
| F12-T6 | 侧边栏新增"更新日志"入口，可手动查看历史版本 | 前端 | `components/AppSidebar.vue` 或 `AppHeader.vue` | 1h |
| F12-T7 | API client 封装 `getChangelog()` | 前端 | `api/changelog.ts` | 0.5h |
| F12-T8 | 测试：/api/changelog API 单测 | 测试 | `tests/test_changelog.py` | 1h |

**验收标准 (AC)**：
- **AC-F12-1**：首次访问页面，What's New Modal 自动弹出，显示当前版本更新内容
- **AC-F12-2**：关闭 Modal 后刷新页面，不再自动弹出（localStorage 已记录）
- **AC-F12-3**：版本号更新后再次访问，Modal 重新自动弹出
- **AC-F12-4**：变更内容支持 markdown 格式渲染（标题、列表、粗体、代码块）
- **AC-F12-5**：侧边栏点击"更新日志"可手动查看历史版本列表
- **AC-F12-6**：`GET /api/changelog` 返回按版本号降序排列的列表

---

### 2.2 F-13 暗色模式

**描述**：CSS 变量双套（Light/Dark），支持三种模式（Light/Dark/跟随系统），localStorage 持久化用户偏好。

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F13-T1 | 扩展 `variables.css`：定义 `[data-theme="dark"]` 下所有 CSS 变量（背景、文字、边框、阴影、卡片等） | 前端 | `styles/variables.css` | 2h |
| F13-T2 | 创建 `useTheme.ts` composable：管理主题状态、localStorage 读写、系统偏好监听（`prefers-color-scheme`） | 前端 | `composables/useTheme.ts` | 2h |
| F13-T3 | 创建 `ThemeToggle.vue` 组件：三态切换按钮（☀️/🌙/💻 系统），下拉菜单或循环切换 | 前端 | `components/ThemeToggle.vue` | 1.5h |
| F13-T4 | 在 `index.html` 或 `main.ts` 中添加主题初始化脚本（防止闪烁：读取 localStorage → 设置 `data-theme`） | 前端 | `main.ts` 或内联 `<script>` | 0.5h |
| F13-T5 | 审查所有组件样式，确保暗色模式下无硬编码颜色值 | 前端 | 全局样式审查 | 2h |
| F13-T6 | 集成 ThemeToggle 到 AppHeader 或侧边栏 | 前端 | `AppHeader.vue` | 0.5h |
| F13-T7 | 测试：useTheme composable 单测 | 测试 | `tests/composables/useTheme.spec.ts` | 1h |

**验收标准 (AC)**：
- **AC-F13-1**：点击主题切换按钮，页面在 Light/Dark 间切换，过渡动画流畅
- **AC-F13-2**：选择"跟随系统"模式后，操作系统切换暗色/亮色时页面自动跟随
- **AC-F13-3**：主题偏好持久化：设置 Dark 模式后刷新页面，仍为 Dark 模式
- **AC-F13-4**：暗色模式下所有文字可读（对比度 ≥ 4.5:1），无白色背景闪现（FOUC）
- **AC-F13-5**：暗色模式下图表（Dashboard）、卡片、Modal、搜索高亮均正确适配

---

### 2.3 F-14 时间线视图

**描述**：按日期分组的记忆时间线视图，直观展示记忆的产生过程和时间分布。

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F14-T1 | 创建 `TimelineView.vue` 页面组件：左侧时间轴线条 + 右侧按日期分组的记忆卡片 | 前端 | `views/TimelineView.vue` | 3h |
| F14-T2 | 实现日期分组逻辑：按 `createdAt` 分组（今天/昨天/本周/本月/更早），支持 Pinia store 计算属性 | 前端 | `stores/agentmemory.ts` 扩展 | 1.5h |
| F14-T3 | 创建 `TimelineGroup.vue` 组件：日期标题 + 记忆卡片列表 | 前端 | `components/TimelineGroup.vue` | 1.5h |
| F14-T4 | Vue Router 新增 `/timeline` 路由 + 导航入口 | 前端 | `router/index.ts` | 0.5h |
| F14-T5 | 时间轴样式：竖线 + 节点圆点 + 日期标签，Apple 风格 | 前端 | `TimelineView.vue` 样式部分 | 1.5h |
| F14-T6 | 与 F-16 虚拟列表集成预留：大数据量下时间线也能虚拟滚动 | 前端 | `TimelineView.vue` | 1h |

**验收标准 (AC)**：
- **AC-F14-1**：访问 `/timeline` 页面，记忆按日期分组显示，每组有日期标题
- **AC-F14-2**：时间轴线条从上到下贯穿，每个日期节点有圆点标记
- **AC-F14-3**：今天和昨天的记忆单独分组，更早的记忆按月分组
- **AC-F14-4**：每个记忆卡片显示 title、type tag、strength、时间，可点击查看详情
- **AC-F14-5**：空数据时显示友好提示"暂无记忆记录"

---

### 2.4 F-15 记忆归档

**描述**：为记忆添加 `archived` 状态字段，支持归档/取消归档操作，默认过滤已归档记忆。

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F15-T1 | 扩展 AgentMemory Pydantic 模型，新增 `archived: bool = False` 字段 | 后端 | `models/agentmemory.py` | 0.5h |
| F15-T2 | 新增 `PATCH /api/agentmemory/{memory_id}/archive` 端点：切换 archived 状态 | 后端 | `routers/agentmemory.py` | 1h |
| F15-T3 | 修改 `GET /api/agentmemory/paginated`：新增 `include_archived` 参数（默认 false，不返回已归档） | 后端 | `routers/agentmemory.py`, `services/agentmemory.py` | 1.5h |
| F15-T4 | MemoryCard 增加"归档"按钮（图标），已归档记忆显示"取消归档"按钮 | 前端 | `components/MemoryCard.vue` | 1h |
| F15-T5 | API client 封装 `archiveMemory(id)` / `unarchiveMemory(id)` | 前端 | `api/agentmemory.ts` | 0.5h |
| F15-T6 | 列表页增加"显示已归档"开关，默认关闭 | 前端 | `views/HomeView.vue` 或 `components/SearchBar.vue` | 1h |
| F15-T7 | 已归档卡片视觉区分：半透明、灰色边框或角标"已归档" | 前端 | `components/MemoryCard.vue` 样式 | 0.5h |
| F15-T8 | 测试：归档/取消归档 API + include_archived 过滤 | 测试 | `tests/test_agentmemory_archive.py` | 1.5h |

**验收标准 (AC)**：
- **AC-F15-1**：点击卡片"归档"按钮，记忆从默认列表消失
- **AC-F15-2**：开启"显示已归档"开关后，已归档记忆以半透明样式显示
- **AC-F15-3**：已归档记忆卡片显示"取消归档"按钮，点击后恢复到默认列表
- **AC-F15-4**：`GET /api/agentmemory/paginated` 默认不返回已归档记忆
- **AC-F15-5**：`?include_archived=true` 参数可返回全部记忆（含已归档）
- **AC-F15-6**：归档操作不影响记忆的其他字段（content、strength 等不变）
- **AC-F15-7**：已归档记忆仍可通过搜索找到（搜索不受归档状态影响）

---

### 2.5 F-16 虚拟列表

**描述**：当记忆条目 >200 条时启用虚拟滚动，保障列表渲染性能。

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F16-T1 | 安装 `vue-virtual-scroller` 依赖 | 前端 | `package.json` | 0.25h |
| F16-T2 | 创建 `VirtualCardGrid.vue` 包装组件：封装 RecycleScroller，接收 items 数组 | 前端 | `components/VirtualCardGrid.vue` | 2h |
| F16-T3 | CardGrid.vue 增加逻辑：items.length > 200 时自动切换到 VirtualCardGrid | 前端 | `components/CardGrid.vue` | 1h |
| F16-T4 | MemoryCard 适配虚拟滚动：固定高度卡片 + 动态内容折叠 | 前端 | `components/MemoryCard.vue` | 1.5h |
| F16-T5 | 虚拟滚动性能测试：模拟 500 条数据，验证滚动流畅度 | 测试 | 手动测试 | 1h |

**验收标准 (AC)**：
- **AC-F16-1**：记忆 ≤200 条时，使用普通滚动（现有行为不变）
- **AC-F16-2**：记忆 >200 条时，自动启用虚拟滚动，仅渲染可视区域卡片
- **AC-F16-3**：虚拟滚动下快速滚动无卡顿（60fps），无白屏闪烁
- **AC-F16-4**：虚拟滚动下卡片点击、展开/折叠功能正常
- **AC-F16-5**：虚拟滚动与排序/过滤联动正常（过滤后条数变化自动切换模式）

---

### 2.6 F-17 记忆变更通知

**描述**：记忆增删改时通过飞书 webhook 发送消息卡片通知。

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F17-T1 | 新增 `webhook_config.json` 配置文件：webhook URL、启用/禁用、通知事件类型 | 后端 | `backend/webhook_config.json` | 0.5h |
| F17-T2 | 创建 `services/notification.py`：封装飞书 webhook 发送逻辑（HTTP POST + 签名验证） | 后端 | `services/notification.py` | 2h |
| F17-T3 | 设计飞书消息卡片模板：包含事件类型、记忆标题、操作时间、操作详情链接 | 后端 | `templates/feishu_card.json` | 1h |
| F17-T4 | 在记忆 CRUD 操作中集成通知发送（POST/PUT/DELETE 后触发） | 后端 | `services/agentmemory.py` | 1.5h |
| F17-T5 | 新增 `GET/PUT /api/webhook/config` 端点：查看和更新 webhook 配置 | 后端 | `routers/webhook.py` (新文件) | 1h |
| F17-T6 | 通知发送异步化：使用 asyncio 避免阻塞主请求 | 后端 | `services/notification.py` | 1h |
| F17-T7 | 测试：webhook 配置 API + 通知发送 mock 测试 | 测试 | `tests/test_webhook.py` | 1.5h |

**验收标准 (AC)**：
- **AC-F17-1**：创建新记忆后，飞书群收到消息卡片，包含"新增记忆"+标题+时间
- **AC-F17-2**：编辑记忆后，飞书群收到"更新记忆"通知
- **AC-F17-3**：删除记忆后，飞书群收到"删除记忆"通知
- **AC-F17-4**：webhook 配置可通过 API 管理（查看/更新 URL、启用/禁用）
- **AC-F17-5**：webhook 禁用时不发送任何通知
- **AC-F17-6**：webhook 发送失败不阻塞主请求，记录错误日志
- **AC-F17-7**：飞书消息卡片格式正确，包含操作类型图标、记忆标题、时间戳

---

## 3. 任务依赖关系

```
F-12 版本更新说明 ──────────┐
F-13 暗色模式 ──────────────┤
F-14 时间线视图 ────────────┼── 可并行开发（互不依赖）
F-15 记忆归档 ──────────────┤
F-16 虚拟列表 ──────────────┤
F-17 记忆变更通知 ──────────┘

内部依赖：
F12-T4 (WhatNewModal) 依赖 F12-T1~T2 (changelog API 先完成)
F13-T3 (ThemeToggle) 依赖 F13-T1~T2 (CSS 变量 + composable 先完成)
F14-T6 (虚拟列表集成) 依赖 F16-T2 (VirtualCardGrid 组件)
F15-T4~T7 (前端归档 UI) 依赖 F15-T1~T3 (后端归档 API 先完成)

跨功能依赖：
F-14 时间线视图最终需集成 F-16 虚拟列表（大数据量场景）
F-13 暗色模式需覆盖 F-12 Modal、F-14 Timeline 的样式
```

**推荐开发顺序**（单人串行，从简到繁）：

```
Phase 1 (Day 1): F-12 版本更新说明
  理由：独立功能，前后端都简单，快速产出可见成果
  产出：CHANGELOG.json + What's New Modal

Phase 2 (Day 2): F-15 记忆归档
  理由：数据模型扩展 + 简单 API + 简单 UI，中等复杂度
  产出：archive API + 归档 UI

Phase 3 (Day 3): F-13 暗色模式
  理由：纯前端工作，需全面审查样式，耗时但无后端依赖
  产出：useTheme composable + ThemeToggle + 全套暗色 CSS 变量

Phase 4 (Day 4): F-16 虚拟列表
  理由：纯前端性能优化，独立且可快速验证
  产出：VirtualCardGrid 组件

Phase 5 (Day 5): F-14 时间线视图
  理由：纯前端新页面，可复用 Phase 4 的虚拟列表组件
  产出：TimelineView + TimelineGroup

Phase 6 (Day 6): F-17 记忆变更通知
  理由：纯后端功能，需 webhook 配置和飞书集成，放最后避免阻塞
  产出：notification service + webhook API
```

---

## 4. 工作量汇总

| 功能 | 后端 | 前端 | 测试 | 合计 | 复杂度 |
|------|------|------|------|------|--------|
| F-12 版本更新说明 | 2.25h | 6h | 1h | **9.25h** | 🟢 低 |
| F-13 暗色模式 | 0 | 7h | 1h | **8h** | 🟡 中 |
| F-14 时间线视图 | 0 | 7.5h | 0 | **7.5h** | 🟡 中 |
| F-15 记忆归档 | 3h | 3h | 1.5h | **7.5h** | 🟡 中 |
| F-16 虚拟列表 | 0 | 4.75h | 1h | **5.75h** | 🟢 低 |
| F-17 记忆变更通知 | 7h | 0 | 1.5h | **8.5h** | 🟡 中 |
| **合计** | **12.25h** | **28.25h** | **6h** | **46.5h** | — |

> 约 **6 个工作日**（按 8h/天计算）

---

## 5. 风险评估

| # | 风险 | 影响 | 概率 | 缓解措施 |
|---|------|------|------|---------|
| R1 | **暗色模式样式遗漏** | 部分组件在暗色模式下文字不可读或背景色异常 | 🟡 中 | Phase 3 预留充足时间（2h）做全量审查；使用 CSS 变量而非硬编码颜色 |
| R2 | **虚拟列表与展开/折叠冲突** | 虚拟滚动要求固定高度，展开/折叠改变卡片高度 | 🟡 中 | 虚拟列表模式下默认折叠，展开时弹出详情 Modal 而非内联展开 |
| R3 | **webhook 飞书签名验证** | 飞书 webhook 有签名验证机制，配置错误导致通知失败 | 🟢 低 | 提供配置文档 + 测试模式（dry-run 不实际发送） |
| R4 | **CHANGELOG.json 维护成本** | 每次发版需手动更新，容易遗忘 | 🟢 低 | 在 CI/CD 流程中加入 changelog 更新检查（P2 不做，P3 考虑） |
| R5 | **归档状态与搜索的交互** | 用户期望搜索能找到归档记忆，但默认列表不显示 | 🟢 低 | 搜索结果默认包含归档记忆，但视觉标记"已归档" |

---

## 6. 技术决策记录

| 决策 | 选项 | 选择 | 理由 |
|------|------|------|------|
| 虚拟滚动库 | vue-virtual-scroller / vue-virtual-list / 自研 | **vue-virtual-scroller** | Vue 3 兼容好；API 简洁；支持动态高度（虽本项目用固定高度） |
| 主题方案 | CSS 变量 / SCSS 变量 / Tailwind dark: | **CSS 变量 + data-theme 属性** | 零构建依赖；运行时切换无需重编译；浏览器原生支持 |
| Changelog 存储 | JSON 文件 / Markdown / 数据库 | **JSON 文件** | 与现有数据存储风格一致；前端直接消费结构化数据；易维护 |
| 归档方式 | 软删除（archived 字段）/ 物理删除+回收站 | **软删除 archived 字段** | 不丢失数据；可恢复；实现简单 |
| 通知方案 | 飞书 webhook / 邮件 / WebSocket | **飞书 webhook** | 用户需求明确；实现简单；团队已在飞书协作 |

---

## 7. 验收检查清单（Sprint Review 用）

- [ ] F-12：首次访问自动弹出 What's New Modal
- [ ] F-12：关闭后刷新不再弹出，版本更新后重新弹出
- [ ] F-12：侧边栏可手动查看更新历史
- [ ] F-13：Light/Dark/系统 三种模式切换正常
- [ ] F-13：暗色模式下所有页面（含 Dashboard、Timeline）视觉正确
- [ ] F-13：主题偏好刷新后保留
- [ ] F-14：时间线按日期分组显示，时间轴线条+节点渲染正确
- [ ] F-14：今天/昨天/本周/本月/更早 分组逻辑正确
- [ ] F-15：归档/取消归档操作正常
- [ ] F-15：默认列表不显示已归档记忆，开关可切换
- [ ] F-16：>200 条数据时自动启用虚拟滚动
- [ ] F-16：虚拟滚动下功能（点击、搜索、过滤）正常
- [ ] F-17：记忆 CRUD 操作触发飞书通知
- [ ] F-17：webhook 配置 API 可用
- [ ] 所有新增 API 端点出现在 `/api/docs` Swagger 文档中
- [ ] 前端构建无 TypeScript 错误（`npm run build` 成功）
- [ ] 后端测试全部通过（`pytest` 成功）
