# Memory Viewer v2 — 功能增强 + 前后端分离重构规格文档

> **版本**: 2.2（用户调整优先级）
> **日期**: 2026-05-28
> **作者**: pm-orchestrator
> **基于**: v1 PM_SPEC.md (2026-05-27) + v2.0 规格

---

## 0. 功能增强方案（v2.1 新增）

### 0.1 设计原则

- **实用优先**：功能服务于"快速理解和管理 Agent 记忆"这一核心目标
- **渐进增强**：P0 保底上线，P1/P2 按用户反馈迭代
- **Apple 风格一致**：每个新功能都必须符合 v1 建立的视觉语言
- **数据量适配**：当前 ~100 条记忆，不需要过度工程化

### 0.2 功能总览（按优先级）

#### P0 — 必须纳入 v2 首版

| # | 功能 | 描述 | 用户价值 | 复杂度 | 涉及层 |
|---|------|------|---------|--------|--------|
| **F-02** | 记忆排序 | 支持按时间（新→旧/旧→新）、强度（高→低）、类型排序 | v1 无排序，数据多了找不到最新/最重要的条目 | 🟢 低（前端 sort + 后端 paginated 端点已支持 sort 参数） | 前端+后端 |
| **F-03** | 记忆详情展开/折叠 | 卡片默认显示摘要（前 2 行），点击展开完整内容 | v1 内容全部展开，页面过长；折叠后信息密度提升 3x | 🟢 低（组件 toggle state + CSS transition） | 前端 |
| **F-04** | Swagger API 文档 | FastAPI 自动生成 OpenAPI 文档，`/api/docs` 可访问 | 开发者零成本查阅 API；方便未来集成调试 | 🟢 极低（FastAPI 内置，只需配置 title/description） | 后端 |
| **F-05** | 搜索高亮渲染 | 搜索结果中关键词高亮显示（`<mark>` 标签） | 用户一眼看到匹配位置，快速判断相关性 | 🟢 低（后端已返回 matchSnippet，前端做 HTML 渲染） | 前端 |
| **F-06** | 键盘快捷键 | `/` 聚焦搜索、`Esc` 清除搜索、`R` 刷新、`1/2/3` 切换 Tab | 效率用户的核心诉求；Apple 风格产品标配 | 🟢 低（全局 keydown 事件监听） | 前端 |
| **F-07** | 记忆创建 | 手动创建新的 agentmemory 条目（title/content/type/concepts） | 无需通过 Agent 对话即可录入知识；主动管理记忆库 | 🟡 中（POST API + 创建表单 + 概念标签输入） | 前端+后端 |
| **F-08** | 记忆导入 | 从 JSON/Markdown 文件批量导入记忆条目 | 批量迁移记忆数据；从备份恢复 | 🟡 中（文件上传 + 解析 + 去重逻辑） | 前端+后端 |
| **F-09** | 记忆导出 | 导出为 JSON/Markdown 格式，支持单条和全量导出 | 备份记忆数据；跨环境迁移 | 🟢 低（后端序列化 + 前端下载触发） | 前端+后端 |

#### P1 — v2.1 迭代（首版上线后 1-2 周）

| # | 功能 | 描述 | 用户价值 | 复杂度 | 涉及层 |
|---|------|------|---------|--------|--------|
| **F-07** | 高级搜索面板 | 可视化过滤器：类型多选、时间范围 picker、strength 滑块、数据源切换 | 比输入关键词更直观的筛选方式；适合"回忆某类记忆"场景 | 🟡 中（新增 FilterPanel 组件 + 搜索 API 参数扩展） | 前端+后端 |
| **F-08** | 记忆编辑 | 支持编辑 agentmemory 条目的 content/concepts/strength | 发现记忆有误时可修正；调整 strength 控制衰减 | 🟡 中（PUT API + 编辑表单 + agentmemory JSON 写回） | 前端+后端 |
| **F-09** | 记忆删除 | 支持删除单条/批量删除 agentmemory 条目 | 清理过期/错误记忆；保持记忆库整洁 | 🟢 低（DELETE API + 确认对话框 + audit trail） | 前端+后端 |
| **F-10** | 统计仪表盘 | 可视化图表：按类型饼图、按时间折线图、按 profile 柱状图、strength 分布 | 一眼掌握记忆全貌；发现记忆系统的问题（如某类型过多/过少） | 🟡 中（新增 /api/stats 端点 + 图表库 echarts/chart.js） | 前端+后端 |
| **F-11** | 缓存自动刷新 | 后端定时任务（每 30 分钟）自动执行 fetch_agentmemory 更新缓存 | 不需要手动刷新；数据始终最新 | 🟢 低（APScheduler 或 asyncio 定时任务） | 后端 |
#### P2 — 未来版本（按需求优先级）

| # | 功能 | 描述 | 用户价值 | 复杂度 | 涉及层 |
|---|------|------|---------|--------|--------|
| **F-12** | 版本更新说明 | 首页弹出 What's New 面板，展示当前版本的更新内容；支持手动查看历史版本日志 | 用户每次部署后能立刻看到新功能；版本迭代有迹可循 | 🟢 低（后端 /api/changelog 端点 + 前端 Modal + localStorage 记录已读版本） | 前端+后端 |
| **F-13** | 暗色模式 | 支持 Light/Dark 主题切换，跟随系统偏好 + 手动覆盖 | 护眼、美观；优先级最低 | 🟡 中（CSS 变量双套 + 切换逻辑 + localStorage 持久化） | 前端 |
| **F-14** | 时间线视图 | 按日期分组的记忆时间线，支持缩放 | 直观看到记忆的产生过程和时间分布 | 🟡 中（新增 TimelineView + 日期分组逻辑） | 前端 |
| **F-15** | 记忆归档 | 标记记忆为"归档"状态，不默认展示但可检索 | 不删除但降低干扰；适合历史记忆管理 | 🟡 中（数据模型扩展 + 过滤逻辑） | 前端+后端 |
| **F-16** | 虚拟列表 | 数据量 >200 条时启用虚拟滚动 | 性能保障；当前数据量不需要 | 🟢 低（vue-virtual-scroller 集成） | 前端 |
| **F-17** | 记忆变更通知 | 记忆增删改时发送飞书 webhook 通知 | 团队协作场景下感知记忆变更 | 🟡 中（webhook 配置 + 飞书消息卡片模板） | 后端 |

#### P3 — 智能化（记忆 >100 条时有价值）

| # | 功能 | 描述 | 用户价值 | 复杂度 | 涉及层 |
|---|------|------|---------|--------|--------|
| **F-18** | 记忆关联图谱 | 基于 concepts 共现关系构建知识图谱，可视化记忆关联 | 发现记忆之间的隐藏联系 | 🟠 高（图数据结构 + D3.js/force-graph） | 前端+后端 |
| **F-19** | 智能推荐 | 根据当前查看的记忆推荐相关条目（基于 concepts 相似度） | 快速找到关联记忆 | 🟠 高（相似度算法 + 推荐引擎） | 后端+前端 |
| **F-20** | 记忆健康度评分 | 综合 strength/age/引用次数计算健康度，低分标记待清理 | 主动发现需要清理的记忆 | 🟡 中（评分算法 + 可视化指标） | 前端+后端 |
| **F-21** | 自动去重 | 检测语义相似的记忆条目，提示合并（需 embedding 或 LLM） | 减少冗余，保持记忆库整洁 | 🟠 高（embedding 计算 + 相似度阈值） | 后端 |
| **F-22** | 记忆衰减曲线 | 可视化 strength 随时间的衰减趋势，预测即将"遗忘"的记忆 | 理解记忆生命周期 | 🟡 中（时间序列图表 + 预测模型） | 前端+后端 |

#### P4 — 协作与集成

| # | 功能 | 描述 | 用户价值 | 复杂度 | 涉及层 |
|---|------|------|---------|--------|--------|
| **F-23** | 多 Agent 记忆对比 | 并排对比不同 profile 的 memory 差异 | 发现不同 Agent 的知识差异 | 🟡 中（diff 算法 + 双栏布局） | 前端+后端 |
| **F-24** | 记忆版本历史 | 追踪每条记忆的修改历史，支持回滚 | 类似 git log，可追溯变更 | 🟠 高（版本存储 + diff 展示） | 前端+后端 |
| **F-25** | 飞书集成 | 在飞书内直接查看/搜索记忆（飞书小程序或消息卡片） | 无需切换工具即可查阅 | 🟠 高（飞书开放平台 API + 小程序） | 后端+前端 |
| **F-26** | API Webhook 订阅 | 外部系统订阅记忆变更事件 | 与外部系统联动 | 🟡 中（webhook 注册 + 事件分发） | 后端 |
| **F-27** | MCP Server 模式 | 将 Memory Viewer 暴露为 MCP Server，其他 Agent 可直接查询 | Agent 生态集成 | 🟠 高（MCP 协议实现） | 后端 |

#### P5 — 运维与可观测性

| # | 功能 | 描述 | 用户价值 | 复杂度 | 涉及层 |
|---|------|------|---------|--------|--------|
| **F-28** | 记忆系统诊断 | 检测重复条目、孤立 concepts、strength 异常分布 | 主动发现记忆系统问题 | 🟢 低（规则引擎 + 诊断报告） | 后端 |
| **F-29** | 操作审计日志 | 记录所有增删改操作，支持按时间/用户/操作类型筛选 | 追溯操作历史，安全合规 | 🟡 中（审计中间件 + 日志存储） | 后端+前端 |
| **F-30** | 备份与恢复 | 定时自动备份 + 一键恢复到任意时间点 | 数据安全保障 | 🟡 中（快照机制 + 恢复流程） | 后端 |
| **F-31** | 多实例管理 | 一个面板管理多个 Hermes 实例的记忆 | 团队多 Agent 场景统一管理 | 🟠 高（多实例路由 + 权限隔离） | 前端+后端 |
| **F-32** | 性能监控 | 记忆读写延迟、缓存命中率、API 响应时间图表 | 运维可观测性 | 🟡 中（指标采集 + 图表展示） | 前端+后端 |

### 0.3 P0 功能详细设计

#### F-07 记忆创建

**实现方案**：
- 新增 `POST /api/agentmemory` 端点，接收 `{title, content, type, concepts}`
- 后端写入 agentmemory JSON 缓存文件（原子写入：tmp + rename）
- 前端新增 CreateMemoryModal 组件：表单含 title(必填)、content(必填)、type(下拉)、concepts(标签输入)
- 创建成功后自动刷新列表

