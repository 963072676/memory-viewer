# Memory Viewer v2 — P3 迭代计划

> **版本**: 1.0
> **日期**: 2026-05-29
> **作者**: pm-orchestrator
> **基于**: PM_SPEC.md v2.2 + P2 迭代完成状态

---

## 0. 迭代概述

P3 迭代聚焦**智能化方向**（记忆关联图谱、智能推荐、自动去重）和**数据质量**（健康度评分、衰减曲线可视化），为记忆库从"被动浏览"转向"主动发现"奠定基础。

**目标**：建立记忆之间的关联网络，提供智能推荐和数据质量监控，减少冗余。

**预计工期**：8-10 个工作日（单人全栈）

**当前状态**：P0+P1+P2 已全部上线（19/33 功能），后端测试 59/59 通过，服务运行在 192.168.5.55:8501。

---

## 1. 当前状态评估

### 已完成（P0+P1+P2）
| 项目 | 状态 | 说明 |
|------|------|------|
| P0 全部 9 项功能 | ✅ 已完成 | 排序、展开折叠、Swagger、高亮、快捷键、创建、导入、导出 |
| P1 全部 5 项功能 | ✅ 已完成 | 高级搜索、编辑、删除、统计仪表盘、缓存自动刷新 |
| P2 全部 6 项功能 | ✅ 已完成 | 版本更新说明、暗色模式、时间线视图、记忆归档、虚拟列表、记忆变更通知 |
| 后端测试 | ✅ 59/59 通过 | 覆盖全部 P0+P1+P2 后端 API |
| 服务运行 | ✅ 192.168.5.55:8501 | 正常提供服务 |

### 未完成（P3）
| 项目 | 说明 |
|------|------|
| F-18 记忆关联图谱 | 前后端均未开始 |
| F-19 智能推荐 | 前后端均未开始 |
| F-20 记忆健康度评分 | 前后端均未开始 |
| F-21 自动去重 | 前后端均未开始 |
| F-22 记忆衰减曲线 | 前后端均未开始 |

### 现有数据模型关键字段（P3 设计基础）
```python
# backend/app/models/agentmemory.py
class AgentMemoryItem(BaseModel):
    id: str
    type: str = "pattern"
    title: str
    content: str
    concepts: list[str] = Field(default_factory=list)  # ← P3 核心：concepts 共现分析
    strength: int = 5                                    # ← P3 核心：健康度 + 衰减
    createdAt: Optional[str] = None                      # ← P3 核心：age 计算
    archived: bool = False
```

---

## 2. 功能任务拆分

### 2.1 F-18 记忆关联图谱

**描述**：基于 concepts 共现关系构建知识图谱，可视化记忆之间的关联。节点=记忆条目，边=concepts 交集（边权重=共享 concepts 数量）。

**技术方案**：
- 后端构建图数据结构：遍历所有记忆的 concepts 集合，计算两两交集（O(n²) 但 n 通常 <1000，可接受）
- 仅保留 weight ≥ 1 的边（至少共享 1 个 concept）
- 前端优先使用 `vue-force-graph`（基于 `force-graph` 轻量库，~50KB），备选 SVG 自绘
- 不引入 D3 全量（~250KB），仅用 force-directed 布局

**API 设计**：
```
GET /api/agentmemory/graph
Response: {
  nodes: [{id, label, type, strength, size}],
  edges: [{source, target, weight, shared_concepts: [string]}],
  meta: {node_count, edge_count, max_weight}
}
```

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F18-T1 | 创建 `services/graph.py`：图数据构建逻辑（concepts 交集计算、边权重计算） | 后端 | `services/graph.py` | 3h |
| F18-T2 | 创建 `models/graph.py`：GraphResponse、GraphNode、GraphEdge Pydantic 模型 | 后端 | `models/graph.py` | 1h |
| F18-T3 | 新增 `routers/graph.py`：`GET /api/agentmemory/graph` 端点 | 后端 | `routers/graph.py` | 1h |
| F18-T4 | 注册 graph router 到 `main.py` | 后端 | `app/main.py` | 0.25h |
| F18-T5 | 安装 `vue-force-graph` 或 `force-graph` 前端依赖 | 前端 | `package.json` | 0.25h |
| F18-T6 | 创建 `GraphView.vue`：图谱可视化页面，集成 force-graph | 前端 | `views/GraphView.vue` | 4h |
| F18-T7 | 实现交互：点击节点高亮关联边、缩放拖拽、节点 tooltip 显示详情 | 前端 | `views/GraphView.vue` | 2h |
| F18-T8 | Vue Router 新增 `/graph` 路由 + AppSidebar 导航入口 | 前端 | `router/index.ts`, `AppSidebar.vue` | 0.5h |
| F18-T9 | API client 封装 `getGraph()` | 前端 | `api/agentmemory.ts` | 0.5h |
| F18-T10 | 测试：graph API 单测 | 测试 | `tests/test_graph.py` | 2h |

