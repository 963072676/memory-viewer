# Memory Viewer P4+P5 测试计划

---

## F-28 记忆系统诊断

| # | 用例 | 优先级 | 类型 |
|---|------|--------|------|
| F28-01 | GET /api/diagnostics 返回 200 | P0 | 后端 |
| F28-02 | 返回 duplicates/orphaned_concepts/strength_anomalies 三个字段 | P0 | 后端 |
| F28-03 | 空数据时返回空数组（非 null） | P1 | 后端 |
| F28-04 | 检测到重复时 pairs 非空 | P1 | 后端 |
| F28-05 | strength<1 的记忆被标记为异常 | P1 | 后端 |
| F28-06 | 诊断页面渲染正常 | P0 | 前端 |

## F-29 操作审计日志

| # | 用例 | 优先级 | 类型 |
|---|------|--------|------|
| F29-01 | 创建记忆后 GET /api/audit 返回 create 记录 | P0 | 后端 |
| F29-02 | 编辑记忆后 audit 包含 update 记录 | P0 | 后端 |
| F29-03 | 删除记忆后 audit 包含 delete 记录 | P0 | 后端 |
| F29-04 | 按 action 筛选返回正确结果 | P1 | 后端 |
| F29-05 | 按时间范围筛选 | P1 | 后端 |
| F29-06 | audit 记录包含 timestamp/method/path/status | P1 | 后端 |
| F29-07 | 审计日志页面渲染正常 | P0 | 前端 |

## F-30 备份与恢复

| # | 用例 | 优先级 | 类型 |
|---|------|--------|------|
| F30-01 | POST /api/backup/create 返回 200 + 备份 ID | P0 | 后端 |
| F30-02 | GET /api/backup/list 返回备份列表 | P0 | 后端 |
| F30-03 | POST /api/backup/restore 恢复数据 | P0 | 后端 |
| F30-04 | 恢复后数据与备份一致 | P0 | 后端 |
| F30-05 | 备份文件存在于 backups/ 目录 | P1 | 后端 |
| F30-06 | 备份管理页面渲染正常 | P0 | 前端 |

## F-24 记忆版本历史

| # | 用例 | 优先级 | 类型 |
|---|------|--------|------|
| F24-01 | 编辑记忆后 GET /api/agentmemory/{id}/versions 返回版本列表 | P0 | 后端 |
| F24-02 | 版本包含 version/content/timestamp | P0 | 后端 |
| F24-03 | POST rollback 恢复到指定版本 | P0 | 后端 |
| F24-04 | 回滚后当前内容与目标版本一致 | P0 | 后端 |
| F24-05 | 无编辑历史时返回空列表 | P1 | 后端 |
| F24-06 | 版本历史 UI 渲染正常 | P0 | 前端 |

## F-23 多 Agent 记忆对比

| # | 用例 | 优先级 | 类型 |
|---|------|--------|------|
| F23-01 | GET /api/memory/compare?profile_a=X&profile_b=Y 返回 200 | P0 | 后端 |
| F23-02 | 返回两个 profile 的记忆列表 | P0 | 后端 |
| F23-03 | 标记 only_in_a/only_in_b/modified 差异 | P1 | 后端 |
| F23-04 | 相同 profile 对比返回空差异 | P1 | 后端 |
| F23-05 | 双栏对比页面渲染正常 | P0 | 前端 |

## F-26 API Webhook 订阅

| # | 用例 | 优先级 | 类型 |
|---|------|--------|------|
| F26-01 | POST /api/webhook/subscriptions 创建订阅 | P0 | 后端 |
| F26-02 | GET /api/webhook/subscriptions 返回列表 | P0 | 后端 |
| F26-03 | DELETE /api/webhook/subscriptions/{id} 删除订阅 | P0 | 后端 |
| F26-04 | 记忆变更时推送到已注册的 webhook | P0 | 后端 |
| F26-05 | 无效 URL 时不崩溃 | P1 | 后端 |
| F26-06 | 订阅管理 UI 渲染正常 | P0 | 前端 |

## F-25 飞书集成

| # | 用例 | 优先级 | 类型 |
|---|------|--------|------|
| F25-01 | POST /api/memory/summary/send-to-feishu 返回 200 | P0 | 后端 |
| F25-02 | 摘要包含记忆数量、类型分布 | P1 | 后端 |
| F25-03 | 前端发送按钮可用 | P0 | 前端 |

## F-32 性能监控

| # | 用例 | 优先级 | 类型 |
|---|------|--------|------|
| F32-01 | GET /api/metrics 返回 200 | P0 | 后端 |
| F32-02 | 包含 avg/p50/p95/p99 延迟 | P0 | 后端 |
| F32-03 | 包含请求计数 | P1 | 后端 |
| F32-04 | 性能图表页面渲染正常 | P0 | 前端 |

## F-31 多实例管理

| # | 用例 | 优先级 | 类型 |
|---|------|--------|------|
| F31-01 | GET /api/instances 返回实例列表 | P0 | 后端 |
| F31-02 | 实例包含 name/url/status | P1 | 后端 |
| F31-03 | 实例列表页面渲染正常 | P0 | 前端 |

## F-27 MCP Server

| # | 用例 | 优先级 | 类型 |
|---|------|--------|------|
| F27-01 | POST /mcp/jsonrpc 调用 memory.list 返回列表 | P0 | 后端 |
| F27-02 | memory.get 返回单条记忆 | P0 | 后端 |
| F27-03 | memory.search 返回搜索结果 | P0 | 后端 |
| F27-04 | memory.create 创建记忆 | P0 | 后端 |
| F27-05 | 无效方法返回 error | P1 | 后端 |
| F27-06 | 无效 JSON 返回 parse error | P1 | 后端 |

---

## 汇总

| 优先级 | 后端 | 前端 | 总计 |
|--------|------|------|------|
| P0 | 28 | 10 | 38 |
| P1 | 15 | 0 | 15 |
| 总计 | 43 | 10 | 53 |

加上回归测试 92 条，总计预计 145 条。