**验收标准**：
- AC-F07-1: 填写必填字段后提交，新记忆出现在列表中
- AC-F07-2: type 有默认值（pattern），concepts 可为空
- AC-F07-3: 创建后页面自动刷新，无需手动刷新
- AC-F07-4: 表单验证：title/content 为空时提示错误

#### F-08 记忆导入

**实现方案**：
- 新增 `POST /api/agentmemory/import` 端点，接收文件上传
- 支持 JSON 格式（agentmemory export 格式）和 Markdown 格式（§分隔）
- 后端解析 + 去重（按 title + content 哈希判断）+ 合并写入缓存
- 前端新增 ImportModal：拖拽上传 + 文件选择 + 导入预览 + 确认

**验收标准**：
- AC-F08-1: 上传 agentmemory JSON 文件，条目成功导入
- AC-F08-2: 重复条目自动跳过，返回导入统计（新增/跳过/失败）
- AC-F08-3: 导入后列表自动刷新
- AC-F08-4: 非法文件格式给出友好错误提示

#### F-09 记忆导出

**实现方案**：
- 新增 `GET /api/agentmemory/export` 端点，支持 `?format=json|markdown`
- JSON 格式：直接返回 agentmemory 缓存
- Markdown 格式：每条记忆格式化为 `## title

content

**type**: pattern | **strength**: 70%

---
`
- 前端在列表页/详情页增加"导出"按钮，触发浏览器下载

**验收标准**：
- AC-F09-1: JSON 导出文件可被导入功能正确读取（闭环）
- AC-F09-2: Markdown 导出文件可读性良好
- AC-F09-3: 支持单条导出（详情页按钮）和全量导出（列表页按钮）

#### F-02 记忆排序

**实现方案**：
- 前端排序控件：下拉菜单（时间↓/↑、强度↓/↑、类型 A-Z）
- 集成到 StatsBar 或 SearchBar 旁
- 后端 `/api/agentmemory/paginated` 已支持 `sort` + `order` 参数

**验收标准**：
- AC-F02-1: 按时间排序：最新条目在前
- AC-F02-2: 按强度排序：strength 高的在前
- AC-F02-3: 按类型排序：相同类型聚合
- AC-F02-4: 排序状态 URL 可分享（query param: `?sort=strength&order=desc`）

#### F-03 记忆详情展开/折叠

**实现方案**：
- MemoryCard 默认显示 title + content 前 100 字符 + type tag
- 点击展开：完整 content + concepts + files + strength + 时间
- CSS transition 动画（Apple 风格 spring 动画）
- 全部展开/折叠按钮

**验收标准**：
- AC-F03-1: 默认折叠态信息密度提升（屏幕可见条目数 ≥ 2x）
- AC-F03-2: 展开动画流畅（60fps）
- AC-F03-3: "全部展开/折叠" 按钮正常工作

#### F-05 搜索高亮渲染

**实现方案**：
- 后端 `matchSnippet` 已包含 `<em>hermes</em>` 标记
- 前端用 `v-html` 渲染（需 XSS 过滤：只允许 `<em>` 标签）
- 高亮样式：`<em>` → `background: #fff3cd; padding: 1px 2px; border-radius: 2px;`

**验收标准**：
- AC-F05-1: 搜索结果中关键词以黄色高亮显示
- AC-F05-2: 仅搜索模式下高亮，正常浏览不显示
- AC-F05-3: XSS 安全（script 标签被过滤）

### 0.4 功能依赖关系

```
P0:
F-02 排序 ─── 依赖 F-03 展开/折叠（排序后需重新渲染）
F-03 展开/折叠 ── 独立
F-04 Swagger ─── 独立（后端零成本）
F-05 搜索高亮 ── 依赖 v2 基础搜索功能
F-06 键盘快捷键 ─ 依赖 F-03（快捷键控制展开/折叠）
F-07 记忆创建 ─── 独立（新增 POST API + 表单）
F-08 记忆导入 ─── 独立（新增上传 API + 解析）
F-09 记忆导出 ─── 独立（新增导出 API + 下载）

P1:
F-10 高级搜索 ─── 依赖 F-05（高亮渲染）
F-11 记忆编辑 ─── 依赖 F-03（编辑态展开）
F-12 记忆删除 ─── 独立
F-13 统计仪表盘 ─ 独立
F-14 自动刷新 ─── 独立

P2:
F-13(原) 暗色模式 ─ 独立
F-14 时间线 ─── 独立
F-15 归档 ─── 独立
F-16 虚拟列表 ── 独立
F-17 飞书通知 ── 独立
```

### 0.5 对现有 v2 架构的影响

| 功能 | 后端变更 | 前端变更 | 部署变更 |
|------|---------|---------|---------|
| F-01 暗色模式 | 无 | +ThemeToggle.vue, variables.css 扩展 | 无 |
| F-02 排序 | 无（已有 sort 参数） | +SortDropdown.vue, store 扩展 | 无 |
| F-03 展开/折叠 | 无 | MemoryCard.vue 重构 | 无 |
| F-04 Swagger | +main.py 配置 | 无 | 无 |
| F-05 搜索高亮 | 无 | +highlight.ts utility, v-html 渲染 | 无 |
| F-06 快捷键 | 无 | +useKeyboard.ts composable | 无 |
| F-07 高级搜索 | +search 参数扩展 | +FilterPanel.vue | 无 |
| F-08 编辑 | +PUT /api/agentmemory/{id} | +EditModal.vue | 无 |
| F-09 删除 | +DELETE /api/agentmemory/{id} | +ConfirmDialog.vue | 无 |
| F-10 统计 | +GET /api/stats | +DashboardView.vue, echarts | 无 |
| F-11 自动刷新 | +APScheduler | 无 | requirements.txt |
| F-12 导出 | +GET /api/agentmemory/export | +ExportButton.vue | 无 |

---

## 1. 重构目标

将 v1 的单体应用（FastAPI serve HTML）拆分为**独立前端 SPA + 独立后端 API**，实现：

- 前后端可**独立开发、独立测试、独立部署**
- 前端可替换为任意静态托管（nginx / CDN / GitHub Pages）
- 后端保持**向后兼容**（v1 API 端点不变）
- 新增搜索、分页等 v1 缺失的功能

---

## 2. 技术选型

### 2.1 前端框架：Vue 3 + Vite + TypeScript

| 候选方案 | 优点 | 缺点 | 评分 |
|---------|------|------|------|
| **Vue 3 + Vite** ✅ | 渐进式，学习成本低；SFC 单文件组件天然分离模板/逻辑/样式；Vite 开发体验极佳（HMR <50ms）；TypeScript 支持完善；社区成熟（Element Plus / Naive UI 可直接复用 Apple 风格组件） | 生态略小于 React | ⭐⭐⭐⭐⭐ |
| React + Vite | 生态最大；Next.js 可选 SSR | 需要 JSX 编译；状态管理选型多（Redux/Zustand/Jotai）增加决策成本；对于此规模项目过度工程化 | ⭐⭐⭐⭐ |
| Svelte | 编译时框架，零运行时开销；语法最简洁 | 生态最小；团队协作/招聘成本高；UI 库选择少 | ⭐⭐⭐ |
| 纯 Vanilla JS | v1 方案，零依赖 | 无组件化、无类型安全、549 行单文件已难维护 | ⭐⭐ |

**选择 Vue 3 的理由**：

1. **数据量适中**：~100 条记忆，不需要 React 级别的虚拟 DOM 优化，Vue 的响应式系统足够
2. **SFC 组件化**：将 v1 的 664 行 `index.html` 拆分为 ~10 个 `.vue` 文件，每个 <100 行
3. **Vite 开发体验**：相比 webpack 配置简单 10 倍，开箱即用的 TypeScript + CSS Modules
4. **Apple 风格适配**：Vue 的 `<style scoped>` 天然隔离样式，配合 CSS 变量可精确复刻 v1 设计系统
5. **渐进式迁移**：可以先用 Vue 3 的 CDN 版本快速原型，再逐步组件化

### 2.2 后端框架：FastAPI（保持不变）

| 维度 | 说明 |
|------|------|
| 框架 | FastAPI ≥0.100，Python 3.11+ |
| 服务器 | uvicorn（开发）/ gunicorn + uvicorn workers（生产） |
| 新增依赖 | `pydantic`（数据模型验证，FastAPI 自带）；`python-multipart`（如需 POST 端点） |
| 不变 | CORS 中间件、环境变量配置方式 |

### 2.3 工具链

| 工具 | 用途 |
|------|------|
| Vite 5 | 前端构建、开发服务器、HMR |
| TypeScript 5 | 前端类型安全 |
| Vue Router 4 | 前端路由（SPA 页面切换） |
| Pinia | Vue 3 官方状态管理（替代 Vuex） |
| Vitest | 前端单元测试 |
| Playwright | E2E 测试（可选） |
| pytest + httpx | 后端 API 测试（替代 TestClient） |
| Docker + docker-compose | 容器化部署 |
| nginx | 反向代理 + 前端静态文件服务 |

---

## 3. 目录结构设计

