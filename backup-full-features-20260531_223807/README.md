# Memory Viewer v2 完整功能备份

**备份时间**: 2026-05-31 22:38:07
**备份目的**: 开源精简时保留所有现有功能代码

## 内容索引

### 前端 views (41 个)
- AgentMemoryView
- AnalyticsView
- AnnotationsView
- AnomaliesView
- ApiDocsView
- ApiPlaygroundView
- ApiPlayground
- AuditView
- BackupView
- ClustersView
- CollectionsView
- CompareView
- ConflictsView
- CrossAgentView
- CustomDashboard
- DashboardView
- DiagnosticsView
- DigestView
- GovernanceView
- GraphView
- HealthScanView
- HermesMemoryView
- HomeView
- InstancesView
- LineageView
- LlmUsageView
- MemoryDetailView
- MetricsView
- PluginsView
- ProfilesView
- ReportsView
- SettingsView
- SnapshotsView
- SourcesView
- SubscriptionsView
- TemplatesView
- TimelineView
- VersionHistoryView
- VersionHistory
- WorkflowsView
- WorkspacesView

### 后端 routers (55 个)
- agentmemory
- analytics
- annotations
- anomalies
- audit
- auto_tag
- backup
- changelog
- cli
- clusters
- collections
- compare
- comparison
- conflicts
- cross_agent
- dashboard
- decay
- dedup
- diagnostics
- digest
- favorites
- feishu_summary
- governance
- graph
- health
- health_scan
- heatmap
- hermes_memory
- instances
- lineage
- links
- llm_usage
- mcp
- memory_health
- metrics
- nlq
- plugins
- profiles
- rag
- realtime
- recommendation
- redaction
- reports
- search
- semantic_search
- sharing
- snapshots
- sources
- sso
- subscriptions
- templates
- versioning
- webhook
- workflows
- workspaces

## 恢复方法

如果需要恢复某个功能：

1. 从备份目录复制对应文件到原位置
2. 在 main.py 或 router/index.ts 中添加对应的 import 和路由注册
3. 在侧边栏中添加对应的菜单项

## 功能分类

### 核心功能
- HomeView, AgentMemoryView, HermesMemoryView, MemoryDetailView
- ProfilesView, SettingsView
- agentmemory router (CRUD)

### 分析功能
- DashboardView, AnalyticsView, GraphView, ClustersView, AnomaliesView
- cross_agent router, analytics router, clusters router, anomalies router

### 管理功能
- AuditView, GovernanceView, InstancesView, SnapshotsView
- audit router, governance router, instances router, snapshots router

### 协作功能
- WorkspacesView, TemplatesView, SubscriptionsView, WorkflowsView
- workspaces router, templates router, subscriptions router, workflows router

### AI 功能
- SemanticSearchView, NLQView, RAGView, DedupView, AutoTagView
- semantic_search router, nlq router, rag router, dedup router, auto_tag router