**验收标准 (AC)**：
- **AC-F18-1**：`GET /api/agentmemory/graph` 返回有效图数据（nodes + edges）
- **AC-F18-2**：每条边的 weight 等于两端记忆共享的 concepts 数量
- **AC-F18-3**：仅共享 ≥1 个 concept 的记忆对之间有边
- **AC-F18-4**：前端 `/graph` 页面正确渲染力导向图，节点可拖拽
- **AC-F18-5**：点击节点时高亮关联边和邻接节点，tooltip 显示记忆标题
- **AC-F18-6**：空数据（无记忆）时显示友好提示
- **AC-F18-7**：100 条记忆时图谱渲染 < 3 秒

---

### 2.2 F-19 智能推荐

**描述**：根据当前查看的记忆，推荐相关条目。算法基于 concepts 集合 Jaccard 相似度 + strength 加权。

**技术方案**：
- Jaccard 相似度 = |A ∩ B| / |A ∪ B|，A、B 为两条记忆的 concepts 集合
- 加权公式：`score = jaccard * 0.7 + (strength / 10) * 0.3`
- 过滤条件：排除自身、排除已归档记忆、排除 concepts 为空的记忆
- 排序：按 score 降序，取 top N
- 复杂度：O(n) 遍历（与当前记忆比较），整体 O(n²) 内

**API 设计**：
```
GET /api/agentmemory/{id}/recommendations?limit=5
Response: {
  memory_id: string,
  recommendations: [
    {memory: AgentMemoryItem, score: float, shared_concepts: [string]}
  ]
}
```

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F19-T1 | 创建 `services/recommendation.py`：Jaccard 相似度计算 + strength 加权 + top-N 排序 | 后端 | `services/recommendation.py` | 2.5h |
| F19-T2 | 新增 `routers/recommendation.py`：`GET /api/agentmemory/{id}/recommendations` 端点 | 后端 | `routers/recommendation.py` | 1h |
| F19-T3 | 注册 recommendation router 到 `main.py` | 后端 | `app/main.py` | 0.25h |
| F19-T4 | 创建 `RelatedMemories.vue` 组件：显示"相关记忆"列表，每项展示 title + score + 共享 concepts | 前端 | `components/Layout/RelatedMemories.vue` | 2h |
| F19-T5 | 在 MemoryCard 展开时（MemoryDetail.vue）集成 RelatedMemories 组件 | 前端 | `components/Layout/MemoryDetail.vue` | 1h |
| F19-T6 | API client 封装 `getRecommendations(id, limit)` | 前端 | `api/agentmemory.ts` | 0.5h |
| F19-T7 | 测试：recommendation API 单测 | 测试 | `tests/test_recommendation.py` | 2h |

**验收标准 (AC)**：
- **AC-F19-1**：`GET /api/agentmemory/{id}/recommendations` 返回推荐列表
- **AC-F19-2**：推荐结果按 score 降序排列
- **AC-F19-3**：推荐结果不包含自身、不包含已归档记忆
- **AC-F19-4**：当目标记忆 concepts 为空时，返回空推荐列表（不报错）
- **AC-F19-5**：MemoryCard 展开时显示"相关记忆"列表，点击可跳转
- **AC-F19-6**：无推荐时显示"暂无相关记忆"
- **AC-F19-7**：`?limit=N` 参数正确控制返回数量

---