```
/opt/data/memory-viewer/v2/
├── PM_SPEC.md                  # 本文档
├── docker-compose.yml          # 一键启动：backend + frontend + nginx
├── .env.example                # 环境变量模板
│
├── backend/                    # 后端 API 服务
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── start.sh                # 启动脚本（fetch + uvicorn）
│   ├── fetch_agentmemory.py    # MCP 数据导出脚本（从 v1 复制）
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app 入口
│   │   ├── config.py           # 环境变量配置（pydantic Settings）
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── agentmemory.py  # /api/agentmemory 端点
│   │   │   ├── hermes_memory.py # /api/hermes-memory 端点
│   │   │   ├── profiles.py     # /api/profiles 端点
│   │   │   ├── search.py       # /api/search 端点（新增）
│   │   │   └── health.py       # /api/health 端点（新增）
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── agentmemory.py  # Pydantic 数据模型
│   │   │   └── hermes_memory.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── agentmemory.py  # agentmemory 数据读取服务
│   │   │   ├── hermes_memory.py # hermes memory 文件解析服务
│   │   │   └── search.py       # 搜索服务（内存过滤 + 关键词匹配）
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── markdown.py     # § 分隔符解析器
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py         # pytest fixtures（临时数据目录）
│       ├── test_agentmemory.py
│       ├── test_hermes_memory.py
│       ├── test_profiles.py
│       ├── test_search.py
│       └── test_health.py
│
├── frontend/                   # 前端 SPA
│   ├── Dockerfile              # 多阶段构建：node build → nginx serve
│   ├── nginx.conf              # nginx 配置（SPA fallback + API proxy）
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html              # Vite 入口 HTML
│   │
│   ├── public/
│   │   └── favicon.svg
│   │
│   ├── src/
│   │   ├── main.ts             # Vue app 初始化
│   │   ├── App.vue             # 根组件
│   │   │
│   │   ├── router/
│   │   │   └── index.ts        # Vue Router 配置
│   │   │
│   │   ├── stores/
│   │   │   ├── agentmemory.ts  # Pinia store: agentmemory 数据
│   │   │   ├── hermesMemory.ts # Pinia store: hermes memory 数据
│   │   │   └── ui.ts           # Pinia store: UI 状态（tab、搜索、loading）
│   │   │
│   │   ├── api/
│   │   │   ├── client.ts       # axios/fetch 封装（baseURL、错误处理）
│   │   │   ├── agentmemory.ts  # agentmemory API 调用
│   │   │   ├── hermesMemory.ts # hermes memory API 调用
│   │   │   ├── profiles.ts     # profiles API 调用
│   │   │   └── search.ts       # search API 调用
│   │   │
│   │   ├── components/
│   │   │   ├── AppHeader.vue       # 页面标题 + 描述
│   │   │   ├── SearchBar.vue       # 搜索输入框（debounce）
│   │   │   ├── StatsBar.vue        # 统计数字
│   │   │   ├── TabBar.vue          # 数据源切换 Tab
│   │   │   ├── RefreshButton.vue   # 刷新按钮
│   │   │   ├── MemoryCard.vue      # agentmemory 条目卡片
│   │   │   ├── HermesCard.vue      # hermes memory 条目卡片
│   │   │   ├── ProfileSection.vue  # Profile 分组展示
│   │   │   ├── CardGrid.vue        # 卡片网格容器
│   │   │   ├── SkeletonLoader.vue  # 骨架屏
│   │   │   ├── EmptyState.vue      # 空状态
│   │   │   ├── ErrorBanner.vue     # 错误提示
│   │   │   ├── ThemeToggle.vue     # 🆕 暗色模式切换按钮
│   │   │   ├── SortDropdown.vue    # 🆕 排序下拉菜单
│   │   │   └── KeyboardHelp.vue    # 🆕 快捷键帮助 overlay
│   │   │
│   │   ├── views/
│   │   │   ├── HomeView.vue        # 首页：全部记忆
│   │   │   ├── AgentMemoryView.vue # AgentMemory 详情页
│   │   │   ├── HermesMemoryView.vue # Hermes Memory 详情页
│   │   │   └── SearchResultsView.vue # 搜索结果页
│   │   │
│   │   ├── types/
│   │   │   ├── agentmemory.ts  # TypeScript 接口定义
│   │   │   └── hermesMemory.ts
│   │   │
│   │   ├── styles/
│   │   │   ├── variables.css   # CSS 变量（从 v1 迁移设计系统，含暗色模式）
│   │   │   ├── reset.css       # CSS reset
│   │   │   └── animations.css  # 动画（skeleton、spin、spring 展开）
│   │   │
│   │   ├── composables/        # 🆕 Vue 3 组合式函数
│   │   │   ├── useKeyboard.ts  # 🆕 全局键盘快捷键
│   │   │   └── useTheme.ts     # 🆕 暗色模式主题管理
│   │   │
│   │   └── utils/
│   │       ├── format.ts       # 日期格式化、文本截断
│   │       └── highlight.ts    # 搜索高亮
│   │
│   └── tests/
│       ├── components/         # 组件单元测试（Vitest）
│       └── stores/             # Store 单元测试
│
└── nginx/                      # 生产环境 nginx 配置（docker-compose 用）
    └── nginx.conf              # 反向代理：/ → frontend, /api → backend
```

---

## 4. API 规格

### 4.1 向后兼容端点（v1 → v2 完全不变）

#### `GET /api/agentmemory`
```json
// Request: 无参数
// Response 200:
{
  "memories": [
    {
      "id": "mem_mpll8an1_4976b2ceceae",
      "type": "pattern",
      "title": "Kanban multi-agent workflow...",
      "content": "Hermes built-in Kanban board...",
      "concepts": ["hermes", "使用技巧", "kanban", "multi-agent"],
      "files": [],
      "createdAt": "2026-05-25T19:16:57.181Z",
      "updatedAt": "2026-05-25T19:16:57.181Z",
      "strength": 7,
      "version": 1,
      "isLatest": true,
      "sessionIds": []
    }
  ]
}
```

#### `GET /api/hermes-memory`
```json
// Response 200:
{
  "global": {
    "memory": ["entry 1", "entry 2", ...],
    "user": ["user entry 1", ...]
  },
  "profiles": {
    "chief-agent": { "memory": [...], "user": [...] },
    "daily": { "memory": [...], "user": [...] }
  }
}
```

#### `GET /api/profiles`
```json
// Response 200:
["chief-agent", "daily", "dev-worker", "pm-orchestrator", "qa-worker"]
```

### 4.2 新增端点

#### `GET /api/health`
```json
// Response 200:
{
  "status": "ok",
  "version": "2.0.0",
  "uptime_seconds": 12345,
  "cache_age_seconds": 300,
  "agentmemory_count": 11,
  "hermes_memory_count": 16
}
```

#### `GET /api/search`
对所有记忆数据进行服务端搜索（支持跨数据源）。
```
Query Parameters:
  q           string  required  搜索关键词
  source      string  optional  数据源过滤: "agentmemory" | "hermes" | 默认 "all"
  type        string  optional  agentmemory 类型过滤: "pattern" | "fact" | "preference" | "bug" | "workflow" | "architecture"
  profile     string  optional  hermes profile 过滤: "global" | profile name
  limit       int     optional  每页条数，默认 50，最大 200
  offset      int     optional  偏移量，默认 0
```

```json
// Response 200:
{
  "query": "hermes",
  "total": 8,
  "limit": 50,
  "offset": 0,
  "results": [
    {
      "source": "agentmemory",
      "id": "mem_xxx",
      "type": "pattern",
      "title": "...",
      "content": "...",
      "concepts": [...],
      "strength": 7,
      "updatedAt": "2026-05-25T19:16:57.181Z",
      "matchField": "content",
      "matchSnippet": "...matching text with <em>hermes</em>..."
    },
    {
      "source": "hermes",
      "profile": "daily",
      "file": "MEMORY.md",
      "index": 1,
      "content": "...",
      "matchField": "content",
      "matchSnippet": "..."
    }
  ]
}
```

#### `GET /api/agentmemory/paginated`
分页版本的 agentmemory 端点（可选，仅在数据量增长到 >200 条时启用）。
```
Query Parameters:
  limit       int     optional  每页条数，默认 50
  offset      int     optional  偏移量，默认 0
  sort        string  optional  排序字段: "updatedAt" | "createdAt" | "strength" | "type"
  order       string  optional  排序方向: "asc" | "desc"，默认 "desc"
  type        string  optional  类型过滤
```

```json
// Response 200:
{
  "total": 11,
  "limit": 50,
  "offset": 0,
  "memories": [...]
}
```

### 4.3 P1 预留端点（v2.1 迭代）

#### `PUT /api/agentmemory/{memory_id}`
编辑记忆条目（F-08）。
```
Request Body:
  content     string  optional  新内容
  concepts    string  optional  新概念（逗号分隔）
  strength    int     optional  新强度 (1-10)
```
```json
// Response 200: { "success": true, "memory": {...} }
// Response 404: { "detail": "Memory not found" }
```

#### `DELETE /api/agentmemory/{memory_id}`
删除记忆条目（F-09）。
```
Query Parameters:
  reason      string  optional  删除原因（记录 audit trail）
```
```json
// Response 200: { "success": true, "deleted_id": "mem_xxx" }
```

#### `GET /api/stats`
记忆统计数据（F-10）。
```json
// Response 200:
{
  "agentmemory": {
    "total": 11,
    "by_type": { "pattern": 3, "fact": 2, "preference": 2, ... },
    "by_strength": { "1-3": 2, "4-6": 4, "7-10": 5 },
    "timeline": { "2026-05": 11 }
  },
  "hermes": {
    "total": 16,
    "by_profile": { "global": 4, "chief-agent": 3, ... },
    "by_file": { "MEMORY.md": 10, "USER.md": 6 }
  }
}
```

#### `GET /api/agentmemory/export`
导出记忆数据（F-12）。
```
Query Parameters:
  format      string  optional  "json" | "markdown"，默认 "json"
  ids         string  optional  逗号分隔的 ID 列表，为空则导出全部
```

### 4.4 API 版本策略

- v1 端点（`/api/agentmemory`、`/api/hermes-memory`、`/api/profiles`）保持**完全不变**
- 新增端点以**查询参数扩展**或**新路径**方式添加
- 未来如需 breaking change，使用 `/api/v2/` 前缀

---

## 5. 前端架构

### 5.1 路由设计（Vue Router）

| 路径 | 视图组件 | 说明 |
|------|---------|------|
| `/` | `HomeView.vue` | 首页：全部记忆（AgentMemory + Hermes） |
| `/agentmemory` | `AgentMemoryView.vue` | AgentMemory 详情页 |
| `/hermes` | `HermesMemoryView.vue` | Hermes Memory 详情页 |
| `/search` | `SearchResultsView.vue` | 搜索结果页（query param: `?q=xxx`） |

### 5.2 状态管理（Pinia）

#### `useAgentMemoryStore`
```typescript
interface AgentMemoryState {
  memories: AgentMemory[]    // 全部条目
  loading: boolean
  error: string | null
  lastFetch: Date | null
}
// Actions: fetchMemories(), refresh()
// Getters: filteredMemories(query), memoriesByType(type)
```

#### `useHermesMemoryStore`
```typescript
interface HermesMemoryState {
  global: { memory: string[], user: string[] }
  profiles: Record<string, { memory: string[], user: string[] }>
  loading: boolean
  error: string | null
  lastFetch: Date | null
}
// Actions: fetchMemory(), refresh()
// Getters: profileNames, totalEntries, filteredEntries(query, profile)
```

#### `useUIStore`
```typescript
interface UIState {
  currentTab: 'all' | 'agentmemory' | 'hermes'
  searchQuery: string
  selectedProfile: string | null  // null = show all
  sidebarCollapsed: boolean
  // 🆕 P0 增强
  theme: 'light' | 'dark' | 'system'        // 主题模式
  sortBy: 'updatedAt' | 'createdAt' | 'strength' | 'type'  // 排序字段
  sortOrder: 'asc' | 'desc'                  // 排序方向
  allExpanded: boolean | null                 // null=个别, true=全展开, false=全折叠
  showKeyboardHelp: boolean                   // 快捷键帮助 overlay
}
// Actions: setTab(), setSearch(), setProfile(), toggleSidebar()
// 🆕 Actions: setTheme(), setSort(), toggleAllExpanded(), toggleKeyboardHelp()
```

