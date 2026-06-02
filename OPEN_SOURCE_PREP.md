# Memory Viewer v2 — GitHub 开源准备计划

> **目标版本**: v1.0.0 (开源首发)  
> **日期**: 2026-05-31  
> **状态**: 准备中

---

## 一、现状分析

### 1.1 代码规模

| 层级 | 当前数量 | 精简后目标 |
|------|----------|------------|
| 前端视图 (views) | 47 | ~12 |
| 后端路由 (routers) | 50+ | ~15 |
| 路由文件行数 | 4,097 | ~1,500 |
| Feature Flags | 39 | ~10 (核心功能) |

### 1.2 核心问题

1. **功能膨胀**: 从 8 个 P0 功能扩展到 50+ 个功能
2. **导航复杂**: 侧边栏 6 个分组，30+ 菜单项
3. **文档缺失**: 无 README、无 CONTRIBUTING、无 LICENSE
4. **代码碎片**: 大量半完成功能，API 和 UI 不匹配
5. **依赖臃肿**: 可能包含未使用的 npm/pip 包

---

## 二、精简策略

### 2.1 保留功能清单 (开源 v1.0)

#### 核心功能 (必须)

| 功能 | 路由 | 描述 |
|------|------|------|
| **首页浏览** | `/` | 记忆列表，支持搜索、分页、排序 |
| **记忆详情** | `/memory/:id` | 查看单条记忆完整内容 |
| **记忆创建** | `POST /api/agentmemory` | 创建新记忆 |
| **记忆编辑** | `PUT /api/agentmemory/:id` | 编辑已有记忆 |
| **记忆删除** | `DELETE /api/agentmemory/:id` | 删除记忆 |
| **记忆搜索** | `/api/search` | 关键词搜索 |
| **Hermes Memory** | `/hermes` | 查看 Hermes MEMORY.md |
| **Profiles** | `/profiles` | 查看多 profile 记忆 |
| **收藏夹** | Favorites | 收藏重要记忆 |
| **智能分类** | Collections | 基于规则的智能分类 |
| **导出** | `/api/agentmemory/export` | 导出 JSON/Markdown |
| **设置** | `/settings` | 基础设置 |

#### 移除功能清单

| 分组 | 移除的视图 | 移除的原因 |
|------|------------|------------|
| **分析类** | Dashboard, Analytics, Anomalies, CrossAgent, Clusters, Graph | 需要 ML/embedding，当前数据量不需要 |
| **管理类** | Audit, Governance, Instances, Snapshots | 运维功能，普通用户不需要 |
| **工具类** | ApiPlayground, LLM Usage, Health Scan, Reports | 开发者/运维专用 |
| **高级类** | Timeline, Lineage, Conflicts, Annotations, Diagnostics | 高级功能，v2 可考虑 |
| **协作类** | Workspaces, Templates, Subscriptions, Workflows | v2 协作功能 |
| **高级 AI** | Semantic Search, NLQ, RAG, Dedup, AutoTag, Recommendations | 需要外部 LLM/API |
| **PII 安全** | Redaction, Sharing | 需要额外安全审计 |
| **其他** | Plugins, SSO, MCP Server, Realtime | 高级集成功能 |

### 2.2 后端路由精简

**保留的路由**:

```
agentmemory    - 核心 CRUD
hermes_memory  - Hermes MEMORY.md
profiles       - Profile 列表
search         - 搜索
health         - 健康检查
changelog      - 版本日志
sources        - 统一数据源
dashboard      - 统计 (简化版)
favorites       - 收藏夹
collections    - 智能分类
```

**移除的路由模块**:

```
analytics, annotations, anomalies, audit, auto_tag, 
backup, clusters, conflicts, cross_agent, decay, 
dedup, diagnostics, digest, feishu_summary, graph, 
governance, heatmap, instances, lineage, links, 
llm_usage, mcp, memory_health, metrics, nlq, plugins, 
rag, realtime, redaction, reports, semantic_search, 
sharing, snapshots, subscriptions, templates, versioning, 
webhook, workflows, workspaces, sso, cli, compare, comparison
```

---

## 三、开源文档准备

### 3.1 必须文档

| 文档 | 位置 | 内容要点 |
|------|------|----------|
| **README.md** | 根目录 | 项目介绍、快速开始、功能列表、截图 |
| **CONTRIBUTING.md** | 根目录 | 开发流程、代码规范、PR 流程 |
| **LICENSE** | 根目录 | MIT License |
| **CHANGELOG.md** | 根目录 | 版本变更记录 |
| **API.md** | docs/ | API 端点文档 |
| **ARCHITECTURE.md** | docs/ | 系统架构图、技术栈 |

### 3.2 README.md 结构

