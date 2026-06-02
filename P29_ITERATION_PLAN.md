# P29 迭代计划

> **日期**: 2026-05-31  
> **阶段**: P29  
> **目标**: PM规划新功能阶段

---

## 状态

P28 (F-67 Export & Reporting) 已完成。
backlog 为空，需要 PM 规划新功能。

根据 PM_SPEC.md，以下功能尚未实现：

| 功能ID | 功能名称 | 优先级 | 复杂度 |
|--------|----------|--------|--------|
| F-21 | 自动去重 (语义相似检测) | P2 | 🟠 高 |
| F-23 | 多 Agent 记忆对比 | P4 | 🟡 中 |
| F-24 | 记忆版本历史 | P4 | 🟠 高 |
| F-27 | MCP Server 模式 | P4 | 🟠 高 |
| F-32 | 性能监控 | P5 | 🟡 中 |

## P29 规划

选择 **F-32 性能监控** 作为 P29 目标：
- 独立功能，不依赖其他未完成功能
- 可观测性对运维有价值
- 后端 + 前端各约 200 行代码
- 复杂度中等

### F-32 性能监控 功能描述

**问题**: 没有可观测性，API 响应时间、缓存命中率等指标不可见。

**解决方案**:
- 后端：新增 `/api/metrics` 端点，返回内存读写延迟、缓存命中率、API QPS
- 前端：新增 MetricsView.vue，图表展示实时指标
- 使用 Python 内置 `time.time()` 测量延迟，无外部依赖

### 实现任务

1. **P29-T1**: 后端 metrics 端点
   - 新增 `backend/app/services/metrics_service.py`
   - 端点: `/api/metrics` (GET)
   - 指标: avg_read_latency_ms, cache_hit_rate, api_qps, memory_count

2. **P29-T2**: 前端 MetricsView.vue
   - 仪表盘布局，3个指标卡片
   - 每10秒自动刷新
   - 图表: 延迟趋势折线图

3. **P29-T3**: 验证
   - pytest + vue-tsc 无错误

## 验收标准

- AC-F32-1: `/api/metrics` 返回 JSON 格式指标
- AC-F32-2: 前端显示 3 个指标卡片
- AC-F32-3: 页面自动每 10s 刷新数据
- AC-F32-4: pytest 无新增失败
- AC-F32-5: vue-tsc 无错误