### 5.3 组件树

```
App.vue
├── AppHeader.vue
│   ├── 标题 "Memory Viewer"
│   ├── 副标题 "Hermes Agent 记忆系统全景视图"
│   └── ThemeToggle.vue 🆕（暗色模式切换）
├── SearchBar.vue
│   └── input + debounce → uiStore.setSearch()
├── StatsBar.vue
│   ├── 读取 agentMemoryStore + hermesMemoryStore 统计
│   └── SortDropdown.vue 🆕（排序选择）
├── TabBar.vue
│   └── 全部 / AgentMemory / Hermes Memory
├── RefreshButton.vue
│   └── 触发两个 store 的 refresh()
├── ErrorBanner.vue
│   └── 显示 store.error
├── KeyboardHelp.vue 🆕（`?` 触发，显示快捷键列表）
└── <router-view>
    ├── HomeView.vue
    │   ├── section "AgentMemory"
    │   │   ├── CardGrid.vue
    │   │   │   └── MemoryCard.vue × N
    │   │   └── EmptyState.vue (if empty)
    │   └── section "Hermes Memory"
    │       ├── ProfileSection.vue × N
    │       │   ├── profile heading
    │       │   └── CardGrid.vue
    │       │       └── HermesCard.vue × M
    │       └── EmptyState.vue (if empty)
    ├── AgentMemoryView.vue
    │   ├── 分页控制（如启用）
    │   └── CardGrid → MemoryCard
    ├── HermesMemoryView.vue
    │   └── ProfileSection (按 profile 分组)
    └── SearchResultsView.vue
        ├── 搜索统计 "找到 N 条结果"
        └── CardGrid → MemoryCard / HermesCard (统一渲染)
```

### 5.4 API 客户端封装

```typescript
// src/api/client.ts
const API_BASE = import.meta.env.VITE_API_BASE || '/api'

// 统一错误处理、loading 状态、重试逻辑
// 开发环境: VITE_API_BASE=http://localhost:8501/api (proxy to backend)
// 生产环境: VITE_API_BASE=/api (nginx reverse proxy)
```

### 5.5 设计系统迁移

从 v1 的 CSS 变量完整迁移到 `variables.css`：

```css
:root {
  --primary: #1d1d1f;
  --bg: #f5f5f7;
  --card: #ffffff;
  --border: #e5e5e7;
  --text-secondary: #6e6e73;
  --accent: #0071e3;
  --accent-hover: #0077ed;
  --tag-bg: #e8e8ed;
  --radius: 12px;
  --shadow: 0 2px 12px rgba(0,0,0,0.08);
  --font: 'SF Pro Display', -apple-system, BlinkMacSystemFont,
          'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}
```

所有组件使用 `<style scoped>` + CSS 变量，确保样式隔离。

---

## 6. Docker 部署方案

### 6.1 架构图

```
                    ┌─────────────────────────────┐
                    │       Host :8501             │
                    └──────────┬──────────────────┘
                               │
                    ┌──────────▼──────────────────┐
                    │    nginx container           │
                    │    (反向代理 + 静态文件)      │
                    │                              │
                    │  /           → frontend SPA  │
                    │  /api/*      → backend:8000  │
                    └──────┬───────────┬───────────┘
                           │           │
              ┌────────────▼──┐   ┌────▼──────────────┐
              │  frontend     │   │  backend           │
              │  (nginx)      │   │  (uvicorn)         │
              │  :80 内部     │   │  :8000 内部        │
              │               │   │                    │
              │  静态 HTML/   │   │  FastAPI +          │
              │  JS/CSS       │   │  fetch_agentmemory  │
              └───────────────┘   └────────────────────┘
                                      │
                                      │ 读取
                                      ▼
                              ┌───────────────┐
                              │ /opt/data/     │
                              │ (volume mount) │
                              │ - memories/    │
                              │ - profiles/    │
                              │ - cache/       │
                              └───────────────┘
```

### 6.2 docker-compose.yml

```yaml
version: "3.8"

services:
  # ── 后端 API ──
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: memory-viewer-backend
    volumes:
      - /opt/data:/opt/data:ro
    environment:
      - MEMORY_VIEWER_PORT=8000
      - MEMORY_VIEWER_HOST=0.0.0.0
      - AGENTMEMORY_CACHE=/opt/data/memory-viewer/cache/agentmemory.json
      - HERMES_MEMORIES_DIR=/opt/data/memories
      - HERMES_PROFILES_DIR=/opt/data/profiles
      - CORS_ORIGINS=http://localhost:8501
    expose:
      - "8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  # ── 前端 SPA ──
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: memory-viewer-frontend
    expose:
      - "80"
    restart: unless-stopped

  # ── nginx 反向代理（统一入口） ──
  nginx:
    image: nginx:alpine
    container_name: memory-viewer-nginx
    ports:
      - "${MEMORY_VIEWER_PORT:-8501}:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      backend:
        condition: service_healthy
      frontend:
        condition: service_started
    restart: unless-stopped
```

### 6.3 nginx 配置

```nginx
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # ── 前端静态文件 ──
    server {
        listen 80;
        server_name _;

        # API 请求代理到后端
        location /api/ {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_read_timeout 30s;
        }

        # 前端静态文件
        location / {
            root /usr/share/nginx/html;
            index index.html;

            # SPA fallback：所有非文件请求回退到 index.html
            try_files $uri $uri/ /index.html;
        }

        # 健康检查（nginx 自身）
        location /nginx-health {
            return 200 '{"status":"ok"}';
            add_header Content-Type application/json;
        }
    }
}
```

### 6.4 Backend Dockerfile

```dockerfile
FROM python:3.11-slim

# Node.js（fetch_agentmemory.py 需要）
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MEMORY_VIEWER_PORT=8000
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["bash", "start.sh"]
```

### 6.5 Frontend Dockerfile（多阶段构建）

```dockerfile
# ── 构建阶段 ──
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_API_BASE=/api
ENV VITE_API_BASE=${VITE_API_BASE}
RUN npm run build

# ── 生产阶段 ──
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# nginx.conf 由 docker-compose volume mount
```

### 6.6 开发环境（无需 Docker）

```bash
# 终端 1: 启动后端
cd /opt/data/memory-viewer/v2/backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# 终端 2: 启动前端
cd /opt/data/memory-viewer/v2/frontend
npm install
npm run dev  # Vite dev server on :5173, proxy /api → :8000
```