### 2.3 F-20 记忆健康度评分

**描述**：综合 strength、age、concepts 丰富度、是否被推荐过等因素，计算 0-100 的健康度评分。

**技术方案**：
- 评分公式（各维度归一化到 0-100）：
  - strength 分（40%）：`strength / 10 * 100`
  - age 分（30%）：`max(0, 100 - days_since_created / 30 * 100)`（30 天内满分，线性衰减到 0）
  - concepts 丰富度分（15%）：`min(len(concepts) / 5, 1) * 100`（5 个 concepts 满分）
  - 推荐引用分（15%）：`min(recommendation_count / 3, 1) * 100`（被推荐 3 次满分）
  - 总分 = 各维度加权和
- 颜色标记：绿(>70)、黄(40-70)、红(<40)

**API 设计**：
```
GET /api/agentmemory/{id}/health
Response: {
  memory_id: string,
  health_score: int,          # 0-100
  color: "green" | "yellow" | "red",
  breakdown: {
    strength_score: int,      # 0-100 (weight 40%)
    age_score: int,           # 0-100 (weight 30%)
    concepts_score: int,      # 0-100 (weight 15%)
    recommendation_score: int # 0-100 (weight 15%)
  },
  days_since_created: int,
  days_until_strength_zero: Optional[int]  # 与 F-22 衰减曲线联动
}
```

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F20-T1 | 创建 `services/health.py`：健康度评分算法（四维度加权） | 后端 | `services/health.py` | 2h |
| F20-T2 | 新增 `routers/health.py`：`GET /api/agentmemory/{id}/health` 端点；扩展列表接口附加 `health_score` | 后端 | `routers/health.py` | 1.5h |
| F20-T3 | 注册 health router 到 `main.py` | 后端 | `app/main.py` | 0.25h |
| F20-T4 | 创建 `HealthBadge.vue` 组件：健康度徽章（圆形进度 + 颜色） | 前端 | `components/Layout/HealthBadge.vue` | 2h |
| F20-T5 | 在 MemoryCard.vue 中集成 HealthBadge，列表模式下显示 | 前端 | `components/Layout/MemoryCard.vue` | 1h |
| F20-T6 | API client 封装 `getHealth(id)` | 前端 | `api/agentmemory.ts` | 0.5h |
| F20-T7 | 测试：health API 单测（含评分边界） | 测试 | `tests/test_health.py` | 2h |

**验收标准 (AC)**：
- **AC-F20-1**：`GET /api/agentmemory/{id}/health` 返回 0-100 的评分
- **AC-F20-2**：评分 breakdown 包含四个维度，权重之和为 100%
- **AC-F20-3**：strength=10、created 今天、concepts 5 个 → 评分 >90
- **AC-F20-4**：strength=1、created 60 天前、concepts 空 → 评分 <20
- **AC-F20-5**：颜色标记正确：绿(>70)、黄(40-70)、红(<40)
- **AC-F20-6**：MemoryCard 显示健康度徽章，颜色与评分一致
- **AC-F20-7**：列表接口可选附加 health_score（`?include_health=true`）

---

### 2.4 F-21 自动去重

**描述**：检测语义相似的记忆条目，提示用户合并。纯本地算法，不依赖外部 embedding API。

**技术方案**：
- Jaccard 相似度（concepts）：`|A ∩ B| / |A ∪ B|`，阈值 > 0.6
- 标题相似度（Levenshtein）：`1 - edit_distance(a, b) / max(len(a), len(b))`，阈值 > 0.7
- 综合相似度：`concepts_jaccard * 0.6 + title_similarity * 0.4`
- 仅当综合相似度 > threshold 时判定为重复
- 复杂度：O(n²) 遍历（n < 1000 可接受，>1000 时可引入倒排索引优化）
- 一键合并：保留 strength 较高的记忆，合并 concepts（去重），更新 content

