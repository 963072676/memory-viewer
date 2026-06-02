# P22 迭代计划

> **日期**: 2026-05-31  
> **阶段**: P22  
> **目标**: 3-5个高价值功能（命令面板 + 批量操作 + 热力图 + 衰减曲线）

---

## 任务清单

| ID | 功能 | 类型 | 优先级 | 依赖 | 预估工时 |
|----|------|------|--------|------|----------|
| P22-T1 | F-35 命令面板 (⌘K) | frontend | P0 | 无 | 2h |
| P22-T2 | F-36 批量操作工具栏 | frontend+backend | P0 | F-35 | 2h |
| P22-T3 | F-37 记忆活动热力图 | frontend | P1 | 后端API已就绪 | 1.5h |
| P22-T4 | F-22 记忆衰减曲线 | frontend | P1 | 后端API已就绪 | 1.5h |
| P22-T5 | F-33 语义搜索 | backend+frontend | P2 | embedding服务 | 3h |

---

## 详细设计

### P22-T1: F-35 命令面板 (⌘K)

**后端改动**: 无（纯前端功能）

**前端改动**:
- 新增 `components/Layout/CommandPalette.vue`
- 全局快捷键 `⌘K` / `Ctrl+K` 触发
- 模糊搜索：导航项、最近记忆、操作命令
- 分区：Actions / Navigate / Recent Memories / Settings
- 使用 `fuse.js` 进行 fuzzy search

**验收标准**:
- AC-F35-1: ⌘K/Ctrl+K 在任意视图打开命令面板
- AC-F35-2: 输入文字进行模糊匹配过滤
- AC-F35-3: Enter 执行选中命令，Esc 关闭面板
- AC-F35-4: 最近记忆出现在结果中，点击跳转详情

---

### P22-T2: F-36 批量操作工具栏

**后端改动**: 扩展 `POST /api/agentmemory/bulk` 端点

**前端改动**:
- 记忆卡片添加复选框（批量模式激活时显示）
- 底部浮动操作栏：选中数量 + 操作按钮（Delete/Export/Tag/Archive）
- `Shift+Click` 范围选择，`Cmd+A` 全选
- 进度指示（>10条操作时）

**验收标准**:
- AC-F36-1: 点击 "批量操作" 后出现复选框
- AC-F36-2: 可选择多条记忆并批量删除（需确认）
- AC-F36-3: 批量导出：下载选中记忆为 JSON
- AC-F36-4: 批量操作记录在审计日志

---

### P22-T3: F-37 记忆活动热力图

**后端改动**: 无（`/api/metrics/heatmap` 已实现）

**前端改动**:
- 新增 `components/Layout/ActivityHeatmap.vue`
- GitHub 风格网格：52列×7行
- 颜色刻度：5级（浅→深）
- 悬停提示：日期+数量
- 切换：Created / Accessed / Modified
- 集成到 `DashboardView.vue`

**验收标准**:
- AC-F37-1: 过去365天热力图正确渲染
- AC-F37-2: 悬停显示日期和数量提示
- AC-F37-3: 点击某天跳转到该日期过滤的记忆列表
- AC-F37-4: 暗色模式兼容

---

### P22-T4: F-22 记忆衰减曲线

**后端改动**: 无（`/api/agentmemory/{id}/decay` 已实现）

**前端改动**:
- 新增 `components/Layout/DecayCurve.vue`
- 折线图展示 strength 随时间的衰减趋势
- 预测即将"遗忘"的记忆（低 strength + 高 age）
- 集成到记忆详情页或 Dashboard

**验收标准**:
- AC-F22-1: 每条记忆显示衰减曲线图表
- AC-F22-2: 预测模型展示未来衰减趋势
- AC-F22-3: 低分记忆高亮标记

---

### P22-T5: F-33 语义搜索

**后端改动**:
- 新增 `services/embedding.py`（`sentence-transformers`）
- 新端点：`GET /api/search/semantic?q=...&limit=10`
- 优雅降级：嵌入服务不可用时回退关键词搜索

**前端改动**:
- 搜索栏增加 "keyword ↔ semantic" 切换
- 结果显示相似度百分比徽章

**验收标准**:
- AC-F33-1: 搜索 "security" 能找到 "vulnerability" 相关记忆
- AC-F33-2: 每个结果显示相似度百分比 (0-100%)
- AC-F33-3: 搜索栏支持关键词/语义搜索切换
- AC-F33-4: 嵌入服务不可用时优雅降级

---

## 验证要求

每完成一个任务后必须运行：
```bash
cd /opt/data/memory-viewer/v2
/opt/hermes/.venv/bin/python3 -m pytest backend/tests/ -q --tb=short 2>&1 | tail -3
cd frontend && npx vue-tsc --noEmit 2>&1 | grep "error TS" | wc -l
```

errors > 0 时必须修复，不能跳过。

---

## 预期成果

- 完成 5 个功能开发
- pytest 无错误，vue-tsc 无错误
- 3 个 quick wins（F-35/F-36/F-37/F-22 前后端联调）