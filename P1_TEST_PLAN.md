# Memory Viewer v2 — P1 测试计划

> **版本**: 1.0  
> **日期**: 2026-05-29  
> **基于**: P1_ITERATION_PLAN.md  
> **现有测试**: 20 个用例（backend/tests/），全部通过

---

## 目录

1. [F-07 高级搜索面板](#f-07-高级搜索面板)
2. [F-08 记忆编辑](#f-08-记忆编辑)
3. [F-09 记忆删除](#f-09-记忆删除)
4. [F-10 统计仪表盘](#f-10-统计仪表盘)
5. [F-11 缓存自动刷新](#f-11-缓存自动刷新)
6. [测试汇总](#测试汇总)

---

## F-07 高级搜索面板

### 后端 API 测试（pytest）

新增文件：`backend/tests/test_search_advanced.py`

```python
# === 纯过滤模式（无关键词） ===

def test_filter_by_type_only(client):
    """无 q 参数，仅按 type 过滤，应返回对应类型的记忆"""
    ...

def test_filter_by_type_multiple(client):
    """type=pattern,fact 多选过滤，返回两种类型的记忆"""
    ...

def test_filter_by_date_range(client):
    """date_from + date_to 过滤，返回时间范围内的记忆"""
    ...

def test_filter_by_strength_range(client):
    """strength_min=5, strength_max=10 过滤"""
    ...

def test_filter_by_source_agentmemory(client):
    """source=agentmemory，仅返回 agentmemory 数据"""
    ...

def test_filter_by_source_hermes(client):
    """source=hermes，仅返回 hermes-memory 数据"""
    ...

def test_filter_combined_type_and_strength(client):
    """组合过滤：type + strength，交集结果正确"""
    ...

def test_filter_all_params_combined(client):
    """全部过滤参数组合使用，结果为各条件交集"""
    ...

def test_filter_empty_result(client):
    """过滤条件导致无匹配，返回空列表，status 200"""
    ...

def test_filter_invalid_date_format(client):
    """date_from 格式错误，返回 422"""
    ...

def test_filter_invalid_strength_range(client):
    """strength_min > strength_max，返回 422 或空结果"""
    ...
```

### 前端测试（描述性）

| # | 用例 | 步骤 | 预期 |
|---|------|------|------|
| FE-07-1 | FilterPanel 展开/收起 | 点击筛选按钮 | 面板平滑展开，再点收起 |
| FE-07-2 | 类型多选过滤 | 勾选 pattern + fact | 结果仅含两种类型 |
| FE-07-3 | 时间范围过滤 | 选择起止日期 | 结果仅含该时间段记忆 |
| FE-07-4 | Strength 滑块 | 拖动到 [5, 10] | 结果仅含 strength 5-10 |
| FE-07-5 | 数据源切换 | 选择 hermes | 仅显示 hermes 记忆 |
| FE-07-6 | URL 参数同步 | 设置过滤后刷新页面 | 过滤状态保留 |
| FE-07-7 | 无关键词纯过滤 | 不输入搜索词，仅设置过滤条件 | 正常返回结果 |

### 边界条件

- 空搜索 + 所有过滤器都为空 → 返回全部数据
- 同时应用 4 种过滤器 → 结果为交集
- date_from > date_to → 应提示错误或返回空
- strength_min = strength_max → 精确匹配该值
- 过滤参数通过 URL 超长参数串 → 无异常

### 验收检查清单（AC）

- [ ] **AC-F07-1**：面板显示 4 类过滤器，布局清晰
- [ ] **AC-F07-2**：类型多选过滤结果正确
- [ ] **AC-F07-3**：时间范围过滤结果正确
- [ ] **AC-F07-4**：strength 滑块过滤结果正确
- [ ] **AC-F07-5**：数据源切换过滤结果正确
- [ ] **AC-F07-6**：URL query params 保留过滤状态
- [ ] **AC-F07-7**：纯过滤模式正常工作

---

## F-08 记忆编辑

### 后端 API 测试（pytest）

新增文件：`backend/tests/test_agentmemory_update.py`

```python
# === PUT /api/agentmemory/{memory_id} ===

def test_update_content(client, sample_memory_id):
    """修改 content，返回更新后的完整对象，content 已变更"""
    ...

def test_update_strength(client, sample_memory_id):
    """修改 strength 5→8，返回新值"""
    ...

def test_update_concepts(client, sample_memory_id):
    """修改 concepts 列表，返回新列表"""
    ...

def test_update_multiple_fields(client, sample_memory_id):
    """同时修改 content + strength + concepts"""
    ...

def test_update_no_fields_idempotent(client, sample_memory_id):
    """空 body 或仅传未变更字段，数据不变（幂等）"""
    ...

def test_update_nonexistent_id(client):
    """PUT 不存在的 ID，返回 404"""
    ...

def test_update_invalid_strength(client, sample_memory_id):
    """strength 超出范围（如 -1 或 11），返回 422"""
    ...

def test_update_empty_content(client, sample_memory_id):
    """content 为空字符串，返回 422"""
    ...

def test_update_returns_full_object(client, sample_memory_id):
    """响应包含完整的记忆对象（id, title, content, type, concepts, strength, ...）"""
    ...

def test_update_readonly_fields_ignored(client, sample_memory_id):
    """尝试修改 title 或 type，字段不变（忽略或报错）"""
    ...
```

### 前端测试（描述性）

| # | 用例 | 步骤 | 预期 |
|---|------|------|------|
| FE-08-1 | 打开编辑弹窗 | 点击卡片编辑按钮 | Modal 弹出，表单预填当前值 |
| FE-08-2 | 修改 content | 编辑文本 → 保存 | 卡片显示新内容 |
| FE-08-3 | 修改 strength | 滑块拖到 8 → 保存 | 卡片显示新 strength |
| FE-08-4 | Concepts 标签增删 | 输入标签回车 → 点×删除 | 标签正确增删 |
| FE-08-5 | 幂等提交 | 不修改直接保存 | 数据不变，Toast 成功 |
| FE-08-6 | 网络错误处理 | 断网后保存 | 显示错误提示，表单数据保留 |
| FE-08-7 | 编辑后列表刷新 | 保存成功 | 列表自动刷新，卡片更新 |

### 边界条件

- content 为超长文本（>10000 字符）→ 截断或报错
- concepts 传入重复标签 → 自动去重
- concepts 传入空列表 → strength 正常更新
- 快速连续点击保存按钮 → 不重复提交
- 编辑过程中其他用户删除该记忆 → 保存时返回 404

### 验收检查清单（AC）

- [ ] **AC-F08-1**：编辑弹窗预填当前值
- [ ] **AC-F08-2**：修改 content 后列表更新
- [ ] **AC-F08-3**：修改 strength 后卡片更新
- [ ] **AC-F08-4**：concepts 标签支持增删
- [ ] **AC-F08-5**：不修改直接提交，数据不变
- [ ] **AC-F08-6**：编辑失败显示错误提示
- [ ] **AC-F08-7**：PUT API 返回完整记忆对象

---

## F-09 记忆删除

### 后端 API 测试（pytest）

新增文件：`backend/tests/test_agentmemory_delete.py`

```python
# === DELETE /api/agentmemory/{memory_id} ===

def test_delete_single_memory(client, sample_memory_id):
    """删除单条记忆，返回 { success: true, deleted_id }"""
    ...

def test_delete_returns_correct_id(client, sample_memory_id):
    """返回的 deleted_id 与请求 ID 一致"""
    ...

def test_delete_nonexistent_id(client):
    """删除不存在的 ID，返回 404"""
    ...

def test_delete_after_delete_gone(client, sample_memory_id):
    """删除后 GET 该 ID，返回 404"""
    ...

def test_delete_writes_audit_log(client, sample_memory_id):
    """删除后 cache/audit.json 包含该记录（memory_id, title, deleted_at）"""
    ...

# === DELETE /api/agentmemory/batch ===

def test_batch_delete_multiple(client, sample_memory_ids):
    """批量删除 3 条，返回 { success: true, deleted_ids: [...] }"""
    ...

def test_batch_delete_partial_invalid(client, sample_memory_ids):
    """批量删除含不存在 ID，返回部分成功或 404 列表"""
    ...

def test_batch_delete_empty_list(client):
    """传入空列表，返回 400 或 422"""
    ...

def test_batch_delete_writes_audit_log(client, sample_memory_ids):
    """批量删除后审计日志包含每条记录"""
    ...

def test_delete_idempotent(client, sample_memory_id):
    """同一条记忆删除两次，第二次返回 404"""
    ...
```

### 前端测试（描述性）

| # | 用例 | 步骤 | 预期 |
|---|------|------|------|
| FE-09-1 | 单条删除确认 | 点击删除 → 确认 | 记忆消失，Toast "已删除" |
| FE-09-2 | 取消删除 | 点击删除 → 取消 | 记忆不受影响 |
| FE-09-3 | 确认框显示标题 | 点击删除 | 对话框显示记忆标题 |
| FE-09-4 | 批量选择删除 | 勾选 3 条 → 批量删除 → 确认 | 3 条全部移除 |
| FE-09-5 | 删除后列表刷新 | 删除成功 | 列表自动刷新 |

### 边界条件

- 删除最后一条记忆 → 列表显示空状态
- 批量删除全选 → 全部移除，显示空状态
- 网络错误时删除 → 显示错误提示，记忆保留
- 快速连续点击删除 → 不重复触发

### 验收检查清单（AC）

- [ ] **AC-F09-1**：确认对话框显示记忆标题
- [ ] **AC-F09-2**：确认后记忆消失 + Toast
- [ ] **AC-F09-3**：取消删除不影响记忆
- [ ] **AC-F09-4**：批量删除正常工作
- [ ] **AC-F09-5**：审计日志记录正确
- [ ] **AC-F09-6**：DELETE API 返回 `{ success, deleted_id }`
- [ ] **AC-F09-7**：删除不存在 ID 返回 404

---

## F-10 统计仪表盘

### 后端 API 测试（pytest）

新增文件：`backend/tests/test_stats.py`

```python
# === GET /api/stats ===

def test_stats_returns_200(client):
    """GET /api/stats 返回 200"""
    ...

def test_stats_has_type_distribution(client):
    """响应包含 by_type 字段，为 dict（类型→数量）"""
    ...

def test_stats_has_time_distribution(client):
    """响应包含 by_time 字段，按月/周聚合"""
    ...

def test_stats_has_profile_distribution(client):
    """响应包含 by_profile 字段"""
    ...

def test_stats_has_strength_distribution(client):
    """响应包含 by_strength 字段，分桶统计"""
    ...

def test_stats_type_counts_match_total(client):
    """by_type 各项之和 = 总记忆数"""
    ...

def test_stats_strength_buckets_cover_0_to_10(client):
    """by_strength 覆盖 0-10 范围"""
    ...

def test_stats_empty_data(client):
    """无记忆数据时，各字段返回 0 或空，不报错"""
    ...

def test_stats_response_time(client):
    """~100 条数据下响应时间 < 500ms"""
    ...

def test_stats_appears_in_swagger(client):
    """/api/docs 中包含 /api/stats 端点"""
    ...
```

### 前端测试（描述性）

| # | 用例 | 步骤 | 预期 |
|---|------|------|------|
| FE-10-1 | 导航到仪表盘 | 点击导航栏 Dashboard | 进入 /dashboard 页面 |
| FE-10-2 | 饼图渲染 | 页面加载 | 显示各类型占比饼图 |
| FE-10-3 | 折线图渲染 | 页面加载 | 显示记忆创建趋势 |
| FE-10-4 | 柱状图渲染 | 页面加载 | 显示各 profile 条数 |
| FE-10-5 | 直方图渲染 | 页面加载 | 显示 strength 分布 |
| FE-10-6 | 空数据状态 | 无记忆数据 | 显示友好空状态提示 |
| FE-10-7 | 图表数据一致 | 对比图表与列表数据 | 数值一致 |

### 边界条件

- 数据量为 0 → 图表区域显示"暂无数据"
- 某类型记忆为 0 → 饼图中该类型不显示或显示 0
- strength 分布极端偏斜（全为 0）→ 直方图仍正确渲染
- API 加载中 → 显示 loading 状态

### 验收检查清单（AC）

- [ ] **AC-F10-1**：/dashboard 页面 4 个图表正确渲染
- [ ] **AC-F10-2**：饼图显示各类型占比
- [ ] **AC-F10-3**：折线图显示创建趋势
- [ ] **AC-F10-4**：柱状图显示各 profile 条数
- [ ] **AC-F10-5**：直方图显示 strength 分布
- [ ] **AC-F10-6**：空数据友好提示
- [ ] **AC-F10-7**：响应时间 < 500ms

---

## F-11 缓存自动刷新

### 后端 API 测试（pytest）

新增文件：`backend/tests/test_cache_refresh.py`

```python
# === 定时任务 ===

def test_scheduler_starts_on_app_startup(app):
    """应用启动后 scheduler 正确初始化"""
    ...

def test_scheduler_uses_config_interval(app):
    """CACHE_REFRESH_INTERVAL 环境变量生效"""
    ...

def test_scheduler_default_interval_30min(app):
    """未设置环境变量时默认 30 分钟"""
    ...

# === /api/health 增强 ===

def test_health_has_last_refresh_at(client):
    """/api/health 响应包含 last_refresh_at 字段（ISO 格式）"""
    ...

def test_health_has_next_refresh_at(client):
    """/api/health 响应包含 next_refresh_at 字段"""
    ...

def test_health_last_refresh_at_valid_iso(client):
    """last_refresh_at 为合法 ISO 8601 时间戳"""
    ...

def test_health_next_refresh_at_after_last(client):
    """next_refresh_at > last_refresh_at"""
    ...

# === 刷新逻辑 ===

def test_refresh_updates_cache(cache_dir):
    """执行刷新后缓存文件更新"""
    ...

def test_refresh_failure_does_not_crash(app):
    """刷新失败（如 MCP 不可用）时服务继续运行"""
    ...

def test_refresh_does_not_interrupt_api(client):
    """刷新过程中 API 请求正常响应"""
    ...
```

### 前端测试

P-11 无独立前端页面，前端仅读取 `/api/health` 的 `last_refresh_at` 字段显示在状态栏（如有）。

| # | 用例 | 步骤 | 预期 |
|---|------|------|------|
| FE-11-1 | Health 显示刷新时间 | 查看页面状态栏 | 显示上次刷新时间 |

### 边界条件

- CACHE_REFRESH_INTERVAL 设为 0 或负数 → 使用默认值 30
- 缓存文件被外部删除 → 刷新时重建
- MCP 服务不可达 → 刷新失败但不崩溃，记录错误日志
- 快速连续重启 → 不产生多个 scheduler 实例

### 验收检查清单（AC）

- [ ] **AC-F11-1**：启动日志显示 "scheduler started"
- [ ] **AC-F11-2**：/api/health 包含 last_refresh_at
- [ ] **AC-F11-3**：CACHE_REFRESH_INTERVAL 环境变量生效
- [ ] **AC-F11-4**：刷新过程中 API 不中断
- [ ] **AC-F11-5**：刷新失败记录错误日志，服务可用

---

## 测试汇总

| 功能 | 后端用例数 | 前端用例数 | 边界条件数 | AC 数 |
|------|-----------|-----------|-----------|-------|
| F-07 高级搜索 | 11 | 7 | 5 | 7 |
| F-08 记忆编辑 | 10 | 7 | 5 | 7 |
| F-09 记忆删除 | 10 | 5 | 4 | 7 |
| F-10 统计仪表盘 | 10 | 7 | 4 | 7 |
| F-11 缓存刷新 | 10 | 1 | 4 | 5 |
| **合计** | **51** | **27** | **22** | **33** |

### 新增测试文件清单

| 文件 | 用例数 | 功能 |
|------|--------|------|
| `backend/tests/test_search_advanced.py` | 11 | F-07 高级搜索过滤 |
| `backend/tests/test_agentmemory_update.py` | 10 | F-08 PUT 编辑 |
| `backend/tests/test_agentmemory_delete.py` | 10 | F-09 DELETE 删除 |
| `backend/tests/test_stats.py` | 10 | F-10 统计 API |
| `backend/tests/test_cache_refresh.py` | 10 | F-11 缓存刷新 |

### 执行优先级

1. **P0（必须通过）**：F-08 PUT、F-09 DELETE 的核心 CRUD 测试
2. **P1（应该通过）**：F-10 stats API、F-11 scheduler、F-07 过滤
3. **P2（最好通过）**：边界条件、性能测试、前端交互测试

### 已有测试影响

现有 20 个测试用例**不修改**，P1 新增 51 个后端用例，预计总计 71 个。