**API 设计**：
```
GET /api/agentmemory/duplicates?threshold=0.7
Response: {
  pairs: [
    {
      memory_a: AgentMemoryItem,
      memory_b: AgentMemoryItem,
      similarity: float,
      concepts_similarity: float,
      title_similarity: float,
      shared_concepts: [string]
    }
  ],
  total_pairs: int
}

POST /api/agentmemory/merge
Request: {keep_id: string, merge_id: string}
Response: {success: bool, merged_memory: AgentMemoryItem}
```

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F21-T1 | 创建 `services/dedup.py`：Jaccard 相似度 + Levenshtein 编辑距离 + 综合相似度计算 | 后端 | `services/dedup.py` | 3h |
| F21-T2 | 新增 `routers/dedup.py`：`GET /api/agentmemory/duplicates` + `POST /api/agentmemory/merge` 端点 | 后端 | `routers/dedup.py` | 2h |
| F21-T3 | 注册 dedup router 到 `main.py` | 后端 | `app/main.py` | 0.25h |
| F21-T4 | 创建 `DuplicatePanel.vue`：重复记忆提示面板，展示重复对 + 相似度 + 共享 concepts | 前端 | `components/Layout/DuplicatePanel.vue` | 3h |
| F21-T5 | 实现一键合并交互：选择保留哪条 → 调用 merge API → 刷新列表 | 前端 | `components/Layout/DuplicatePanel.vue` | 2h |
| F21-T6 | 在侧边栏或工具栏添加"去重检查"入口 | 前端 | `AppSidebar.vue` 或 `HomeView.vue` | 0.5h |
| F21-T7 | API client 封装 `getDuplicates(threshold)` + `mergeMemories(keepId, mergeId)` | 前端 | `api/agentmemory.ts` | 0.5h |
| F21-T8 | 测试：dedup API + merge API 单测 | 测试 | `tests/test_dedup.py` | 2.5h |

**验收标准 (AC)**：
- **AC-F21-1**：`GET /api/agentmemory/duplicates` 返回重复记忆对列表
- **AC-F21-2**：每对包含 similarity、concepts_similarity、title_similarity
- **AC-F21-3**：`?threshold=0.7` 正确过滤低于阈值的对
- **AC-F21-4**：不依赖外部 embedding API，纯本地计算
- **AC-F21-5**：`POST /api/agentmemory/merge` 合并后保留 strength 较高的记忆
- **AC-F21-6**：合并后 concepts 去重合并，content 更新
- **AC-F21-7**：前端 DuplicatePanel 显示重复对，支持一键合并
- **AC-F21-8**：合并后被合并的记忆从列表中移除

---

### 2.5 F-22 记忆衰减曲线

**描述**：可视化 strength 随时间的衰减趋势，预测记忆何时"遗忘"。

**技术方案**：
- 线性衰减模型：`strength(t) = initial_strength - decay_rate * days`
- decay_rate 默认值：`strength / 90`（假设 90 天衰减到 0）
- 可在记忆详情中查看衰减曲线（小型折线图，可使用 Chart.js 轻量版或 SVG 自绘）
- 预测：N 天后 strength 降至 0 的日期

**API 设计**：
```
GET /api/agentmemory/{id}/decay
Response: {
  memory_id: string,
  current_strength: int,
  initial_strength: int,
  decay_rate: float,           # 每天衰减量
  days_since_created: int,
  predicted_zero_date: string, # ISO date，strength 降至 0 的预测日期
  decay_curve: [               # 折线图数据点
    {day: int, strength: float}
  ]
}
```

| # | 任务 | 层 | 文件（预估） | 工作量 |
|---|------|-----|-------------|--------|
| F22-T1 | 创建 `services/decay.py`：线性衰减模型计算 + 预测逻辑 | 后端 | `services/decay.py` | 1.5h |
| F22-T2 | 新增 `routers/decay.py`：`GET /api/agentmemory/{id}/decay` 端点 | 后端 | `routers/decay.py` | 1h |
| F22-T3 | 注册 decay router 到 `main.py` | 后端 | `app/main.py` | 0.25h |
| F22-T4 | 创建 `DecayChart.vue`：小型折线图组件（SVG 自绘或 Chart.js lite） | 前端 | `components/Layout/DecayChart.vue` | 3h |
| F22-T5 | 在 MemoryDetail.vue 中集成 DecayChart，展示衰减曲线 | 前端 | `components/Layout/MemoryDetail.vue` | 1h |
| F22-T6 | API client 封装 `getDecay(id)` | 前端 | `api/agentmemory.ts` | 0.5h |
| F22-T7 | 测试：decay API 单测 | 测试 | `tests/test_decay.py` | 1.5h |

