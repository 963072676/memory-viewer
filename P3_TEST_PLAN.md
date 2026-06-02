# Memory Viewer v2 — P3 测试计划

> **版本**: 1.0
> **日期**: 2026-05-29
> **基于**: P3_ITERATION_PLAN.md
> **现有测试**: 59 个用例（P0+P1+P2），全部通过

---

## 目录

1. [F-18 记忆关联图谱](#f-18-记忆关联图谱)
2. [F-19 智能推荐](#f-19-智能推荐)
3. [F-20 记忆健康度评分](#f-20-记忆健康度评分)
4. [F-21 自动去重](#f-21-自动去重)
5. [F-22 记忆衰减曲线](#f-22-记忆衰减曲线)
6. [测试汇总](#测试汇总)

---

## F-18 记忆关联图谱

### 后端 API 测试（pytest）

新增文件：`backend/tests/test_graph.py`

```python
# === GET /api/agentmemory/graph ===

def test_graph_returns_200(client):
    """GET /api/agentmemory/graph 返回 200"""
    ...

def test_graph_returns_nodes_and_edges(client):
    """响应包含 nodes 和 edges 数组"""
    ...

def test_graph_nodes_have_required_fields(client):
    """每个 node 包含 id, label, type, strength, size 字段"""
    ...

def test_graph_edges_have_required_fields(client):
    """每个 edge 包含 source, target, weight, shared_concepts 字段"""
    ...

def test_graph_edge_weight_equals_shared_concepts_count(client):
    """边的 weight 等于两端记忆共享的 concepts 数量"""
    ...

def test_graph_only_edges_with_shared_concepts(client):
    """仅当两条记忆共享 >= 1 个 concept 时才有边"""
    ...

def test_graph_no_self_loops(client):
    """图中不存在自环（source != target）"""
    ...

def test_graph_meta_fields(client):
    """响应包含 meta 字段：node_count, edge_count, max_weight"""
    ...

def test_graph_empty_memories(client):
    """无记忆时返回空 nodes 和 edges"""
    ...

def test_graph_excludes_archived_memories(client):
    """图谱默认不包含已归档记忆"""
    ...

def test_graph_size_based_on_strength(client):
    """节点 size 与 strength 正相关"""
    ...
```

### 前端测试（描述性）

| # | 用例 | 优先级 | 步骤 | 预期 |
|---|------|--------|------|------|
| FE-18-1 | **图谱页面渲染** | **P0** | 访问 /graph | 力导向图正确渲染，显示节点和边 |
| FE-18-2 | **节点拖拽** | **P0** | 拖拽图谱中的节点 | 节点跟随鼠标移动，边实时更新 |
| FE-18-3 | **点击高亮** | **P0** | 点击某个节点 | 关联边高亮，邻接节点高亮，tooltip 显示记忆标题 |
| FE-18-4 | **缩放交互** | P1 | 滚轮缩放图谱 | 图谱平滑缩放，不丢失细节 |
| FE-18-5 | **空数据状态** | P1 | 无记忆时访问 /graph | 显示"暂无记忆数据"友好提示 |
| FE-18-6 | **大数据量渲染** | P1 | 100 条记忆时访问 | 图谱渲染 < 3 秒，交互流畅 |
| FE-18-7 | **导航入口** | P1 | 从侧边栏进入 | /graph 路由可访问 |
| FE-18-8 | **节点大小区分** | P2 | 观察不同 strength 的节点 | strength 越大节点越大 |
| FE-18-9 | **边权重可视化** | P2 | 观察边的粗细 | weight 越大边越粗 |

### 边界条件

- 仅 1 条记忆 → 只有 1 个节点，无边
- 所有记忆 concepts 为空 → 只有节点，无边
- 两条记忆 concepts 完全相同 → 边权重 = concepts 数量
- 记忆数 > 500 → 限制显示 top N 节点（按 strength 排序）
- 所有记忆已归档 → 空图谱

### 验收检查清单（AC）

- [ ] **AC-F18-1**：API 返回有效图数据（nodes + edges） ⭐ P0
- [ ] **AC-F18-2**：边 weight = 共享 concepts 数量 ⭐ P0
- [ ] **AC-F18-3**：仅共享 ≥1 个 concept 的记忆对有边
- [ ] **AC-F18-4**：前端力导向图正确渲染 ⭐ P0
- [ ] **AC-F18-5**：节点可拖拽 ⭐ P0
- [ ] **AC-F18-6**：点击节点高亮关联边
- [ ] **AC-F18-7**：空数据友好提示

---

## F-19 智能推荐

### 后端 API 测试（pytest）

新增文件：`backend/tests/test_recommendation.py`

```python
# === GET /api/agentmemory/{id}/recommendations ===

def test_recommendations_returns_200(client, sample_memory_id):
    """GET /api/agentmemory/{id}/recommendations 返回 200"""
    ...

def test_recommendations_returns_list(client, sample_memory_id):
    """响应为推荐列表，每项包含 memory, score, shared_concepts"""
    ...

def test_recommendations_ordered_by_score_desc(client, sample_memory_id):
    """推荐结果按 score 降序排列"""
    ...

def test_recommendations_excludes_self(client, sample_memory_id):
    """推荐结果不包含自身"""
    ...

def test_recommendations_excludes_archived(client, sample_memory_id):
    """推荐结果不包含已归档记忆"""
    ...

def test_recommendations_limit_param(client, sample_memory_id):
    """?limit=3 只返回 3 条推荐"""
    ...

def test_recommendations_empty_concepts(client):
    """当目标记忆 concepts 为空时返回空推荐列表"""
    ...

def test_recommendations_nonexistent_id(client):
    """不存在的 ID 返回 404"""
    ...

def test_recommendations_score_range(client, sample_memory_id):
    """score 值在 0.0 ~ 1.0 范围内"""
    ...

def test_recommendations_shared_concepts_correct(client, sample_memory_id):
    """shared_concepts 为两条记忆 concepts 的交集"""
    ...
```

### 前端测试（描述性）

| # | 用例 | 优先级 | 步骤 | 预期 |
|---|------|--------|------|------|
| FE-19-1 | **相关记忆显示** | **P0** | 展开有共同 concepts 的记忆卡片 | MemoryDetail 显示"相关记忆"列表 |
| FE-19-2 | **推荐列表内容** | **P0** | 查看推荐列表 | 每项显示 title + score + 共享 concepts |
| FE-19-3 | **点击跳转** | **P0** | 点击推荐列表中的记忆 | 跳转到该记忆详情 |
| FE-19-4 | **无推荐状态** | P1 | 展开 concepts 为空的记忆 | 显示"暂无相关记忆" |
| FE-19-5 | **推荐加载状态** | P1 | 展开记忆卡片 | 显示 loading 指示器，加载完成后显示推荐 |
| FE-19-6 | **推荐刷新** | P2 | 编辑记忆 concepts 后重新展开 | 推荐列表更新 |

### 边界条件

- 所有记忆 concepts 为空 → 返回空推荐
- 仅 2 条记忆且有共同 concept → 返回 1 条推荐
- 目标记忆已归档 → 返回 404（不推荐已归档记忆的关联）
- limit > 总推荐数 → 返回全部推荐（不报错）
- limit=0 → 返回空列表

### 验收检查清单（AC）

- [ ] **AC-F19-1**：API 返回推荐列表 ⭐ P0
- [ ] **AC-F19-2**：按 score 降序排列 ⭐ P0
- [ ] **AC-F19-3**：不包含自身和已归档记忆
- [ ] **AC-F19-4**：concepts 为空时返回空列表
- [ ] **AC-F19-5**：MemoryCard 展开显示推荐 ⭐ P0
- [ ] **AC-F19-6**：点击可跳转 ⭐ P0
- [ ] **AC-F19-7**：limit 参数正确

---

## F-20 记忆健康度评分

### 后端 API 测试（pytest）

新增文件：`backend/tests/test_health.py`

```python
# === GET /api/agentmemory/{id}/health ===

def test_health_returns_200(client, sample_memory_id):
    """GET /api/agentmemory/{id}/health 返回 200"""
    ...

def test_health_score_range(client, sample_memory_id):
    """health_score 在 0-100 范围内"""
    ...

def test_health_color_green(client):
    """高 strength + 新创建 + 多 concepts → green"""
    ...

def test_health_color_yellow(client):
    """中等 strength + 中等 age → yellow"""
    ...

def test_health_color_red(client):
    """低 strength + 老记忆 + 无 concepts → red"""
    ...

def test_health_breakdown_has_four_dimensions(client, sample_memory_id):
    """breakdown 包含 strength_score, age_score, concepts_score, recommendation_score"""
    ...

def test_health_breakdown_weights_sum(client, sample_memory_id):
    """breakdown 各维度权重之和 = 100%（40+30+15+15）"""
    ...

def test_health_nonexistent_id(client):
    """不存在的 ID 返回 404"""
    ...

def test_health_high_strength_high_score(client):
    """strength=10, created today, concepts=5 → score > 90"""
    ...

def test_health_low_strength_low_score(client):
    """strength=1, created 60 days ago, concepts=[] → score < 20"""
    ...

def test_health_days_since_created(client, sample_memory_id):
    """days_since_created 计算正确"""
    ...

# === GET /api/agentmemory/paginated?include_health=true ===

def test_paginated_with_health_score(client):
    """?include_health=true 时每条记忆附加 health_score"""
    ...

def test_paginated_without_health_score(client):
    """默认不附加 health_score（性能考虑）"""
    ...
```

### 前端测试（描述性）

| # | 用例 | 优先级 | 步骤 | 预期 |
|---|------|--------|------|------|
| FE-20-1 | **健康度徽章显示** | **P0** | 浏览记忆列表 | MemoryCard 显示健康度徽章 |
| FE-20-2 | **绿色徽章** | **P0** | 查看高分记忆 | 徽章为绿色（>70） |
| FE-20-3 | **黄色徽章** | **P0** | 查看中分记忆 | 徽章为黄色（40-70） |
| FE-20-4 | **红色徽章** | **P0** | 查看低分记忆 | 徽章为红色（<40） |
| FE-20-5 | **徽章数值** | P1 | 观察徽章 | 显示具体分数（如 85） |
| FE-20-6 | **hover 详情** | P1 | hover 健康度徽章 | 显示 breakdown tooltip（四维度分数） |
| FE-20-7 | **暗色模式适配** | P2 | 暗色模式下查看徽章 | 颜色在暗色背景下可辨识 |

### 边界条件

- strength=0, age=0 天, concepts=[] → score ≈ 40（strength 分=0, age 分=100, concepts 分=0, 推荐分=0 → 0*0.4 + 100*0.3 + 0*0.15 + 0*0.15 = 30）
- strength=10, age=0, concepts=["a","b","c","d","e"] → score ≈ 100
- createdAt 为空 → 使用 updatedAt 或当前时间
- 不存在的记忆 ID → 404

### 验收检查清单（AC）

- [ ] **AC-F20-1**：API 返回 0-100 评分 ⭐ P0
- [ ] **AC-F20-2**：breakdown 包含四维度 ⭐ P0
- [ ] **AC-F20-3**：高分记忆评分 >90 ⭐ P0
- [ ] **AC-F20-4**：低分记忆评分 <20 ⭐ P0
- [ ] **AC-F20-5**：颜色标记正确（绿/黄/红） ⭐ P0
- [ ] **AC-F20-6**：MemoryCard 显示健康度徽章
- [ ] **AC-F20-7**：列表接口可选附加 health_score

---

## F-21 自动去重

### 后端 API 测试（pytest）

新增文件：`backend/tests/test_dedup.py`

```python
# === 辅助函数测试 ===

def test_jaccard_similarity_identical():
    """concepts 完全相同 → Jaccard = 1.0"""
    ...

def test_jaccard_similarity_disjoint():
    """concepts 完全不同 → Jaccard = 0.0"""
    ...

def test_jaccard_similarity_partial():
    """部分相同 → 0 < Jaccard < 1"""
    ...

def test_jaccard_similarity_empty():
    """两个空集 → Jaccard = 0.0（避免除零）"""
    ...

def test_levenshtein_similarity_identical():
    """标题完全相同 → similarity = 1.0"""
    ...

def test_levenshtein_similarity_completely_different():
    """标题完全不同 → similarity < 0.3"""
    ...

def test_levenshtein_similarity_similar():
    """标题相似（如 typo） → similarity > 0.7"""
    ...

def test_levenshtein_similarity_empty():
    """空标题 → similarity = 0.0"""
    ...

# === GET /api/agentmemory/duplicates ===

def test_duplicates_returns_200(client):
    """GET /api/agentmemory/duplicates 返回 200"""
    ...

def test_duplicates_returns_pairs(client):
    """响应包含 pairs 数组，每对含 memory_a, memory_b, similarity"""
    ...

def test_duplicates_threshold_filter(client):
    """?threshold=0.9 只返回高相似度对"""
    ...

def test_duplicates_default_threshold(client):
    """默认 threshold=0.7"""
    ...

def test_duplicates_pair_fields(client):
    """每对包含 concepts_similarity, title_similarity, shared_concepts"""
    ...

def test_duplicates_no_self_comparison(client):
    """不存在 memory_a.id == memory_b.id 的对"""
    ...

def test_duplicates_no_duplicates_when_all_unique(client):
    """所有记忆完全不同时返回空 pairs"""
    ...

def test_duplicates_similar_concepts_detected(client):
    """concepts 高度重叠的记忆对被检测到"""
    ...

def test_duplicates_similar_title_detected(client):
    """标题相似的记忆对被检测到"""
    ...

# === POST /api/agentmemory/merge ===

def test_merge_returns_200(client):
    """POST /api/agentmemory/merge 返回 200"""
    ...

def test_merge_keeps_higher_strength(client):
    """合并后保留 strength 较高的记忆"""
    ...

def test_merge_concepts_merged(client):
    """合并后 concepts 为两者的并集（去重）"""
    ...

def test_merge_merged_memory_removed(client):
    """被合并的记忆从列表中移除"""
    ...

def test_merge_kept_memory_content_preserved(client):
    """保留的记忆 content 不变"""
    ...

def test_merge_invalid_ids(client):
    """无效 ID 返回 400 或 404"""
    ...

def test_merge_same_id(client):
    """keep_id == merge_id 返回 400"""
    ...
```

### 前端测试（描述性）

| # | 用例 | 优先级 | 步骤 | 预期 |
|---|------|--------|------|------|
| FE-21-1 | **去重面板渲染** | **P0** | 点击"去重检查" | DuplicatePanel 显示重复记忆对列表 |
| FE-21-2 | **重复对信息** | **P0** | 查看重复对 | 显示两条记忆的 title + 相似度 + 共享 concepts |
| FE-21-3 | **一键合并** | **P0** | 点击"合并"按钮 → 确认 | 合并成功，被合并记忆从列表消失 |
| FE-21-4 | **合并确认弹窗** | **P0** | 点击合并 | 二次确认弹窗，防止误操作 |
| FE-21-5 | **无重复状态** | P1 | 所有记忆不重复时检查 | 显示"未发现重复记忆" |
| FE-21-6 | **阈值调节** | P1 | 调整 threshold 滑块 | 列表实时更新 |
| FE-21-7 | **合并后刷新** | P1 | 合并后查看列表 | 主列表自动刷新，被合并记忆消失 |
| FE-21-8 | **加载状态** | P2 | 点击去重检查 | 显示 loading 指示器 |

### 边界条件

- 仅 1 条记忆 → 无重复对
- 所有记忆 concepts 为空 → 仅基于标题相似度检测
- threshold=1.0 → 仅返回完全相同的对
- threshold=0.0 → 返回所有对（可能为 n*(n-1)/2）
- 被合并记忆已被删除 → merge 返回 404
- 大量重复对（>100 对）→ 分页或限制显示

### 验收检查清单（AC）

- [ ] **AC-F21-1**：API 返回重复记忆对 ⭐ P0
- [ ] **AC-F21-2**：每对包含 similarity + concepts_similarity + title_similarity ⭐ P0
- [ ] **AC-F21-3**：threshold 参数正确过滤
- [ ] **AC-F21-4**：不依赖外部 embedding API ⭐ P0
- [ ] **AC-F21-5**：合并保留 strength 较高的记忆 ⭐ P0
- [ ] **AC-F21-6**：合并后 concepts 去重合并
- [ ] **AC-F21-7**：前端 DuplicatePanel 显示重复对 ⭐ P0
- [ ] **AC-F21-8**：一键合并后被合并记忆消失

---

## F-22 记忆衰减曲线

### 后端 API 测试（pytest）

新增文件：`backend/tests/test_decay.py`

```python
# === GET /api/agentmemory/{id}/decay ===

def test_decay_returns_200(client, sample_memory_id):
    """GET /api/agentmemory/{id}/decay 返回 200"""
    ...

def test_decay_returns_required_fields(client, sample_memory_id):
    """响应包含 current_strength, initial_strength, decay_rate, predicted_zero_date, decay_curve"""
    ...

def test_decay_rate_calculation(client, sample_memory_id):
    """decay_rate = initial_strength / 90"""
    ...

def test_decay_curve_data_points(client, sample_memory_id):
    """decay_curve 包含从创建日到预测归零日的数据点"""
    ...

def test_decay_curve_first_point_equals_initial(client, sample_memory_id):
    """decay_curve 第一个点的 strength = initial_strength"""
    ...

def test_decay_curve_monotonically_decreasing(client, sample_memory_id):
    """decay_curve 的 strength 单调递减"""
    ...

def test_decay_predicted_zero_date(client, sample_memory_id):
    """predicted_zero_date = created_date + (initial_strength / decay_rate) 天"""
    ...

def test_decay_current_strength_matches(client, sample_memory_id):
    """current_strength 与记忆的实际 strength 一致"""
    ...

def test_decay_nonexistent_id(client):
    """不存在的 ID 返回 404"""
    ...

def test_decay_strength_zero(client):
    """strength=0 时，predicted_zero_date 为今天（或已过期）"""
    ...

def test_decay_curve_max_points(client):
    """decay_curve 最多 365 个数据点"""
    ...
```

### 前端测试（描述性）

| # | 用例 | 优先级 | 步骤 | 预期 |
|---|------|--------|------|------|
| FE-22-1 | **衰减曲线渲染** | **P0** | 展开记忆详情 | MemoryDetail 显示折线图 |
| FE-22-2 | **曲线数据正确** | **P0** | 观察折线图 | 从 initial_strength 开始线性下降 |
| FE-22-3 | **当前位置标记** | **P0** | 观察折线图 | 当前 strength 位置有标记点 |
| FE-22-4 | **预测归零日期** | P1 | 查看详情 | 显示"N 天后 strength 降至 0" |
| FE-22-5 | **strength=0 状态** | P1 | 查看 strength=0 的记忆 | 显示"记忆已遗忘"提示 |
| FE-22-6 | **曲线响应式** | P2 | 缩小窗口 | 折线图自适应宽度 |
| FE-22-7 | **暗色模式适配** | P2 | 暗色模式下查看 | 折线图颜色适配暗色背景 |

### 边界条件

- strength=10, 创建于今天 → decay_rate ≈ 0.111, predicted ≈ 90 天后
- strength=1, 创建于今天 → decay_rate ≈ 0.011, predicted ≈ 90 天后
- strength=10, 创建于 100 天前 → predicted_zero_date 已过去，显示"已过期"
- createdAt 为空 → 使用 updatedAt 或当前时间
- 不存在的记忆 ID → 404

### 验收检查清单（AC）

- [ ] **AC-F22-1**：API 返回衰减数据 ⭐ P0
- [ ] **AC-F22-2**：decay_curve 数据点合理 ⭐ P0
- [ ] **AC-F22-3**：predicted_zero_date 计算正确 ⭐ P0
- [ ] **AC-F22-4**：前端折线图正确渲染 ⭐ P0
- [ ] **AC-F22-5**：当前位置有标记点
- [ ] **AC-F22-6**：strength=10 → predicted ≈ 90 天后
- [ ] **AC-F22-7**：strength=0 显示"已遗忘"提示

---

## 测试汇总

| 功能 | 后端用例数 | 前端用例数 | 边界条件数 | AC 数 |
|------|-----------|-----------|-----------|-------|
| F-18 记忆关联图谱 | 11 | 9 | 5 | 7 |
| F-19 智能推荐 | 10 | 6 | 5 | 7 |
| F-20 记忆健康度评分 | 13 | 7 | 4 | 7 |
| F-21 自动去重 | 22 | 8 | 6 | 8 |
| F-22 记忆衰减曲线 | 11 | 7 | 5 | 7 |
| **合计** | **67** | **37** | **25** | **36** |

### 新增测试文件清单

| 文件 | 用例数 | 功能 |
|------|--------|------|
| `backend/tests/test_graph.py` | 11 | F-18 图谱 API |
| `backend/tests/test_recommendation.py` | 10 | F-19 推荐 API |
| `backend/tests/test_health.py` | 13 | F-20 健康度 API |
| `backend/tests/test_dedup.py` | 22 | F-21 去重 + 合并 API |
| `backend/tests/test_decay.py` | 11 | F-22 衰减 API |

### 执行优先级

#### ⭐ P0 — 必须通过（上线阻塞）

| 用例 | 功能 | 说明 |
|------|------|------|
| test_graph_returns_nodes_and_edges | 图谱 API | 核心数据结构 |
| test_graph_edge_weight_equals_shared_concepts_count | 图谱 API | 核心算法正确性 |
| FE-18-1 | 图谱页面渲染 | 核心功能 |
| FE-18-2 | 节点拖拽 | 核心交互 |
| FE-18-3 | 点击高亮 | 核心交互 |
| test_recommendations_ordered_by_score_desc | 推荐 API | 排序逻辑 |
| test_recommendations_excludes_self | 推荐 API | 数据正确性 |
| FE-19-1 | 相关记忆显示 | 核心功能 |
| FE-19-3 | 点击跳转 | 核心交互 |
| test_health_score_range | 健康度 API | 数据范围 |
| test_health_color_green | 健康度 API | 颜色逻辑 |
| test_health_color_red | 健康度 API | 颜色逻辑 |
| FE-20-1 | 健康度徽章显示 | 核心功能 |
| FE-20-2 | 绿色徽章 | 颜色正确性 |
| FE-20-4 | 红色徽章 | 颜色正确性 |
| test_merge_keeps_higher_strength | 合并 API | 核心逻辑 |
| test_merge_concepts_merged | 合并 API | 数据完整性 |
| FE-21-1 | 去重面板渲染 | 核心功能 |
| FE-21-3 | 一键合并 | 核心功能 |
| test_decay_rate_calculation | 衰减 API | 核心算法 |
| test_decay_predicted_zero_date | 衰减 API | 预测正确性 |
| FE-22-1 | 衰减曲线渲染 | 核心功能 |
| FE-22-2 | 曲线数据正确 | 数据正确性 |

#### 🟡 P1 — 应该通过（影响用户体验）

| 用例 | 功能 | 说明 |
|------|------|------|
| FE-18-4 | 缩放交互 | 交互完整性 |
| FE-18-5 | 空数据状态 | 用户体验 |
| test_recommendations_limit_param | 推荐 API | 参数功能 |
| FE-19-4 | 无推荐状态 | 空状态处理 |
| FE-20-5 | 徽章数值 | 信息展示 |
| FE-20-6 | hover 详情 | 信息展示 |
| test_duplicates_threshold_filter | 去重 API | 参数功能 |
| FE-21-2 | 重复对信息 | 信息展示 |
| FE-21-4 | 合并确认弹窗 | 防误操作 |
| FE-21-5 | 无重复状态 | 空状态处理 |
| test_decay_curve_monotonically_decreasing | 衰减 API | 数据正确性 |
| FE-22-4 | 预测归零日期 | 信息展示 |
| FE-22-5 | strength=0 状态 | 边界状态 |
| test_health_breakdown_has_four_dimensions | 健康度 API | 数据完整性 |
| test_graph_only_edges_with_shared_concepts | 图谱 API | 数据正确性 |

#### 🟢 P2 — 最好通过（边界和优化）

| 用例 | 功能 | 说明 |
|------|------|------|
| test_graph_no_self_loops | 图谱 API | 数据健壮性 |
| test_graph_empty_memories | 图谱 API | 空数据边界 |
| FE-18-8 | 节点大小区分 | 视觉细节 |
| FE-18-9 | 边权重可视化 | 视觉细节 |
| test_jaccard_similarity_empty | 算法 | 空集边界 |
| test_levenshtein_similarity_empty | 算法 | 空字符串边界 |
| FE-19-6 | 推荐刷新 | 动态更新 |
| FE-20-7 | 暗色模式适配 | 视觉一致性 |
| FE-21-8 | 加载状态 | 交互细节 |
| FE-22-6 | 曲线响应式 | 响应式布局 |
| FE-22-7 | 暗色模式适配 | 视觉一致性 |
| test_merge_same_id | 合并 API | 输入校验 |
| test_decay_curve_max_points | 衰减 API | 性能边界 |

### 已有测试影响

现有 59 个测试用例（P0+P1+P2）**不修改**，P3 新增 67 个后端用例，预计总计 **126 个**后端测试。

> 注：F-20 健康度评分的 `include_health=true` 扩展了分页 API，需确认现有分页测试不受影响（默认不附加 health_score）。

---

## 评审附录（qa-worker）

> **评审日期**: 2026-05-29
> **评审结论**: ⚠️ 有条件通过 — 存在 12 个遗漏场景需补充

---

### 一、总体评价

测试计划结构清晰，67 后端 + 37 前端用例覆盖面广，AC 定义明确。边界条件和执行优先级划分合理。以下为逐功能评审发现的遗漏。

---

### 二、F-18 记忆关联图谱 — 遗漏 3 项

| # | 遗漏场景 | 严重度 | 说明 |
|---|---------|--------|------|
| G-01 | **孤立节点显式断言** | 🟡 P1 | 边界条件提到"所有 concepts 为空 → 只有节点无边"，但缺少**孤立节点**（部分记忆有 concepts 但与其他记忆无交集）的测试用例。应补充 `test_graph_isolated_nodes`：验证孤立节点仍出现在 nodes 中，edges 中无相关边 |
| G-02 | **全连通图 / 高密度图** | 🟡 P1 | 缺少所有记忆共享同一组 concepts 时的测试。应验证 n 条记忆全共享 → edges = n*(n-1)/2，max_weight 正确 |
| G-03 | **meta 字段数值正确性** | 🟡 P1 | `test_graph_meta_fields` 仅检查字段存在，未验证 node_count/edge_count/max_weight 与实际数据一致。应拆分为数值断言用例 |

### 三、F-19 智能推荐 — 遗漏 3 项

| # | 遗漏场景 | 严重度 | 说明 |
|---|---------|--------|------|
| R-01 | **所有记忆 concepts 相同** | 🟡 P1 | 缺少所有记忆 concepts 完全相同的场景。此时 Jaccard=1.0，score 仅由 strength 差异决定。应验证排序仍正确且不为全满分 |
| R-02 | **目标记忆已归档** | 🔴 P0 | 边界条件提到"目标记忆已归档 → 404"，但**没有对应的后端测试用例**。应补充 `test_recommendations_archived_target_returns_404` |
| R-03 | **候选记忆 concepts 为空** | 🟢 P2 | 测试了目标记忆 concepts 为空，但未测试候选记忆 concepts 为空（目标有 concepts，候选无）。应验证这些候选不产生推荐且不报错 |

### 四、F-20 记忆健康度评分 — 遗漏 3 项

| # | 遗漏场景 | 严重度 | 说明 |
|---|---------|--------|------|
| H-01 | **strength=0 的精确得分** | 🟡 P1 | 边界条件有 strength=0 场景但计算有误：注释写 `score ≈ 40`，实际 `0*0.4 + 100*0.3 + 0*0.15 + 0*0.15 = 30`。**测试预期值与注释不一致**，需修正并补充精确断言 |
| H-02 | **strength 边界值 10（上限）和 11（越界）** | 🟡 P1 | 缺少 strength 超出 0-10 范围的健壮性测试。应验证 strength=10 得满分、strength=11 不 crash（或返回错误） |
| H-03 | **createdAt 完全缺失** | 🟡 P1 | 边界条件提到 `createdAt 为空 → 使用 updatedAt 或当前时间`，但无对应测试用例。应补充 `test_health_created_at_null` |

### 五、F-21 自动去重 — 遗漏 2 项

| # | 遗漏场景 | 严重度 | 说明 |
|---|---------|--------|------|
| D-01 | **阈值边界值** | 🟡 P1 | 缺少 threshold 刚好等于/略高于/略低于某对相似度时的精确过滤测试。如 `similarity=0.7001` + `threshold=0.7` 应保留，`similarity=0.6999` + `threshold=0.7` 应过滤 |
| D-02 | **单字符标题的 Levenshtein** | 🟢 P2 | 未测试极短标题（如 "A" vs "B"，长度=1）时 Levenshtein 公式 `1 - dist / max_len` 的行为（max_len=1 时除零或结果异常） |

### 六、F-22 记忆衰减曲线 — 遗漏 1 项

| # | 遗漏场景 | 严重度 | 说明 |
|---|---------|--------|------|
| C-01 | **strength 已为 0 + 创建于很久前** | 🟡 P1 | `test_decay_strength_zero` 仅验证 predicted_zero_date，未验证 `decay_curve` 数据点行为（strength=0 时 curve 应全为 0 或返回空曲线）。同时缺 **负衰减** 场景：当 `days_since_created > initial_strength / decay_rate` 时，`strength(t)` 会为负数，需验证是否 clamp 到 0 |

---

### 七、跨功能遗漏

| # | 遗漏场景 | 严重度 | 说明 |
|---|---------|--------|------|
| X-01 | **F-20 推荐引用分（recommendation_score）** | 🟡 P1 | 健康度有 recommendation_score 维度（15%），但未测试该维度的计算逻辑（如"被多少条其他记忆推荐"的计数方式）。迭代计划提到"F-20 依赖 F-19 推荐逻辑"，测试计划中未体现此依赖的集成验证 |
| X-02 | **所有新 API 的 /api/docs Swagger 可见性** | 🟢 P2 | 迭代计划验收清单要求"所有新增 API 端点出现在 Swagger 文档中"，测试计划未覆盖此项 |

---

### 八、评审总结

| 类别 | 数量 |
|------|------|
| 🔴 P0 遗漏（阻塞上线） | 1 |
| 🟡 P1 遗漏（影响质量） | 8 |
| 🟢 P2 遗漏（建议补充） | 3 |
| **合计需补充** | **12** |

**建议**：补充 R-02（归档目标记忆 404）为 P0 阻塞项，其余 11 项在开发过程中逐步补充。修正 H-01 的预期值注释。
