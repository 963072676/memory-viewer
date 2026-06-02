# Memory Viewer v2 — P4+P5 迭代计划

> **版本**: 1.0
> **日期**: 2026-05-29
> **基于**: PM_SPEC.md + P0~P3 完成状态 + 6 项 bugfix

---

## 0. 迭代概述

P4+P5 聚焦**协作集成**（飞书、Webhook、MCP）和**运维可观测**（诊断、审计、备份、监控、多实例）。

**目标**：完成路线图最后 10 个功能，实现 33/33 全部完成。

**预计工期**：8-10 个工作日

---

## 1. 当前状态

| 项目 | 状态 |
|------|------|
| P0~P3 功能 | 24/24 ✅ |
| Bug 修复 | 6/6 ✅ |
| 后端测试 | 92/92 ✅ |
| 服务运行 | 192.168.5.55:8501 ✅ |

---

## 2. 功能任务拆分

### 2.1 F-28 记忆系统诊断（P5，优先做）

| # | 任务 | 层 | 工作量 |
|---|------|-----|--------|
| F28-T1 | 创建诊断服务：检测重复（concepts Jaccard>0.6）、孤立 concepts（出现<2次）、strength 异常（<1 或 >9） | 后端 | 2h |
| F28-T2 | 新增 GET /api/diagnostics 端点 | 后端 | 0.5h |
| F28-T3 | 创建 DiagnosticsView.vue 诊断面板 | 前端 | 2h |
| F28-T4 | 测试 | 测试 | 1h |

**AC**：诊断报告包含 duplicates/orphaned_concepts/strength_anomalies 三项

### 2.2 F-29 操作审计日志（P5）

| # | 任务 | 层 | 工作量 |
|---|------|-----|--------|
| F29-T1 | 创建审计中间件（记录 method/path/body/status/time） | 后端 | 1.5h |
| F29-T2 | 审计存储：audit.jsonl（追加写入） | 后端 | 0.5h |
| F29-T3 | 新增 GET /api/audit?limit=50&action=create&type=agentmemory | 后端 | 1h |
| F29-T4 | 创建 AuditView.vue 审计日志页面 | 前端 | 2h |
| F29-T5 | 测试 | 测试 | 1h |

**AC**：所有增删改操作可追溯，支持时间/操作类型筛选

### 2.3 F-30 备份与恢复（P5）

| # | 任务 | 层 | 工作量 |
|---|------|-----|--------|
| F30-T1 | 备份服务：复制 agentmemory.json + hermes memories + webhook config 到 backups/ | 后端 | 1.5h |
| F30-T2 | 新增 POST /api/backup/create, GET /api/backup/list, POST /api/backup/restore | 后端 | 1.5h |
| F30-T3 | 创建 BackupView.vue 备份管理页面 | 前端 | 2h |
| F30-T4 | 测试 | 测试 | 1h |

**AC**：可创建备份、查看列表、一键恢复

### 2.4 F-24 记忆版本历史（P4）

| # | 任务 | 层 | 工作量 |
|---|------|-----|--------|
| F24-T1 | 版本存储：每次编辑保存快照到 versions/{id}.json | 后端 | 1.5h |
| F24-T2 | 新增 GET /api/agentmemory/{id}/versions, POST /api/agentmemory/{id}/versions/{version}/rollback | 后端 | 1.5h |
| F24-T3 | 创建 VersionHistory.vue 版本列表 + diff + 回滚 | 前端 | 3h |
| F24-T4 | 测试 | 测试 | 1h |

**AC**：编辑后自动保存版本，可查看历史、回滚到任意版本

### 2.5 F-23 多 Agent 记忆对比（P4）

| # | 任务 | 层 | 工作量 |
|---|------|-----|--------|
| F23-T1 | 对比服务：读取两个 profile 的 memories，按 title/concepts 做 diff | 后端 | 2h |
| F23-T2 | 新增 GET /api/memory/compare?profile_a=X&profile_b=Y | 后端 | 0.5h |
| F23-T3 | 创建 CompareView.vue 双栏对比布局 | 前端 | 3h |
| F23-T4 | 测试 | 测试 | 1h |

**AC**：双栏显示两个 profile 的记忆，高亮差异项

### 2.6 F-26 API Webhook 订阅（P4）