**验收标准 (AC)**：
- **AC-F22-1**：`GET /api/agentmemory/{id}/decay` 返回衰减数据
- **AC-F22-2**：decay_curve 数据点数量合理（按天生成，最多 365 个点）
- **AC-F22-3**：predicted_zero_date 计算正确（当前 strength / decay_rate 天后）
- **AC-F22-4**：前端 MemoryDetail 显示衰减曲线折线图
- **AC-F22-5**：折线图显示当前 strength 位置（标记点）
- **AC-F22-6**：strength=10、创建于今天 → predicted_zero_date ≈ 90 天后
- **AC-F22-7**：strength=0 时显示"记忆已遗忘"提示

---

## 3. 任务依赖关系

```
F-20 健康度评分 ──────────┐
F-22 衰减曲线 ────────────┤
                          │
F-19 智能推荐 ────────────┼── 可并行开发（后端互不依赖）
                          │
F-21 自动去重 ────────────┤
F-18 关联图谱 ────────────┘

内部依赖：
F18-T6~T9 (前端图谱) 依赖 F18-T1~T4 (后端 graph API 先完成)
F19-T4~T6 (前端推荐) 依赖 F19-T1~T3 (后端 recommendation API 先完成)
F20-T4~T6 (前端健康度) 依赖 F20-T1~T3 (后端 health API 先完成)
F21-T4~T7 (前端去重) 依赖 F21-T1~T3 (后端 dedup API 先完成)
F22-T4~T6 (前端衰减) 依赖 F22-T1~T3 (后端 decay API 先完成)

跨功能依赖：
F-20 健康度评分的 recommendation_score 维度依赖 F-19 推荐逻辑
F-20 健康度 API 中 days_until_strength_zero 联动 F-22 衰减曲线
F-18 图谱中可复用 F-19 的 concepts 相似度计算
```

**推荐开发顺序**（单人串行，从简到繁，降低集成风险）：

```
Phase 1 (Day 1-2): F-22 记忆衰减曲线
  理由：最简单的功能，纯数学计算 + 简单折线图，快速产出可见成果
  产出：decay service + API + DecayChart 组件

Phase 2 (Day 2-3): F-20 记忆健康度评分
  理由：依赖 Phase 1 的衰减数据（days_until_strength_zero），中等复杂度
  产出：health service + API + HealthBadge 组件

Phase 3 (Day 4-5): F-19 智能推荐
  理由：核心算法（Jaccard），为 F-18 和 F-21 提供算法基础
  产出：recommendation service + API + RelatedMemories 组件

Phase 4 (Day 5-6): F-21 自动去重
  理由：复用 Phase 3 的 Jaccard 算法 + 新增 Levenshtein，中高复杂度
  产出：dedup service + API + DuplicatePanel 组件

Phase 5 (Day 7-9): F-18 记忆关联图谱
  理由：最复杂功能（图数据结构 + 第三方可视化库），放最后避免阻塞
  产出：graph service + API + GraphView 页面
```

---

## 4. 工作量汇总

| 功能 | 后端 | 前端 | 测试 | 合计 | 复杂度 |
|------|------|------|------|------|--------|
| F-18 记忆关联图谱 | 5.25h | 6.75h | 2h | **14h** | 🟠 高 |
| F-19 智能推荐 | 3.75h | 3.5h | 2h | **9.25h** | 🟠 高 |
| F-20 记忆健康度评分 | 3.75h | 3.5h | 2h | **9.25h** | 🟡 中 |
| F-21 自动去重 | 5.25h | 6h | 2.5h | **13.75h** | 🟠 高 |
| F-22 记忆衰减曲线 | 2.75h | 4.5h | 1.5h | **8.75h** | 🟡 中 |
| **合计** | **20.75h** | **24.25h** | **10h** | **55h** | — |

> 约 **7-8 个工作日**（按 8h/天计算）

---

## 5. 风险评估