```markdown
# Memory Viewer

Agent Memory Management Dashboard

[截图]

## 特性

- 🔍 记忆搜索与筛选
- 📊 多维度统计
- 🔄 记忆 CRUD
- 📦 导入/导出
- 🌐 多语言支持

## 快速开始

### Docker 部署
docker run -p 8501:8501 ...

### 开发部署
cd backend && pip install -r requirements.txt
cd frontend && npm install && npm run dev

## API

见 docs/API.md

## License

MIT
```

---

## 四、代码清理

### 4.1 前端清理

```
删除文件:
- views/: DashboardView, AnalyticsView, AnomaliesView, CrossAgentView,
         ClustersView, GraphView, AuditView, GovernanceView, InstancesView,
         SnapshotsView, ApiPlaygroundView, LlmUsageView, HealthScanView,
         ReportsView, TimelineView, LineageView, ConflictsView, AnnotationsView,
         DiagnosticsView, TemplatesView, WorkspacesView, SubscriptionsView,
         WorkflowsView, PluginsView, CustomDashboard

清理组件:
- 移除 SmartCollections 中未使用的分类规则
- 简化侧边栏导航
- 清理未使用的 composables
```

### 4.2 后端清理

```
删除路由模块 (整个文件):
- analytics.py, annotations.py, anomalies.py, audit.py, auto_tag.py,
  backup.py, clusters.py, conflicts.py, cross_agent.py, decay.py,
  dedup.py, diagnostics.py, digest.py, feishu_summary.py, graph.py,
  governance.py, heatmap.py, instances.py, lineage.py, links.py,
  llm_usage.py, mcp.py, memory_health.py, metrics.py, nlq.py,
  plugins.py, rag.py, realtime.py, redaction.py, reports.py,
  semantic_search.py, sharing.py, snapshots.py, subscriptions.py,
  templates.py, versioning.py, webhook.py, workflows.py, workspaces.py,
  sso.py, cli.py, compare.py, comparison.py

清理 main.py:
- 移除对应的 import 和 include_router
- 移除未使用的 middleware
```

### 4.3 配置清理

```python
# /api/config 响应简化
features = {
    "search": True,
    "crud": True,
    "export": True,
    "favorites": True,
    "collections": True,
    "hermes_memory": True,
    "profiles": True,
}
```

---

## 五、执行计划

### Phase 1: 代码精简 (预计 2-4 小时)

- [ ] 1.1 删除前端未使用的视图文件
- [ ] 1.2 简化侧边栏导航到 ~10 个菜单项
- [ ] 1.3 更新路由表
- [ ] 1.4 删除后端未使用的路由模块
- [ ] 1.5 清理 main.py import
- [ ] 1.6 简化 /api/config 响应
- [ ] 1.7 清理未使用的 npm/pip 依赖

### Phase 2: 功能打磨 (预计 2-4 小时)

- [ ] 2.1 移动端体验完善
- [ ] 2.2 核心 CRUD 功能测试
- [ ] 2.3 搜索功能验证
- [ ] 2.4 收藏夹功能验证
- [ ] 2.5 智能分类功能验证
- [ ] 2.6 导入/导出功能验证

### Phase 3: 开源文档 (预计 2-3 小时)

- [ ] 3.1 编写 README.md
- [ ] 3.2 编写 CONTRIBUTING.md
- [ ] 3.3 添加 LICENSE (MIT)
- [ ] 3.4 创建 CHANGELOG.md
- [ ] 3.5 创建 docs/API.md
- [ ] 3.6 创建 docs/ARCHITECTURE.md

### Phase 4: 发布准备 (预计 1-2 小时)

- [ ] 4.1 创建 screenshots/demo
- [ ] 4.2 验证 Docker 构建
- [ ] 4.3 GitHub repo 初始化
- [ ] 4.4 Git tag 设置
- [ ] 4.5 发布 Release

---

## 六、风险与注意事项

### 6.1 风险

1. **删除的文件可能有隐藏依赖** - 需要全面测试
2. **用户可能依赖某些功能** - 需要确认用户认可
3. **文档可能过时** - 需要仔细审核

### 6.2 注意事项

1. **保留分支策略** - 先在 `refactor/` 分支工作
2. **备份** - 删除前确认 git 暂存
3. **测试覆盖** - 确保核心功能被测试覆盖

---

## 七、验收标准

开源 v1.0 完成时必须满足:

- [ ] 前端只有 ~12 个视图
- [ ] 后端只有 ~15 个路由模块
- [ ] 侧边栏只有 ~10 个菜单项
- [ ] README.md 完整可读
- [ ] 项目可 Docker 部署
- [ ] 核心 CRUD 功能完整可用
- [ ] 移动端体验良好
- [ ] 无明显 bug