Vite 开发代理配置：
```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

---

## 7. 开发任务拆分

### Phase 1: 后端重构（~2 天）

| # | 任务 | 描述 | 依赖 | 预估 |
|---|------|------|------|------|
| **BE-01** | 项目初始化 | 创建 backend/ 目录结构，迁移 requirements.txt，添加 pydantic models | — | 0.5h |
| **BE-02** | 配置模块 | 编写 `app/config.py`：pydantic Settings 集中管理环境变量 | BE-01 | 0.5h |
| **BE-03** | 数据服务层 | 从 v1 app.py 提取 `app/services/`：agentmemory 读取、hermes memory 解析、§ 分割器 | BE-01 | 1h |
| **BE-04** | 路由模块化 | 将 v1 的 3 个端点拆分到 `app/routers/`，保持响应格式完全一致 | BE-03 | 1h |
| **BE-05** | 新增 /api/health | 实现健康检查端点：版本、运行时间、缓存状态 | BE-04 | 0.5h |
| **BE-06** | 新增 /api/search | 实现跨数据源搜索：关键词匹配 + 高亮片段 + 分页 | BE-04 | 2h |
| **BE-07** | 分页支持 | `/api/agentmemory/paginated` 端点（可选，标记为低优先级） | BE-04 | 1h |
| **BE-08** | 后端测试 | 迁移 v1 测试 + 新端点测试（pytest + httpx） | BE-04~07 | 2h |
| **BE-09** | 后端 Dockerfile | 编写 backend/Dockerfile + start.sh | BE-04 | 0.5h |
| **BE-10** | Swagger 配置 🆕 | FastAPI app 配置 OpenAPI 元数据（title/description/version），启用 /api/docs + /api/redoc | BE-04 | 0.25h |

### Phase 2: 前端搭建（~3 天）

| # | 任务 | 描述 | 依赖 | 预估 |
|---|------|------|------|------|
| **FE-01** | 项目初始化 | `npm create vue@latest`，配置 Vite + TypeScript + Vue Router + Pinia | — | 0.5h |
| **FE-02** | 设计系统迁移 | 创建 `variables.css` + `reset.css` + `animations.css`，从 v1 迁移全部 CSS 变量和样式 | FE-01 | 1h |
| **FE-03** | API 客户端 | 编写 `api/` 模块：fetch 封装、类型定义、错误处理 | FE-01 | 1h |
| **FE-04** | Pinia Stores | 实现 3 个 store：agentMemory、hermesMemory、ui | FE-03 | 1.5h |
| **FE-05** | 基础组件 | 实现 AppHeader、SearchBar、StatsBar、TabBar、RefreshButton、ErrorBanner | FE-02 | 2h |
| **FE-06** | 数据卡片组件 | 实现 MemoryCard、HermesCard、CardGrid、ProfileSection | FE-02 | 2h |
| **FE-07** | 首页视图 | 实现 HomeView：组合全部组件，实现 v1 完整功能 | FE-04,05,06 | 1.5h |
| **FE-08** | 详情页视图 | 实现 AgentMemoryView + HermesMemoryView | FE-04,06 | 1h |
| **FE-09** | 搜索结果页 | 实现 SearchResultsView：调用 /api/search，统一渲染 | FE-03,06 | 1.5h |
| **FE-10** | 骨架屏 + 空状态 | 实现 SkeletonLoader + EmptyState 组件 | FE-02 | 1h |
| **FE-11** | 前端测试 | 组件单测（Vitest）+ Store 单测 | FE-04~09 | 2h |
| **FE-12** | 前端 Dockerfile | 多阶段构建：node build → nginx serve | FE-01 | 0.5h |

### Phase 2.5: P0 功能增强（~1.5 天）🆕

| # | 任务 | 描述 | 依赖 | 预估 | 对应功能 |
|---|------|------|------|------|---------|
| **FE-13** | 暗色模式 | ThemeToggle.vue + variables.css dark 变量 + localStorage 持久化 + 系统偏好检测 | FE-02 | 2h | F-01 |
| **FE-14** | 记忆排序 | SortDropdown.vue + store 扩展 + URL 参数同步 | FE-04,07 | 1h | F-02 |
| **FE-15** | 展开/折叠 | MemoryCard.vue 重构：摘要态/详情态 + CSS transition + 全部展开按钮 | FE-06 | 1.5h | F-03 |
| **FE-16** | 搜索高亮 | highlight.ts utility（XSS 安全 HTML 渲染）+ 搜索结果样式 | FE-09 | 1h | F-05 |
| **FE-17** | 键盘快捷键 | useKeyboard.ts composable + 快捷键提示 overlay（`?` 显示帮助） | FE-07 | 1h | F-06 |
| **FE-18** | P0 功能测试 | 暗色模式、排序、展开、高亮、快捷键的组件单测 | FE-13~17 | 1.5h | — |

### Phase 3: 集成部署（~1 天）

| # | 任务 | 描述 | 依赖 | 预估 |
|---|------|------|------|------|
| **INT-01** | nginx 配置 | 编写统一入口 nginx.conf：/ → frontend, /api → backend | BE-09, FE-12 | 0.5h |
| **INT-02** | docker-compose | 编写完整 docker-compose.yml（3 个 service） | INT-01 | 0.5h |
| **INT-03** | E2E 验证 | docker compose up 后端到端验证所有功能 | INT-02 | 2h |
| **INT-04** | 文档 | README.md：启动方式、开发指南、API 文档链接 | INT-03 | 1h |

**总预估**：~7.5 天（单人），~4 天（前后端并行）

---

## 8. 验收标准

### 8.1 功能验收（基础）

| # | 测试项 | 验收方式 | 对应 API |
|---|--------|---------|---------|
| AC-01 | 向后兼容：`/api/agentmemory` 返回格式与 v1 完全一致 | 对比 v1/v2 响应 JSON diff 为空 | ✅ v1 |
| AC-02 | 向后兼容：`/api/hermes-memory` 返回格式与 v1 完全一致 | 同上 | ✅ v1 |
| AC-03 | 向后兼容：`/api/profiles` 返回格式与 v1 完全一致 | 同上 | ✅ v1 |
| AC-04 | `/api/health` 返回服务状态 | curl 验证 200 + JSON 字段完整 | 新增 |
| AC-05 | `/api/search?q=hermes` 返回跨数据源搜索结果 | 验证返回 agentmemory + hermes 两类结果 | 新增 |
| AC-06 | `/api/search` 支持 source/type/profile 过滤 | 各参数组合验证 | 新增 |
| AC-07 | `/api/search` 支持分页（limit/offset） | 验证 total/offset/limit 正确 | 新增 |
| AC-08 | 前端首页展示全部记忆（AgentMemory + Hermes） | 浏览器验证，内容与 v1 一致 | — |
| AC-09 | 前端搜索功能正常 | 输入关键词实时过滤 + 搜索结果页 | — |
| AC-10 | 前端 Tab 切换正常 | 全部 / AgentMemory / Hermes Memory | — |
| AC-11 | 前端 Profile 切换正常 | 选择不同 profile 显示对应数据 | — |
| AC-12 | 前端刷新按钮正常 | 点击后重新加载数据 | — |
| AC-13 | 前端骨架屏加载态 | 数据加载时显示 skeleton | — |
| AC-14 | 前端错误态展示 | 后端不可用时显示错误提示 | — |
| AC-15 | Apple 风格视觉一致性 | 与 v1 截图对比，视觉差异 <5% | — |
| AC-16 | `/api/docs` Swagger UI 可访问 | 浏览器打开显示 API 文档 | F-04 |

### 8.2 功能验收（P0 增强）🆕

| # | 测试项 | 验收方式 | 对应功能 |
|---|--------|---------|---------|
| AC-P01 | 暗色模式：系统偏好自动切换 | 系统设置暗色 → 页面自动切换 | F-01 |
| AC-P02 | 暗色模式：手动切换 + 持久化 | 点击切换按钮 → 刷新保持 | F-01 |
| AC-P03 | 暗色模式：对比度合规 | 所有文本对比度 ≥ 4.5:1（可用 axe DevTools 检测） | F-01 |
| AC-P04 | 排序：按时间排序 | 切换排序后条目顺序正确 | F-02 |
| AC-P05 | 排序：按强度排序 | strength 高的在前 | F-02 |
| AC-P06 | 排序：按类型排序 | 同类型聚合 | F-02 |
| AC-P07 | 展开/折叠：默认折叠态 | 首页卡片默认显示摘要 | F-03 |
| AC-P08 | 展开/折叠：点击展开 | 点击卡片展开完整内容，动画流畅 | F-03 |
| AC-P09 | 展开/折叠：全部展开/折叠 | 按钮控制所有卡片状态 | F-03 |
| AC-P10 | 搜索高亮：关键词高亮 | 搜索结果中匹配文字黄色标记 | F-05 |
| AC-P11 | 搜索高亮：XSS 安全 | 注入 `<script>` 标签被过滤 | F-05 |
| AC-P12 | 键盘快捷键：`/` 聚焦搜索 | 按 `/` 光标定位到搜索框 | F-06 |
| AC-P13 | 键盘快捷键：`Esc` 清除 | 按 `Esc` 清空搜索并关闭 | F-06 |
| AC-P14 | 键盘快捷键：`R` 刷新 | 按 `R` 重新加载数据 | F-06 |
| AC-P15 | 键盘快捷键：`?` 帮助 | 按 `?` 显示快捷键列表 overlay | F-06 |

### 8.3 非功能验收

| # | 测试项 | 验收标准 |
|---|--------|---------|
| NF-01 | 后端启动时间 | < 5 秒（不含 fetch_agentmemory） |
| NF-02 | API 响应时间 | 所有端点 < 200ms |
| NF-03 | 前端首屏加载 | < 2 秒（gzip 后 < 100KB） |
| NF-04 | Docker 镜像大小 | backend < 300MB, frontend < 50MB |
| NF-05 | 后端测试覆盖率 | > 80%（核心路由 100%） |
| NF-06 | 前端测试覆盖率 | > 70%（stores + 关键组件） |
| NF-07 | CORS 正确配置 | 前端 dev server (5173) 能跨域访问 backend (8000) |
| NF-08 | 无 npm audit high/critical | `npm audit` 无高危漏洞 |

### 8.4 部署验收

| # | 测试项 | 验收方式 |
|---|--------|---------|
| DP-01 | `docker compose up` 一键启动 | 3 个容器均 healthy |
| DP-02 | `http://localhost:8501` 可访问 | 浏览器打开正常 |
| DP-03 | 开发模式可独立启动后端 | `uvicorn app.main:app --reload` 正常 |
| DP-04 | 开发模式可独立启动前端 | `npm run dev` 正常，API 代理生效 |
| DP-05 | 前端构建产物可独立部署 | `npm run build` → dist/ 可被任意静态服务器 serve |

---

## 9. 风险与缓解

| # | 风险 | 影响 | 缓解措施 |
|---|------|------|---------|
| R-01 | 前后端分离后 CORS 配置遗漏 | 开发环境跨域请求失败 | Vite dev proxy + 后端 CORS allow_origins 配置化 |
| R-02 | v1 数据格式变更导致前端不兼容 | 前端渲染异常 | Pydantic 模型强制校验 + 前端 TypeScript 接口约束 |
| R-03 | nginx SPA fallback 配置错误 | 直接访问 /agentmemory 返回 404 | try_files $uri $uri/ /index.html |
| R-04 | Docker 多容器网络通信问题 | frontend 无法代理到 backend | docker-compose depends_on + healthcheck |
| R-05 | fetch_agentmemory.py Node.js 依赖 | 后端容器构建变大 | 多阶段构建 or 独立 sidecar 容器 |
| R-06 | 前端构建工具链版本漂移 | 构建失败 | lock package-lock.json + .nvmrc 锁定 Node 版本 |

---

## 10. 迁移策略

### 10.1 并行运行

v1 和 v2 可以**同时运行**，互不影响：
- v1: `http://localhost:8501`（现有）
- v2: `http://localhost:8502`（新端口，开发阶段）

### 10.2 切换步骤

1. v2 所有验收标准通过
2. 更新 docker-compose 端口映射：8501 → v2
3. 保留 v1 代码 7 天作为回退
4. 确认无问题后移除 v1 代码

### 10.3 数据层不变

v2 后端读取的数据文件与 v1 **完全相同**：
- `/opt/data/memory-viewer/cache/agentmemory.json`
- `/opt/data/memories/MEMORY.md` / `USER.md`
- `/opt/data/profiles/<name>/memories/MEMORY.md` / `USER.md`

无需数据迁移。

---

## 附录 A: v1 → v2 文件映射

| v1 文件 | v2 目标位置 | 变更说明 |
|---------|------------|---------|
| `app.py` (155行) | `backend/app/main.py` + `routers/` + `services/` | 拆分为模块化架构 |
| `index.html` (664行) | `frontend/src/` (~10 个 .vue 文件) | 组件化重构 |
| `fetch_agentmemory.py` (203行) | `backend/fetch_agentmemory.py` | 原样复制 |
| `requirements.txt` | `backend/requirements.txt` | 可能新增 httpx（测试用） |
| `Dockerfile` | `backend/Dockerfile` + `frontend/Dockerfile` | 拆分为两个 |
| `docker-compose.yml` | `v2/docker-compose.yml` | 3 个 service |
| `start.sh` | `backend/start.sh` | 微调端口默认值 |
| `tests/test_api.py` | `backend/tests/` | 拆分 + 扩展 |

## 附录 B: TypeScript 类型定义

```typescript
// src/types/agentmemory.ts
export interface AgentMemory {
  id: string
  type: 'pattern' | 'fact' | 'preference' | 'bug' | 'workflow' | 'architecture'
  title: string
  content: string
  concepts: string[]
  files: string[]
  createdAt: string
  updatedAt: string
  strength: number
  version: number
  isLatest: boolean
  sessionIds: string[]
}

export interface AgentMemoryResponse {
  memories: AgentMemory[]
}

// src/types/hermesMemory.ts
export interface HermesProfileData {
  memory: string[]
  user: string[]
}

export interface HermesMemoryResponse {
  global: HermesProfileData
  profiles: Record<string, HermesProfileData>
}

// src/types/search.ts
export interface SearchResult {
  source: 'agentmemory' | 'hermes'
  // agentmemory fields
  id?: string
  type?: string
  concepts?: string[]
  strength?: number
  // hermes fields
  profile?: string
  file?: string
  index?: number
  // common
  title?: string
  content: string
  updatedAt?: string
  matchField: string
  matchSnippet: string
}

export interface SearchResponse {
  query: string
  total: number
  limit: number
  offset: number
  results: SearchResult[]
}
```