| # | 风险 | 影响 | 概率 | 缓解措施 |
|---|------|------|------|---------|
| R1 | **vue-force-graph 兼容性** | 图谱可视化库与 Vue 3 组合式 API 集成问题 | 🟡 中 | 备选方案：SVG 自绘（<100 条时力导向布局可简化为圆环布局） |
| R2 | **Levenshtein 性能** | O(n²) 对比较慢（n=1000 时 50 万次比较） | 🟢 低 | 标题通常 <50 字符，单次比较 O(1)；可预计算 concepts 倒排索引过滤 |
| R3 | **健康度评分主观性** | 权重和阈值可能不符合用户预期 | 🟡 中 | 权重设计为可配置（API 参数），首批上线后根据反馈调整 |
| R4 | **图谱大数据量渲染** | >500 节点时前端 canvas 渲染卡顿 | 🟡 中 | 限制最大显示节点数（如 top 100 条，按 strength 排序）；添加节点过滤 |
| R5 | **合并操作数据丢失** | 一键合并时误操作导致记忆丢失 | 🟡 中 | 合并前二次确认弹窗；合并时保留被合并记忆的 audit log |
| R6 | **衰减模型过于简化** | 线性衰减不符合实际记忆遗忘曲线 | 🟢 低 | 首版用线性模型，后续可升级为 Ebbinghaus 遗忘曲线（指数衰减） |

---

## 6. 技术决策记录

| 决策 | 选项 | 选择 | 理由 |
|------|------|------|------|
| 图谱可视化库 | vue-force-graph / D3 全量 / SVG 自绘 | **vue-force-graph（优先）** | 轻量（~50KB）；支持力导向布局；交互内置（拖拽/缩放）；备选 SVG 自绘兜底 |
| 去重算法 | embedding + cosine / Jaccard + Levenshtein / LLM | **Jaccard + Levenshtein** | 纯本地计算；不依赖外部 API；O(n²) 可接受；精度足够（concepts + title 双维度） |
| 健康度权重 | 固定 / 可配置 | **固定权重 + 预留配置接口** | 首版固定（strength 40%、age 30%、concepts 15%、recommendation 15%），后续可通过 API 参数调整 |
| 衰减模型 | 线性 / 指数(Ebbinghaus) / 自定义 | **线性** | 实现简单；预测直观；后续可升级为指数模型 |
| 折线图方案 | Chart.js / echarts / SVG 自绘 | **SVG 自绘** | 轻量；仅需简单折线图；避免引入大型图表库 |
| 推荐算法 | Jaccard / cosine / TF-IDF | **Jaccard** | 与 concepts 集合天然匹配；计算简单；已有 F-21 去重复用 |

---

## 7. 验收检查清单（Sprint Review 用）

- [ ] F-18：`GET /api/agentmemory/graph` 返回有效图数据
- [ ] F-18：图谱页面正确渲染力导向图，节点可拖拽
- [ ] F-18：点击节点高亮关联边和邻接节点
- [ ] F-19：`GET /api/agentmemory/{id}/recommendations` 返回推荐列表
- [ ] F-19：推荐结果按 score 降序，不包含自身
- [ ] F-19：MemoryCard 展开时显示"相关记忆"列表
- [ ] F-20：`GET /api/agentmemory/{id}/health` 返回 0-100 评分
- [ ] F-20：评分 breakdown 包含四维度
- [ ] F-20：MemoryCard 显示健康度徽章，颜色正确
- [ ] F-21：`GET /api/agentmemory/duplicates` 返回重复记忆对
- [ ] F-21：`POST /api/agentmemory/merge` 合并正确
- [ ] F-21：前端 DuplicatePanel 显示重复对，支持一键合并
- [ ] F-22：`GET /api/agentmemory/{id}/decay` 返回衰减数据
- [ ] F-22：前端 MemoryDetail 显示衰减曲线折线图
- [ ] F-22：predicted_zero_date 计算正确
- [ ] 所有新增 API 端点出现在 `/api/docs` Swagger 文档中
- [ ] 前端构建无 TypeScript 错误（`npm run build` 成功）
- [ ] 后端测试全部通过（`pytest` 成功）