| # | 任务 | 层 | 工作量 |
|---|------|-----|--------|
| F26-T1 | 订阅管理：subscriptions.json 存储 | 后端 | 1h |
| F26-T2 | 新增 POST/DELETE/GET /api/webhook/subscriptions | 后端 | 1.5h |
| F26-T3 | 事件分发：复用 notification.py 基础设施 | 后端 | 1h |
| F26-T4 | 前端订阅管理 UI | 前端 | 2h |
| F26-T5 | 测试 | 测试 | 1h |

**AC**：可注册/注销 webhook，记忆变更时自动推送

### 2.7 F-25 飞书集成（P4，简化版）

| # | 任务 | 层 | 工作量 |
|---|------|-----|--------|
| F25-T1 | 摘要生成：统计记忆数量、类型分布、最新条目 | 后端 | 1h |
| F25-T2 | 新增 POST /api/memory/summary/send-to-feishu | 后端 | 1h |
| F25-T3 | 前端一键发送按钮 | 前端 | 1h |
| F25-T4 | 测试 | 测试 | 0.5h |

**AC**：一键发送记忆摘要到飞书群

### 2.8 F-32 性能监控（P5）

| # | 任务 | 层 | 工作量 |
|---|------|-----|--------|
| F32-T1 | 请求计时中间件（记录每个 API 的响应时间） | 后端 | 1h |
| F32-T2 | 新增 GET /api/metrics（avg/p50/p95/p99 延迟、请求计数） | 后端 | 1h |
| F32-T3 | 创建 MetricsView.vue 性能图表 | 前端 | 2.5h |
| F32-T4 | 测试 | 测试 | 1h |

**AC**：可查看 API 响应时间分布

### 2.9 F-31 多实例管理（P5，配置驱动）

| # | 任务 | 层 | 工作量 |
|---|------|-----|--------|
| F31-T1 | 读取 instances.json 配置 | 后端 | 0.5h |
| F31-T2 | 新增 GET /api/instances, 代理请求到其他实例 | 后端 | 2h |
| F31-T3 | 创建 InstancesView.vue 实例列表 + 切换 | 前端 | 2.5h |
| F31-T4 | 测试 | 测试 | 1h |

**AC**：可查看多实例列表，点击切换

### 2.10 F-27 MCP Server（P4，简化版）

| # | 任务 | 层 | 工作量 |
|---|------|-----|--------|
| F27-T1 | JSON-RPC 2.0 处理器 | 后端 | 2h |
| F27-T2 | 新增 POST /mcp/jsonrpc 端点 | 后端 | 1h |
| F27-T3 | 方法实现：memory.list, memory.get, memory.search, memory.create | 后端 | 2h |
| F27-T4 | 测试 | 测试 | 1.5h |

**AC**：JSON-RPC 调用返回正确结果

---

## 3. 开发顺序

```
F-28 诊断 → F-29 审计 → F-30 备份 → F-24 版本历史 → F-23 对比
→ F-26 订阅 → F-25 飞书 → F-32 监控 → F-31 多实例 → F-27 MCP
```

理由：运维功能先做（对后续有帮助），协作功能中间做，MCP 最后做（最复杂）。

---

## 4. 技术决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 审计存储 | JSONL 追加写入 | 不需要读取全部再写入，性能好 |
| 备份存储 | 文件系统 copies/ | 简单可靠，不需要数据库 |
| 版本存储 | versions/{id}.json | 每条记忆独立文件，易于管理 |
| MCP 协议 | JSON-RPC over HTTP | 不实现 stdio，HTTP 最简单 |
| 多实例代理 | httpx 代理请求 | 配置驱动，不做动态注册 |
| 性能指标 | 内存环形缓冲区（1000 条） | 不持久化，重启清零 |

---

## 5. 验收检查清单

- [ ] F-28：诊断报告包含三项检测结果
- [ ] F-29：所有增删改操作有审计记录
- [ ] F-30：可创建/查看/恢复备份
- [ ] F-24：编辑后自动保存版本，可回滚
- [ ] F-23：双栏对比两个 profile 记忆
- [ ] F-26：可注册/注销 webhook 订阅
- [ ] F-25：一键发送摘要到飞书
- [ ] F-32：API 响应时间图表可用
- [ ] F-31：多实例列表可查看
- [ ] F-27：JSON-RPC 调用返回正确结果
- [ ] 全部回归测试通过
- [ ] 前端构建通过