---

## P8 — Next Generation

> **Phase**: P8
> **Theme**: AI-Powered Intelligence + Developer Experience
> **Features**: 6 (F-33 through F-38)
> **Estimated Effort**: 3-4 weeks

### P8 Feature Table

| # | Feature | Description | User Value | Complexity | Layer |
|---|---------|-------------|------------|------------|-------|
| **F-33** | Semantic Search | Vector-embedding-based search beyond keyword matching | Find related memories even when keywords differ; "security" finds "vulnerability" | 🟠 High | Backend + Frontend |
| **F-34** | AI Auto-Tagging & Summarization | LLM-powered automatic tag generation and memory summarization | Eliminate manual tagging; consistent, high-quality metadata | 🟠 High | Backend + Frontend |
| **F-35** | Command Palette (⌘K) | Global command palette for instant navigation and actions | Power users navigate anywhere in <1 second; Spotlight-style UX | 🟡 Medium | Frontend |
| **F-36** | Bulk Operations Toolbar | Multi-select memories with batch edit, tag, export, delete | Manage 50+ memories efficiently; batch operations save hours | 🟡 Medium | Frontend + Backend |
| **F-37** | Memory Activity Heatmap | GitHub-style calendar heatmap of memory creation/activity | Visualize temporal patterns; discover when you're most productive | 🟡 Medium | Frontend + Backend |
| **F-38** | Plugin System | Extensible plugin architecture for custom processors | Custom logic without modifying core; community ecosystem | 🟠 High | Backend + Frontend |

### P8 Detailed Designs

#### F-33 Semantic Search

**实现方案**：
- 后端新增 `backend/app/services/embedding_service.py`
  - 使用 sentence-transformers (all-MiniLM-L6-v2) 本地生成向量嵌入
  - 嵌入存储为 numpy `.npy` 文件，与记忆数据并列
  - 新端点: `GET /api/search/semantic?q=...&limit=10`
  - 无匹配时回退到关键词搜索
- 前端扩展搜索栏：keyword ↔ semantic 切换
  - 结果显示相似度百分比徽章 (0-100%)
  - "语义匹配" vs "关键词匹配" 不同高亮样式
- 写入时后台任务自动生成嵌入

**验收标准**：
- AC-F33-1: 搜索 "security" 能找到 "vulnerability"、"authentication"、"threat" 相关记忆
- AC-F33-2: 每个结果显示相似度百分比 (0-100%)
- AC-F33-3: 搜索栏支持关键词/语义搜索切换
- AC-F33-4: 单条记忆嵌入生成 <2s
- AC-F33-5: 嵌入模型不可用时优雅降级（回退关键词搜索）

**依赖**: `sentence-transformers`, `numpy`

---

#### F-34 AI Auto-Tagging & Summarization

**实现方案**：
- 后端新增 `backend/app/services/llm_service.py`
  - 可插拔 LLM 提供商（OpenAI API / 本地 Ollama）
  - 创建/更新记忆时自动生成 3-5 个建议标签
  - 新端点: `POST /api/memories/{id}/suggest-tags` → 建议概念
  - 新端点: `POST /api/memories/{id}/summarize` → 1-2 句摘要
  - 新端点: `POST /api/memories/bulk-auto-tag` → 批量处理未标记记忆
- 前端：
  - 创建/编辑弹窗中显示 AI 建议标签（可点击接受/拒绝）
  - 展开记忆视图的 "✨ Summarize" 按钮
  - 设置页：配置 LLM 提供商，启用/禁用自动标记
- 配置：`LLM_PROVIDER` 环境变量 (openai|ollama|none)

**验收标准**：
- AC-F34-1: 创建记忆时显示 AI 建议标签，可接受/拒绝
- AC-F34-2: "Summarize" 在 5s 内生成 1-2 句摘要
- AC-F34-3: 批量自动标记处理所有未标记记忆，带进度指示
- AC-F34-4: 未配置 LLM 时功能优雅禁用
- AC-F34-5: 建议标签与记忆内容相关（目标 >70% 接受率）

**依赖**: `openai` (可选), `httpx` (Ollama)

---

#### F-35 Command Palette (⌘K)

**实现方案**：
- 前端新增 `frontend/src/components/CommandPalette.vue`
  - `⌘K` (Mac) / `Ctrl+K` (Windows/Linux) 触发
  - 模糊搜索：导航项、最近记忆、操作命令
  - 默认显示最近使用项
  - 键盘导航：↑↓ 选择，Enter 执行，Esc 关闭
  - 分区：Actions / Navigate / Recent Memories / Settings
  - 毛玻璃背景，居中弹窗，Apple 风格设计
- 命令列表：
  - `Go to Dashboard`、`Go to Graph`、`Go to Timeline` 等
  - `Create Memory`、`Export All`、`Run Diagnostics`、`Backup Now`
  - `Search: {query}` → 跳转搜索并预填查询
  - `Toggle Dark Mode`、`Toggle Keyboard Shortcuts`

**验收标准**：
- AC-F35-1: ⌘K/Ctrl+K 在任意视图打开命令面板
- AC-F35-2: 输入文字进行模糊匹配过滤
- AC-F35-3: Enter 执行选中命令，Esc 关闭面板
- AC-F35-4: 最近记忆出现在结果中，点击跳转详情
- AC-F35-5: 面板打开 <100ms，搜索结果 <50ms
- AC-F35-6: 暗色模式视觉一致

---

#### F-36 Bulk Operations Toolbar

**实现方案**：
- 前端：
  - 每张记忆卡片添加复选框（批量模式激活时显示）
  - 工具栏 "Select" 按钮激活批量模式
  - 底部浮动操作栏：显示选中数量 + 操作按钮
  - 操作：Delete Selected / Export Selected / Add Tag / Change Type / Archive
  - "Select All" / "Select None" 切换
  - 键盘：`Shift+Click` 范围选择，`Cmd+A` 全选
- 后端：
  - 新端点 `POST /api/agentmemory/bulk`
  - 请求体: `{ ids: [...], action: "delete"|"archive"|"tag"|"retag", params: {...} }`
  - 返回: `{ success: count, failed: count, errors: [...] }`
  - 审计日志记录每次批量操作

**验收标准**：
- AC-F36-1: 点击 "Select" 后出现复选框
- AC-F36-2: 可选择多条记忆并批量删除（需确认）
- AC-F36-3: 批量标记：为所有选中记忆添加标签
- AC-F36-4: 批量导出：下载选中记忆为 JSON
- AC-F36-5: >10 条操作显示进度指示
- AC-F36-6: 批量操作记录在审计日志
- AC-F36-7: Shift+Click 支持范围选择

---

#### F-37 Memory Activity Heatmap

**实现方案**：
- 后端：
  - 新端点: `GET /api/metrics/heatmap?metric=created|accessed|modified&days=365`
  - 返回: `{ "2026-01-15": 5, "2026-01-16": 12, ... }`
  - 从审计日志 + 记忆时间戳聚合数据
- 前端：
  - 新组件 `frontend/src/components/ActivityHeatmap.vue`
  - GitHub 风格网格：52 列 × 7 行
  - 颜色刻度：浅→深（5 级）基于活动数量
  - 悬停提示：「1月15日创建了 12 条记忆」
  - 切换：Created / Accessed / Modified 指标
  - 点击某天 → 过滤到该日期的记忆列表
  - 响应式：≥320px 宽度可水平滚动
  - 集成到 DashboardView

**验收标准**：
- AC-F37-1: 过去 365 天热力图正确渲染，颜色编码准确
- AC-F37-2: 悬停显示日期和数量提示
- AC-F37-3: 支持切换 created/accessed/modified 视图
- AC-F37-4: 点击某天跳转到该日期过滤的记忆列表
- AC-F37-5: ≥320px 屏幕响应式显示
- AC-F37-6: 暗色模式兼容

---

#### F-38 Plugin System

**实现方案**：
- 后端：
  - 新目录 `backend/app/plugins/` + 插件加载器
  - `backend/app/core/plugin_manager.py`:
    - 扫描 `plugins/` 目录中含 `plugin.json` 清单的 Python 文件
    - 清单格式: `{ "name": "...", "version": "...", "hooks": ["on_memory_create", ...] }`
    - 钩子: `on_memory_create` / `on_memory_update` / `on_memory_delete` / `on_search` / `on_export`
    - 插件在隔离异步任务中运行，超时 5s
  - 新端点: `GET /api/plugins` → 已安装插件列表 + 状态
  - 新端点: `POST /api/plugins/{name}/enable|disable`
  - 示例插件: `plugins/auto_translate/` — 自动翻译记忆内容为英文
- 前端：
  - 新视图 `frontend/src/views/PluginsView.vue`
  - 已安装插件列表，启用/禁用开关
  - 插件详情：名称、版本、描述、钩子、状态
  - 日志查看器：最近插件执行日志
  - "Install Plugin" 按钮（上传 .zip 或粘贴 git URL）

**验收标准**：
- AC-F38-1: `plugins/` 目录中的插件启动时自动发现
- AC-F38-2: 创建新记忆时触发 `on_memory_create` 钩子
- AC-F38-3: 插件可启用/禁用，无需重启
- AC-F38-4: 插件执行超时 (5s) 防止挂起
- AC-F38-5: 插件错误不崩溃主应用
- AC-F38-6: UI 显示插件列表、状态和最近日志
- AC-F38-7: 示例 auto_translate 插件端到端工作

---

### P8 Implementation Order

| Week | Features | Rationale |
|------|----------|-----------|
| Week 1 | F-35 Command Palette + F-36 Bulk Operations | UX polish, no new dependencies |
| Week 2 | F-37 Heatmap + F-33 Semantic Search | Data features, backend-heavy |
| Week 3 | F-34 AI Auto-Tagging + F-38 Plugin System | AI & extensibility |
| Week 4 | Integration testing, bug fixes, documentation | Quality assurance |

### P8 New Dependencies

| Package | Purpose | Size |
|---------|---------|------|
| sentence-transformers | Embedding generation | ~80MB |
| numpy | Vector operations | ~15MB |
| openai | LLM API (optional) | ~1MB |
| httpx | Ollama HTTP client | ~1MB |
|| rapidfuzz | Fuzzy search for command palette | ~2MB |

---

## P9 — Data Governance & Advanced Intelligence

> **Phase**: P9
> **Theme**: Data Governance, Collaborative Intelligence & Operational Resilience
> **Features**: 6 (F-39 through F-44)
> **Estimated Effort**: 3-4 weeks
> **Prerequisites**: P8 completed (semantic search, AI auto-tagging, plugin system, etc.)

### P9 Design Principles

- **数据治理优先**：随着记忆数量增长，数据质量和合规性成为核心需求
- **智能化深化**：在 P8 的语义搜索和 AI 标注基础上，进一步提升认知能力
- **协作可分享**：记忆不再局限于单人使用，支持团队级共享与讨论
- **运维可观测**：主动发现异常，容量规划，确保系统长期健康运行
- **体验打磨**：自定义视图满足个性化需求，拖拽提升操作效率

### P9 Feature Table

| # | Feature | Description | User Value | Complexity | Layer |
|---|---------|-------------|------------|------------|-------|
| **F-39** | Natural Language Query (NLQ) | Convert natural language questions into structured API queries using LLM | Non-technical users can query memory system conversationally; "show me all bugs from last week" just works | 🟠 High | Backend + Frontend |
| **F-40** | Memory Clustering | Automatically group memories into topic clusters using embedding similarity | Discover hidden topic structures; navigate 100+ memories by theme instead of scrolling | 🟡 Medium | Backend + Frontend |
| **F-41** | Sensitive Info Masking (PII Redaction) | Detect and mask sensitive data (API keys, emails, phone numbers, passwords) in memory content | Compliance with data governance policies; prevent accidental credential leakage in shared views | 🟡 Medium | Backend + Frontend |
| **F-42** | Memory Sharing | Generate shareable links for individual memories or collections with access control | Collaborate with team members without giving full system access; embed memory links in docs/chat | 🟡 Medium | Backend + Frontend |
| **F-43** | Anomaly Detection & Alerts | Monitor memory system health metrics and trigger alerts on anomalies (sudden drops, unusual patterns) | Proactive issue detection instead of reactive debugging; catch data corruption early | 🟠 High | Backend + Frontend |
| **F-44** | Custom Dashboard Views | User-configurable dashboard layouts with draggable widget placement | Personalized workspace; each user sees what matters most to them first | 🟡 Medium | Frontend |

### P9 Detailed Designs

#### F-39 Natural Language Query (NLQ)

**问题**: 现有搜索支持关键词和语义匹配，但用户仍需理解搜索语法。非技术用户想查询"上周创建的所有 bug 类型的记忆"时，需要手动组合多个过滤器。

**实现方案**:
- 后端新增 `backend/app/services/nlq_service.py`
  - 利用 P8 已有的 LLM 服务（llm_service.py），将自然语言转换为结构化查询
  - NLQ Pipeline: 用户输入 → LLM 解析为 JSON 查询条件 → 执行标准 API 查询 → 返回结果
  - 新端点: `POST /api/search/nlq` 接收 `{ question: string }` 返回查询结果 + 解析出的查询条件
  - 查询条件映射: 支持 type、date_range、strength_range、tags、profile、sort_by 等维度
  - 安全: 限制 LLM 只能输出 JSON 查询条件，不能执行任意代码
- 前端扩展搜索栏
  - 搜索栏增加 "🤖 Ask" 模式切换（关键词 / 语义 / 自然语言）
  - 自然语言模式下显示对话式 UI：输入框 + 结果面板 + 解析条件展示
  - 解析条件可编辑（用户确认/修改 LLM 理解的查询意图）
  - 查询历史保存（最近 10 条 NLQ 查询）
- 前端新增 `frontend/src/components/NLQPanel.vue`

**验收标准**:
- AC-F39-1: 输入"上周创建的 bug 记忆"返回正确过滤结果
- AC-F39-2: 显示 LLM 解析出的结构化查询条件（type=bug, date=last_week）
- AC-F39-3: 用户可编辑解析条件并重新查询
- AC-F39-4: 未配置 LLM 时自然语言模式不可用，显示提示
- AC-F39-5: 查询响应时间 <5s（含 LLM 解析时间）
- AC-F39-6: 查询历史可点击重用

**依赖**: P8 F-34（LLM 服务）, P8 F-33（语义搜索基础设施）

---

#### F-40 Memory Clustering

**问题**: 记忆数量超过 100 条后，线性列表难以发现主题结构。用户不知道自己的记忆主要集中在哪些领域，哪些领域记忆薄弱。

**实现方案**:
- 后端新增 `backend/app/services/clustering_service.py`
  - 利用 P8 的 embedding 服务获取所有记忆的向量表示
  - 聚类算法: K-Means（自动确定 K 值，Silhouette Score 评估）或 HDBSCAN
  - 每个聚类自动生成标签（取该聚类中 TF-IDF 最高的 concepts 作为聚类名称）
  - 新端点: `GET /api/clusters` → 返回聚类列表 `{clusters: [{id, name, count, memory_ids, centroid_concepts}]}`
  - 新端点: `GET /api/clusters/{id}` → 返回该聚类的详细记忆列表
  - 缓存: 聚类结果缓存 1 小时，记忆变更时自动失效
- 前端新增 `frontend/src/views/ClustersView.vue`
  - 聚类可视化: 气泡图（每个气泡 = 一个聚类，大小 = 记忆数量，颜色 = 类型分布）
  - 点击气泡展开该聚类的记忆列表
  - 聚类间关系: 可选的 2D 降维投影（t-SNE/UMAP）散点图
  - Sidebar 集成: 智能集合区域增加 "按主题浏览" 入口

**验收标准**:
- AC-F40-1: 访问 /clusters 返回 ≥3 个有意义的聚类
- AC-F40-2: 每个聚类有可理解的名称（基于 concepts）
- AC-F40-3: 气泡图正确反映聚类大小和关系
- AC-F40-4: 点击聚类可查看其包含的记忆列表
- AC-F40-5: 聚类结果在 100 条记忆时生成时间 <10s
- AC-F40-6: 新增记忆后聚类自动更新（缓存失效）

**依赖**: P8 F-33（embedding 服务）

---

#### F-41 Sensitive Info Masking (PII Redaction)

**问题**: 记忆中可能包含 API 密钥、密码、邮箱、电话号码等敏感信息。在共享视图或导出时存在数据泄露风险。

**实现方案**:
- 后端新增 `backend/app/services/redaction_service.py`
  - 正则表达式检测器: API keys (`sk-...`, `AKIA...`), emails, phone numbers, IP addresses, passwords (`password=xxx`)
  - 可选 LLM 增强检测: 识别正则无法覆盖的敏感模式（如内部系统名称、项目代号）
  - 替换策略: `sk-abc123...xyz` → `sk-****...****`，`user@example.com` → `u***@***.com`
  - 新端点: `POST /api/memories/{id}/redact` → 返回脱敏后的内容（不修改原数据）
  - 新端点: `POST /api/memories/scan-pii` → 扫描所有记忆，返回包含敏感信息的记忆列表
  - 新端点: `GET /api/memories/pii-report` → 敏感信息统计报告
- 前端集成
  - 记忆卡片上显示 🔒 图标标记含敏感信息的记忆
  - 展开记忆时默认显示脱敏内容，点击 "Show Original" 需二次确认
  - 设置页: 配置脱敏规则（启用/禁用各类检测器）
  - 导出时自动脱敏选项（默认开启）
  - PII 扫描报告页面（Dashboard 子视图）

**验收标准**:
- AC-F41-1: 包含 `sk-` 前缀的 API key 被自动检测并标记
- AC-F41-2: 邮箱地址被检测并部分脱敏
- AC-F41-3: PII 扫描报告列出所有含敏感信息的记忆
- AC-F41-4: 导出时可选择自动脱敏
- AC-F41-5: 查看原始内容需要确认操作（防止误操作）
- AC-F41-6: 脱敏不影响原始数据存储

**依赖**: 无（独立功能）

---

#### F-42 Memory Sharing

**问题**: 记忆数据封闭在系统内部，无法与团队成员或外部协作者分享特定记忆条目。

**实现方案**:
- 后端新增 `backend/app/services/sharing_service.py`
  - 分享链接生成: `POST /api/memories/{id}/share` → 返回 `{share_id, share_url, expires_at, access_level}`
  - 访问级别: `view`（只读）/ `comment`（可评论）/ `edit`（可编辑）
  - 过期时间: 1小时/1天/7天/30天/永不过期
  - 分享链接数据存储: `backend/data/shares.json`
  - 公开访问端点: `GET /api/shared/{share_id}` → 无需认证即可访问
  - 分享管理: `GET /api/shares` → 列出所有活跃分享链接
  - 撤销分享: `DELETE /api/shares/{share_id}`
- 前端新增 `frontend/src/components/ShareModal.vue`
  - 记忆详情页增加 "Share" 按钮
  - 分享弹窗: 访问级别选择 + 过期时间选择 + 生成链接
  - 链接复制到剪贴板 + 二维码显示
  - 分享管理页面: 列出所有分享链接，支持撤销
  - 批量分享: 选中多条记忆生成集合分享链接
- 安全
  - 分享链接包含不可猜测的 UUID
  - 可选密码保护
  - 访问日志记录（谁在什么时候访问了分享链接）

**验收标准**:
- AC-F42-1: 为单条记忆生成分享链接，未登录用户可查看
- AC-F42-2: 分享链接在过期后不可访问
- AC-F42-3: 支持 view/comment/edit 三种访问级别
- AC-F42-4: 可撤销分享链接
- AC-F42-5: 批量分享生成集合链接
- AC-F42-6: 分享时自动应用 PII 脱敏（依赖 F-41）

**依赖**: F-41（分享时自动脱敏）

---

#### F-43 Anomaly Detection & Alerts

**问题**: 记忆系统运行中的异常（数据突然丢失、strength 异常分布、API 响应突增）往往在用户发现问题后才被发现，缺乏主动监控。

**实现方案**:
- 后端新增 `backend/app/services/anomaly_service.py`
  - 监控指标:
    - 记忆总数变化率（日环比 >20% 标记异常）
    - 平均 strength 变化（周环比 >15% 标记异常）
    - API 响应时间 P95（>500ms 标记异常）
    - 错误率（>5% 标记异常）
    - 记忆类型分布偏移（某类型占比突变 >30%）
  - 检测算法: 移动平均 + 标准差阈值（Z-score > 2 标记异常）
  - 新端点: `GET /api/anomalies` → 返回检测到的异常列表
  - 新端点: `GET /api/anomalies/health` → 系统整体健康评分（0-100）
  - 新端点: `POST /api/anomalies/check` → 手动触发检测
  - 告警通知: 集成 P4 的 webhook/飞书通知，异常时自动发送
  - 定时任务: 每小时自动检测一次
- 前端新增 `frontend/src/views/AnomaliesView.vue`
  - 异常时间线: 按时间倒序展示检测到的异常事件
  - 健康评分仪表盘: 圆形进度条 + 各维度评分分解
  - 异常详情: 异常类型、发生时间、影响范围、建议修复操作
  - 告警配置: 设置告警阈值和通知渠道
  - Dashboard 集成: 健康评分作为卡片显示在主仪表盘

**验收标准**:
- AC-F43-1: 记忆数量突变时检测到异常并记录
- AC-F43-2: 健康评分正确反映系统状态
- AC-F43-3: 异常发生时通过 webhook 发送告警
- AC-F43-4: 告警阈值可配置
- AC-F43-5: 异常历史可追溯（保留 30 天）
- AC-F43-6: Dashboard 显示当前健康评分

**依赖**: P4 F-26（Webhook 通知）, P5 F-32（性能监控基础设施）

---

#### F-44 Custom Dashboard Views

**问题**: 所有用户看到相同的 Dashboard 布局，但不同角色（开发者、PM、运维）关注的指标不同。

**实现方案**:
- 前端新增 `frontend/src/components/DashboardWidget.vue` 基础组件
  - 可用 Widget 列表:
    - 记忆总数统计（已有）
    - 类型分布饼图（已有）
    - 活动热力图（P8 F-37）
    - 健康评分（F-43）
    - 最近修改记忆列表
    - 聚类概览（F-40）
    - PII 告警摘要（F-41）
    - 异常事件时间线（F-43）
    - 衰减曲线（P3 F-22）
    - 快速操作面板
  - 每个 Widget 支持: 标题、刷新、全屏、移除
- 前端新增 `frontend/src/views/CustomDashboard.vue`
  - 拖拽布局: 使用 `vue-grid-layout` 或 `@vueuse/integrations` 实现网格拖拽
  - 布局持久化: 保存到 localStorage + 后端 `PUT /api/dashboard/layout`
  - 预设模板: "开发者视图" / "运维视图" / "PM 视图" / "默认视图"
  - Widget 添加面板: 从可用 Widget 列表拖入 Dashboard
  - 响应式: 移动端自动堆叠为单列
- 后端新增 `backend/app/routers/dashboard.py`
  - `GET /api/dashboard/layout` → 获取用户保存的布局
  - `PUT /api/dashboard/layout` → 保存布局配置
  - 布局数据: `{widgets: [{id, type, x, y, w, h, config}], preset: string}`

**验收标准**:
- AC-F44-1: Dashboard 支持拖拽调整 Widget 位置和大小
- AC-F44-2: Widget 可添加/移除
- AC-F44-3: 布局配置刷新后保持（localStorage 持久化）
- AC-F44-4: 提供 ≥3 种预设布局模板
- AC-F44-5: 移动端自动适配单列布局
- AC-F44-6: 每个 Widget 独立加载和刷新

**依赖**: P8 F-37（热力图 Widget）, F-43（健康评分 Widget）

---

### P9 Implementation Order

| Week | Features | Rationale |
|------|----------|-----------|
| Week 1 | F-41 (PII Masking) + F-44 (Custom Dashboard) | Independent features, no cross-dependencies; PII masking is a governance prerequisite for sharing |
| Week 2 | F-42 (Memory Sharing) + F-40 (Clustering) | Sharing depends on PII masking; Clustering depends on P8 embeddings |
| Week 3 | F-39 (NLQ) + F-43 (Anomaly Detection) | Both are intelligence features with backend-heavy work |
| Week 4 | Integration testing, E2E testing, documentation | Quality assurance and cross-feature integration |

### P9 Dependency Graph

```
F-39 NLQ ─────────────── 依赖 P8 F-34 (LLM 服务)
F-40 Clustering ──────── 依赖 P8 F-33 (Embedding 服务)
F-41 PII Masking ─────── 独立
F-42 Memory Sharing ──── 依赖 F-41 (分享时自动脱敏)
F-43 Anomaly Detection ─ 依赖 P4 F-26 (Webhook) + P5 F-32 (性能监控)
F-44 Custom Dashboard ── 依赖 P8 F-37 (热力图 Widget) + F-43 (健康评分 Widget)
```

### P9 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| NLQ 准确率不足 | Medium | Medium | 显示解析条件供用户修正；回退到结构化搜索 |
| 聚类效果差（数据量少） | Medium | Low | 数据 <30 条时禁用聚类，显示引导文案 |
| PII 检测误报 | Medium | Medium | 提供白名单机制；用户可标记误报 |
| 分享链接安全 | Low | High | UUID 不可猜测 + 可选密码 + 过期机制 |
| 自定义布局数据损坏 | Low | Low | 布局数据校验 + 重置为默认布局选项 |

### P9 New Dependencies

| Package | Purpose | Size |
|---------|---------|------|
| scikit-learn | K-Means 聚类 + TF-IDF | ~30MB |
| hdbscan | 密度聚类（可选，比 K-Means 更智能） | ~5MB |
| vue-grid-layout | 拖拽网格布局 | ~50KB |
| qrcode | 分享链接二维码生成 | ~200KB |

---

## P13 — UX Polish, Smart Collections & Operational Intelligence

> **Phase**: P13
> **Theme**: User Experience Polish, Smart Organization & Proactive Intelligence
> **Features**: 6 (F-63 through F-68)
> **Estimated Effort**: 3-4 weeks
> **Prerequisites**: P0-P12 completed (85 features total)

### P13 Feature Table

| # | Feature | Description | Complexity | Layer |
|---|---------|-------------|------------|-------|
| **F-63** | Memory Favorites & Pin-to-Top | Star/pin memories for instant access; favorites panel in sidebar | 🟢 Low | Frontend + Backend |
| **F-64** | Saved Searches & Smart Collections | Save search queries as dynamic auto-updating collections | 🟡 Medium | Backend + Frontend |
| **F-65** | Memory Linking & Relation Graph | Manual links between memories with interactive graph visualization | 🟡 Medium | Backend + Frontend |
| **F-66** | Guided Onboarding Tour | Interactive first-time walkthrough highlighting key features | 🟢 Low | Frontend |
| **F-67** | Advanced Export & Reporting | PDF/HTML reports with customizable templates | 🟡 Medium | Backend + Frontend |
| **F-68** | Memory Health Scanner | Proactive health check: orphaned concepts, duplicates, quality gaps | 🟡 Medium | Backend + Frontend |

### P13 Detailed Designs

#### F-63 Memory Favorites & Pin-to-Top

**Problem**: Important memories get buried as the list grows. No quick-access mechanism.

**Solution**: Star/pin system with favorites panel.

**Implementation**:
- Backend: `PUT /api/agentmemory/{id}/favorite` toggle, `GET /api/agentmemory/favorites`, `backend/cache/favorites.json`
- Frontend: FavoriteButton.vue (star icon), FavoritesPanel.vue (sidebar section), "Favorites first" sort option

**Acceptance Criteria**:
- AC-F63-1: Click star toggles favorite
- AC-F63-2: Favorites appear in sidebar panel
- AC-F63-3: Persist across refreshes
- AC-F63-4: "Favorites first" sort option
- AC-F63-5: Visual state correct
- AC-F63-6: Panel allows click-to-navigate

#### F-64 Saved Searches & Smart Collections

**Problem**: Repeated searches; no dynamic grouping.

**Solution**: Named collections with auto-evaluating queries.

**Implementation**:
- Backend: `backend/app/services/collections_service.py`, CRUD endpoints, query evaluation engine
- Frontend: CollectionsView.vue, CollectionCard.vue, CollectionEditor.vue, "Save as Collection"

**Acceptance Criteria**:
- AC-F64-1: Create collection with filters, correct matching
- AC-F64-2: Auto-update when memories change
- AC-F64-3: Save from search results
- AC-F64-4: 4+ query dimensions
- AC-F64-5: Pre-built templates work
- AC-F64-6: Persist across restarts

#### F-65 Memory Linking & Relation Graph

**Problem**: No explicit relationship modeling between memories.

**Solution**: Manual typed links with interactive graph visualization.

**Implementation**:
- Backend: `backend/app/services/linking_service.py`, graph endpoints
- Frontend: GraphView.vue (D3.js force graph), LinkCreator.vue, RelatedMemories.vue

**Acceptance Criteria**:
- AC-F65-1: Create typed link between memories
- AC-F65-2: Graph shows nodes/edges
- AC-F65-3: Click node shows details
- AC-F65-4: Color-coded relation types
- AC-F65-5: "Link to..." action on cards
- AC-F65-6: Interactive zoom/pan/drag
- AC-F65-7: Subgraph view per memory

#### F-66 Guided Onboarding Tour

**Problem**: Feature-rich interface overwhelms new users.

**Solution**: Step-by-step interactive tour.

**Implementation**:
- Frontend only: useOnboarding.ts, OnboardingTour.vue, TourTooltip.vue
- 8 tour steps, auto-trigger on first visit, replayable

**Acceptance Criteria**:
- AC-F66-1: Auto-starts on first visit
- AC-F66-2: Highlights UI elements
- AC-F66-3: Next/Previous navigation
- AC-F66-4: Skip tour option
- AC-F66-5: Persisted in localStorage
- AC-F66-6: Replayable
- AC-F66-7: Correct positioning

#### F-67 Advanced Export & Reporting

**Problem**: Raw export insufficient for stakeholder reporting.

**Solution**: Template-based PDF/HTML report generation.

**Implementation**:
- Backend: report_service.py, Jinja2 templates, PDF via weasyprint
- Frontend: ReportsView.vue, template selector, report history

**Acceptance Criteria**:
- AC-F67-1: HTML report generation
- AC-F67-2: PDF report generation
- AC-F67-3: Charts and statistics included
- AC-F67-4: Custom filters applied
- AC-F67-5: Downloadable from history
- AC-F67-6: <15s for 200 memories

#### F-68 Memory Health Scanner

**Problem**: No automated quality monitoring.

**Solution**: Proactive scanner with actionable recommendations and auto-fix.

**Implementation**:
- Backend: health_scanner_service.py, 7 health checks, auto-fix
- Frontend: HealthScanView.vue, HealthScoreGauge.vue, IssueCard.vue

**Acceptance Criteria**:
- AC-F68-1: Detects empty metadata
- AC-F68-2: Detects duplicates via embeddings
- AC-F68-3: Score 0-100 computed correctly
- AC-F68-4: Auto-fix for empty concepts
- AC-F68-5: <10s for 200 memories
- AC-F68-6: Visual gauge reflects severity
- AC-F68-7: Scan history tracked
